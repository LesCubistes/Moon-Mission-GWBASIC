#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
machine=${1:-cga}
case "$machine" in cga|tandy) ;; *) echo 'Use cga or tandy' >&2; exit 2;; esac
start="$root/build/desktop/start"
landing="$root/build/desktop/landing"
mkdir -p "$start" "$landing"
cp "$root/src/MOON.BAS" "$root/assets/MOONBG.PIC" "$root/assets/EARTH.SPR" "$root/assets/TITLE.SPR" "$root/assets/CREDIT.SPR" "$start/"
cp "$root/src/LANDER.BAS" "$root"/assets/* "$landing/"
if [[ -x "$root/build/venv/bin/pcbasic" ]]; then
    "$root/build/venv/bin/pcbasic" --convert=b "$root/src/MOON.BAS" "$start/MOON.BAS"
    "$root/build/venv/bin/pcbasic" --convert=b "$root/src/LANDER.BAS" "$landing/LANDER.BAS"
fi
if [[ -f "$root/dos/GWBASIC.EXE" ]]; then
    cp "$root/dos/GWBASIC.EXE" "$start/"
fi
config="$root/build/desktop/$machine.conf"
cat > "$config" <<CFG
[sdl]
fullscreen = true
[dosbox]
machine = $machine
memsize = 1
[cpu]
core = normal
cputype = 8086
cpu_cycles = 300
[sblaster]
sbtype = none
[autoexec]
mount a "$start" -t floppy
mount b "$landing" -t floppy
a:
CFG
if [[ -f "$start/GWBASIC.EXE" ]]; then
    printf 'GWBASIC MOON\nexit\n' >> "$config"
else
    cat >> "$config" <<CFG
@echo off
cls
echo MOON MISSION - desktop workspace ready
echo.
echo Missing GWBASIC.EXE from your original disks.
echo Copy it into the repository dos folder, then relaunch.
echo.
echo A: Start disk   B: Landing mission   Machine: $machine
echo Type EXIT to close.
CFG
fi
exec env -u LD_PRELOAD flatpak run --filesystem="$root" io.github.dosbox-staging --noprimaryconf --conf "$config"
