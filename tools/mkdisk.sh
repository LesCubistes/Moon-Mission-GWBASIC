#!/bin/bash
# Build the two Moon Mission disks (360K each). Needs mtools and pcbasic (pip install pcbasic).
# Put your own DISK01.IMG (MS-DOS 3.30 disk 1) and GWBASIC.EXE in dos/ (not committed).
#   START.IMG    bootable: DOS + GW-BASIC + title, high scores, mission menu (MOON.BAS).
#                For the real floppy in drive A:. LANDHS.DAT (high scores) is saved here.
#   LANDING.IMG  the Lunar Landing level (LANDER.BAS + its art), for drive B:.
#                No GW-BASIC on it: the START disk runs it, which leaves room for the level.
# usage: tools/mkdisk.sh [START.IMG] [LANDING.IMG]
set -e
R=$(cd "$(dirname "$0")/.." && pwd)
START=${1:-$R/disks/START.IMG}
LAND=${2:-$R/disks/LANDING.IMG}
mkdir -p "$(dirname "$START")" "$(dirname "$LAND")" "$R/build/tok"
# tokenized programs load ~3x faster on an 8088
for f in MOON LANDER; do
  long=$(tr -d '\r' < "$R/src/$f.BAS" | awk 'length($0) > 250 {print "  line " $1 " is " length($0) " chars"}')
  [ -n "$long" ] && { echo "GW-BASIC lines must stay under 255 characters ($f.BAS):"; echo "$long"; exit 1; }
  pcbasic --convert=b "$R/src/$f.BAS" "$R/build/tok/$f.BAS" >/dev/null 2>&1
done
T=$(mktemp -d)
printf '@ECHO OFF\r\nGWBASIC MOON\r\n' > "$T/GO.BAT"
# The START disk is a game disk: it boots straight into Moon Mission.
# Laser XT fast mode: SPEED.COM from your own Laser DOS disk (dos/SPEED.COM, not committed), run only
# when LASERCHK finds the Laser XT's Central Point BIOS (SPEED writes to port 1F0h, the hard disk
# controller on other PCs).
EXTRA=""
printf '@ECHO OFF\r\n' > "$T/AUTOEXEC.BAT"
if [ -f "$R/dos/SPEED.COM" ]; then
  EXTRA="$R/dos/SPEED.COM $R/assets/LASERCHK.COM"
  printf 'LASERCHK\r\nIF ERRORLEVEL 1 SPEED F > NUL\r\n' >> "$T/AUTOEXEC.BAT"
fi
printf 'GWBASIC MOON\r\n' >> "$T/AUTOEXEC.BAT"

# ---------- START disk: DOS boot files only, plus the game ----------
cp "$R/dos/DISK01.IMG" "$START"
mattrib -i "$START" -r -h -s ::/*.* 2>/dev/null || true
for f in $(mdir -i "$START" -b ::/ | sed 's#^::/##'); do
  case "$f" in IO.SYS|MSDOS.SYS|COMMAND.COM) ;; *) mdel -i "$START" "::/$f" ;; esac
done
mattrib -i "$START" +r +h +s ::/IO.SYS ::/MSDOS.SYS
mcopy -o -i "$START" "$R/dos/GWBASIC.EXE" "$R/build/tok/MOON.BAS" "$R/assets/MOONBG.PIC" \
      "$R/assets/EARTH.SPR" "$R/assets/TITLE.SPR" "$R/assets/CREDIT.SPR" "$R/assets/ROLL.BIN" "$R/assets/ROLL.DAT" "$T/GO.BAT" "$T/AUTOEXEC.BAT" $EXTRA ::/
mlabel -i "$START" ::MOONSTART
echo "START:   $(mdir -i "$START" ::/ | grep free | xargs)"

# ---------- LUNAR LANDING disk ----------
rm -f "$LAND"
dd if=/dev/zero of="$LAND" bs=1024 count=360 2>/dev/null
mformat -i "$LAND" -f 360 -v LUNARLAND ::
LEVEL=$(ls "$R"/assets/*.PIC "$R"/assets/*.SPR "$R"/assets/*.MAP "$R"/assets/*.DAT "$R"/assets/*.RLE "$R"/assets/CKPIT.BIN | grep -v -E '/(MOONBG\.PIC|EARTH\.SPR|TITLE\.SPR|CREDIT\.SPR|ROLL\.DAT|OFL\.SPR|OLM\.SPR|OLMK\.SPR|WRECK\.SPR|CRATER\.SPR)$')
mcopy -o -i "$LAND" "$R/build/tok/LANDER.BAS" $LEVEL ::/
echo "LANDING: $(mdir -i "$LAND" ::/ | grep free | xargs)"
rm -rf "$T"
