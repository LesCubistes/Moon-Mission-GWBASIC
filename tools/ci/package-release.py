#!/usr/bin/env python3
"""Package tokenized game-only disks; never bundle DOS or BASIC fixtures."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import zipfile

root = Path(__file__).resolve().parents[2]
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
for asset in (root / 'assets').iterdir():
    if asset.is_file():
        folder = start if asset.name in {'MOONBG.PIC', 'EARTH.SPR', 'TITLE.SPR'} else land
        # Same obsolete art exclusions as the original floppy builder.
        if asset.name not in {'OFL.SPR', 'OLM.SPR', 'OLMK.SPR', 'WRECK.SPR', 'CRATER.SPR'}:
            shutil.copy2(asset, folder / asset.name)
for label, folder, command in [('START', start, 'MOON'), ('LANDING', land, 'LANDER')]:
    (folder / 'GO.BAT').write_bytes(f'@ECHO OFF\r\nGWBASIC {command}\r\n'.encode())
    image = stage / f'{label}-GAME.IMG'
    with image.open('wb') as f:
        f.truncate(360 * 1024)
    subprocess.run(['mformat', '-i', str(image), '-f', '360', '::'], check=True)
    subprocess.run(['mcopy', '-i', str(image), *map(str, sorted(folder.iterdir())), '::/'], check=True)
readme = '''Moon Mission - game-only release

START-GAME.IMG and LANDING-GAME.IMG are 360K data disks, NOT bootable disks.
They deliberately contain no DOS or BASIC interpreter. Start DOS separately,
provide your own compatible GWBASIC.EXE on START, then type GO with START in A:
and LANDING in B:. Existing single-drive support is not implied by this package.
The START/ and LANDING/ folders contain the same files for emulator directory mounts.
The source files are included under source/.

Emulator checks are functional smoke tests. Real Laser XT, Tandy 1000 and PCjr
hardware, successful landing/replay, score persistence and disk-swap verification
require separate sign-off by the maintainer before publication.
'''
(stage / 'RELEASE.txt').write_text(readme)
shutil.copytree(root / 'src', stage / 'source')
archive = release / 'Moon-Mission-game.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(stage.rglob('*')):
        if path.is_file():
            z.write(path, path.relative_to(stage))
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(release / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
print(f'Created {archive}: {digest}')
