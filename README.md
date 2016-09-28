# electron-gtk3

A modern GTK3 build script for [Electron](https://github.com/electron/electron) and [Libchromiumcontent](https://github.com/electron/libchromiumcontent).

---
Note:
Chromium has stopped supporting GYP in their latest versions. Ill be waiting for electron to modify their build script to use GN before editing this script
---


## Quickstart
```shell
$ git clone https://github.com/nikolowry/electron-gtk3
$ cd electron-gtk3
$ ./build
```

## Building
Intended only for Linux 32-bit/64-bit machines with GTK3 installed. ARM users should still use the official [Electron](https://github.com/electron/electron) repo.

##### Valid Flags
Manually specify machine arch-type with `-t` or `--target_arch`
- 32-bit: `i686` | `ia32`
- 64-bit: `amd64` | `x64` | `x86_64`

Manually specify what components to build with `-c` or `--components`
- Build Release and Debug: `all`
- Build Release (default): `static`

NOTE - The build script will try to auto-detect your machine type if no arch-type flag is passed

## Gotchas
##### Wayland
Chromium build with GTK3 will not invoke XWayland while in a Wayland session. You can track the [issue](https://bugs.chromium.org/p/chromium/issues/detail?id=615164) on the Chromium bug tracker. An example command to launch Electron in Wayland would look like so (using this repo's built electron path as an example):

`GDK_BACKEND=x11 dist/electron`


##### HiDPI
There is a known issue with Chromium-GTK3 and hidpi machines. Chromium has the DPI for libgtkui hardcoded at 96.  When using `electron-gtk3` in builds for an app you should inform hidpi users to modify the `.desktop` file or create an alias like so (using this repo's built electron path as an example):

`GDK_SCALE=2 GDK_DPI_SCALE=.5 dist/electron --force-device-scale-factor=1.5`

## Status
Building on Arch Linux, other distros' statuses are unknown.  Please open an issue if you encounter any errors.

## Screenshots
![screenshot from 2016-05-20 15-54-44](https://cloud.githubusercontent.com/assets/597310/15440824/8a358f5a-1ea5-11e6-9cda-b1f520510bc2.png)
![screenshot from 2016-05-20 15-52-32](https://cloud.githubusercontent.com/assets/597310/15440823/8a345b1c-1ea5-11e6-9dcb-a8c9f4431cd8.png)
