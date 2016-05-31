#!/usr/bin/env python

import argparse
import contextlib
import errno
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib2

from lib.config import get_output_dir


SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
VENDOR_DIR = os.path.join(SOURCE_ROOT, 'vendor')
SRC_DIR = os.path.join(VENDOR_DIR, 'chromium', 'src')
CHROMIUMCONTENT_SOURCE_DIR = os.path.join(SOURCE_ROOT, 'chromiumcontent')
CHROMIUMCONTENT_DESTINATION_DIR = os.path.join(SRC_DIR, 'chromiumcontent')
COMPONENTS = ['static_library', 'shared_library', 'ffmpeg']

TARBALL_REPO = 'zcbenz/chromium-source-tarball'
TARBALL_URL = 'https://github.com/{0}/releases/download/{1}/chromium-{1}.tar.xz'


def main():
  args = parse_args()

  version = chromium_version()
  if not is_source_tarball_updated(version):
    download_source_tarball(version)

  if args.sync:
    target_arch = args.target_arch
    return (apply_patches() or
            copy_chromiumcontent_files() or
            update_clang() or
            run_gyp(target_arch, args.defines))


def parse_args():
  parser = argparse.ArgumentParser(description='Update build configuration')
  parser.add_argument('-t', '--target_arch', default='x64', help='x64 or ia32')
  parser.add_argument('-s', '--sync', action='store_true')
  parser.add_argument('--defines', default='',
                      help='The definetions passed to gyp')
  return parser.parse_args()


def chromium_version():
  with open(os.path.join(SOURCE_ROOT, 'VERSION')) as f:
    return f.readline().strip()


def is_source_tarball_updated(version):
  version_file = os.path.join(SRC_DIR, '.version')
  existing_version = ''
  try:
    with open(version_file, 'r') as f:
      existing_version = f.readline().strip()
  except IOError as e:
    if e.errno != errno.ENOENT:
      raise
    return False
  return existing_version == version


def download_source_tarball(version):
  rm_rf(SRC_DIR)

  dir_name = 'chromium-{0}'.format(version)
  tar_name = dir_name + '.tar'
  xz_name = tar_name + '.xz'
  url = TARBALL_URL.format(TARBALL_REPO, version)
  with open(xz_name, 'wb+') as t:
    with contextlib.closing(urllib2.urlopen(url)) as u:
      while True:
        chunk = u.read(1024*1024)
        if not len(chunk):
            break
        sys.stderr.write('.')
        sys.stderr.flush()
        t.write(chunk)

  sys.stderr.write('\nExtracting...\n')
  sys.stderr.flush()

  rm_f(tar_name)
  tar_xf(xz_name)
  os.rename(dir_name, SRC_DIR)
  os.remove(xz_name)

  version_file = os.path.join(SRC_DIR, '.version')
  with open(version_file, 'w+') as f:
    f.write(version)


def install_sysroot():
  for arch in ('arm', 'amd64', 'i386'):
    install = os.path.join(SRC_DIR, 'build', 'linux', 'sysroot_scripts',
                           'install-sysroot.py')
    subprocess.check_call([sys.executable, install, '--arch', arch])


def tar_xf(filename):
  subprocess.call([xz(), '-dqk', filename])
  tar_name = filename[:-3]
  tar = tarfile.open(tar_name)
  tar.extractall()
  tar.close()
  os.remove(tar_name)


def gyp_env(target_arch, component, gyp_defines):
  env = os.environ.copy()

  if component == 'ffmpeg':
    gyp_defines += ' ffmpeg_branding=Chromium'
  else:
    gyp_defines += ' ffmpeg_branding=Chrome component={0}'.format(component)

  env['GYP_GENERATORS'] = 'ninja'

  if sys.platform in ['win32', 'cygwin']:
    # Do not let Chromium download their own toolchains.
    env['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
    # Use VS 2015.
    env['GYP_MSVS_VERSION'] = '2015'
    # Use Windows 10 SDK.
    env['WINDOWSSDKDIR'] = 'C:\\Program Files (x86)\\Windows Kits\\10'
  elif sys.platform == 'linux2' and target_arch in ('arm', 'ia32'):
    # ARM build requires cross compilation.
    env['GYP_CROSSCOMPILE'] = '1'

  # Whether to build for Mac App Store.
  if env.has_key('MAS_BUILD'):
    gyp_defines += ' mac_mas_build=1'
  else:
    gyp_defines += ' mac_mas_build=0'

  # Always build on 64-bit machine.
  gyp_defines += ' host_arch=x64'

  # Build 32-bit or 64-bit.
  gyp_defines += ' target_arch={0}'.format(target_arch)
  env['GYP_DEFINES'] = gyp_defines

  # Output directory.
  output_dir = 'output_dir={0}'.format(get_output_dir(target_arch, component))
  env['GYP_GENERATOR_FLAGS'] = output_dir

  return env


def copy_chromiumcontent_files():
  try:
    os.makedirs(CHROMIUMCONTENT_DESTINATION_DIR)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise
  for dirpath, dirnames, filenames in os.walk(CHROMIUMCONTENT_SOURCE_DIR):
    for dirname in dirnames:
      mkdir_p(os.path.join(dirpath, dirname))
    for filename in filenames:
      source = os.path.join(dirpath, filename)
      relative = os.path.relpath(source, start=CHROMIUMCONTENT_SOURCE_DIR)
      destination = os.path.join(CHROMIUMCONTENT_DESTINATION_DIR, relative)
      if is_newer(destination, source):
        continue
      shutil.copy2(source, destination)


def apply_patches():
  return subprocess.call([sys.executable,
                          os.path.join(SOURCE_ROOT, 'script', 'apply-patches')])


def update_clang():
  if sys.platform not in ['linux2', 'darwin']:
    return
  update = os.path.join(SRC_DIR, 'tools', 'clang', 'scripts', 'update.py')
  return subprocess.call([sys.executable, update])


def run_gyp(target_arch, defines):
  os.chdir(SRC_DIR)
  gyp = os.path.join('build', 'gyp_chromium')
  relative_dir = os.path.relpath(CHROMIUMCONTENT_DESTINATION_DIR, SRC_DIR)
  args = [sys.executable, gyp, '-Ichromiumcontent/chromiumcontent.gypi',
          os.path.join(relative_dir, 'chromiumcontent.gyp')]
  for component in COMPONENTS:
    subprocess.call(args, env=gyp_env(target_arch, component, defines))


def xz():
  if sys.platform in ['win32', 'cygwin']:
    return os.path.join(VENDOR_DIR, 'xz', 'win32', 'xz.exe')
  elif sys.platform == 'darwin':
    return os.path.join(VENDOR_DIR, 'xz', 'darwin', 'bin', 'xz')
  else:
    return 'xz'


def is_newer(destination, source):
  return os.path.exists(destination) and \
    os.path.getmtime(destination) > os.path.getmtime(source)


def rm_f(path):
  try:
    os.remove(path)
  except OSError as e:
    if e.errno != errno.ENOENT:
      raise


def rm_rf(path):
  try:
    shutil.rmtree(path)
  except OSError as e:
    if e.errno != errno.ENOENT:
      raise


def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise


if __name__ == '__main__':
  import sys
  sys.exit(main())
