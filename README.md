# electron-gtk3

A modern GTK3 build script for [Electron](https://github.com/electron/electron) and [Libchromiumcontent](https://github.com/electron/libchromiumcontent).

## Status
In development and not currently building.

## Building
Intended only for Linux 32-bit/64-bit machines with GTK3 installed. ARM users should still use the official [Electron](https://github.com/electron/electron) repo.

#### Valid Flags
Manually specify machine arch-type with `-t` or `--target_arch`
- 32-bit: `i686` | `ia32`
- 64-bit: `amd64` | `x64` | `x86_64`

```shell
$ git clone https://github.com/nikolowry/electron-gtk3 && cd electron-gtk3
$ ./build
```

NOTE - The build script will try to auto-detect your machine type if no arch-type flag is passed
