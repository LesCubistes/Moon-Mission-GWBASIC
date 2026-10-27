#!/usr/bin/env python3
"""Package the public release; never bundle DOS, BASIC or the Laser XT's SPEED.COM.

release/Moon-Mission-game.zip holds:
  README.TXT            the player's guide (tools/ci/README.TXT)
  FLOPPY/START.IMG      360K START data disk: the title, MAKEBOOT.BAT, GO.BAT, README.TXT
  FLOPPY/LANDING.IMG    360K LUNAR LANDING data disk
  MOON/                 every game file in one folder, for a hard disk or DOSBox
  source/, README.md    the BASIC sources and the developer notes
The START disk keeps room at the very start of the disk for the DOS system files, so
MAKEBOOT (SYS) can make it bootable even on DOS 3.x, which needs IO.SYS there.
"""
import hashlib
from pathlib import Path
import shutil
import subprocess
import zipfile

root = Path(__file__).resolve().parents[2]
ci = Path(__file__).resolve().parent
release = root / 'release'
stage = root / 'build/release'
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)
release.mkdir(exist_ok=True)
start = stage / 'START'
land = stage / 'LANDING'
start.mkdir()
land.mkdir()
for name, folder in [('MOON', start), ('LANDER', land)]:
    source = root / 'src' / f'{name}.BAS'
    for line in source.read_bytes().splitlines():
        if len(line) > 250:
            raise SystemExit(f'{source}: line exceeds 250 characters')
    subprocess.run(['pcbasic', '--convert=b', str(source), str(folder / f'{name}.BAS')], check=True)
START_ART = {'MOONBG.PIC', 'EARTH.SPR', 'TITLE.SPR', 'CREDIT.SPR', 'ROLL.BIN', 'ROLL.DAT'}
OBSOLETE = {'OFL.SPR', 'OLM.SPR', 'OLMK.SPR', 'WRECK.SPR', 'CRATER.SPR',   # same as tools/mkdisk.sh
            'LASERCHK.COM'}                                      # only for SPEED.COM, which isn't ours to share
for asset in (root / 'assets').iterdir():
    if asset.is_file() and asset.name not in OBSOLETE:
        shutil.copy2(asset, (start if asset.name in START_ART else land) / asset.name)
guide = (ci / 'README.TXT').read_text().replace('\r\n', '\n').replace('\n', '\r\n').encode()
for folder, command in [(start, 'MOON'), (land, 'LANDER')]:
    (folder / 'GO.BAT').write_bytes(f'@ECHO OFF\r\nGWBASIC {command}\r\n'.encode())
shutil.copy2(ci / 'MAKEBOOT.BAT', start / 'MAKEBOOT.BAT')
(start / 'README.TXT').write_bytes(guide)

(stage / 'FLOPPY').mkdir()
for label, folder, image in [('MOONSTART', start, 'START.IMG'), ('LUNARLAND', land, 'LANDING.IMG')]:
    path = stage / 'FLOPPY' / image
    with path.open('wb') as f:
        f.truncate(360 * 1024)
    subprocess.run(['mformat', '-i', str(path), '-f', '360', '::'], check=True)
    files = sorted(folder.iterdir())
    if folder is start:
        # Two placeholder files take the first two directory entries and the first 80K, then the
        # game files and the volume label go after them and the placeholders are deleted:
        # SYS finds both the entries and the space free.
        tmp = stage / 'reserve'
        tmp.mkdir()
        for n in ('IO.$$$', 'MSDOS.$$$'):
            (tmp / n).write_bytes(b'\0' * 40 * 1024)
            subprocess.run(['mcopy', '-i', str(path), str(tmp / n), '::/'], check=True)
        subprocess.run(['mcopy', '-i', str(path), *map(str, files), '::/'], check=True)
        subprocess.run(['mlabel', '-i', str(path), f'::{label}'], check=True)
        subprocess.run(['mdel', '-i', str(path), '::/IO.$$$', '::/MSDOS.$$$'], check=True)
        shutil.rmtree(tmp)
    else:
        subprocess.run(['mlabel', '-i', str(path), f'::{label}'], check=True)
        subprocess.run(['mcopy', '-i', str(path), *map(str, files), '::/'], check=True)
    listing = subprocess.run(['mdir', '-i', str(path), '::/'], capture_output=True, text=True).stdout
    print(image, ' '.join(l.strip() for l in listing.splitlines() if 'free' in l))

one = stage / 'MOON'                                     # the one-folder install
one.mkdir()
for folder in (land, start):                             # START's GO.BAT wins
    for f in folder.iterdir():
        shutil.copy2(f, one / f.name)
(one / 'MAKEBOOT.BAT').unlink()
shutil.rmtree(start)
shutil.rmtree(land)
(stage / 'README.TXT').write_bytes(guide)
shutil.copytree(root / 'src', stage / 'source')
shutil.copy2(root / 'README.md', stage / 'README.md')
archive = release / 'Moon-Mission-game.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(stage.rglob('*')):
        if path.is_file():
            z.write(path, path.relative_to(stage))
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(release / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
print(f'Created {archive}: {digest}')
