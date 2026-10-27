#!/usr/bin/env python3
"""Prepare pinned DOS and interpreter fixtures; generic GW-BASIC 3.22 is the CI default."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import urllib.request

REV = '68cebf5a3b7fed40536e5778b3233065f7ecdca9'
URL = f'https://raw.githubusercontent.com/superterran/tandy1000ex/{REV}/img/Tandy%20System%20Disk%201%20-%20DOS%202.1.img'
ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--basic', choices=['generic', 'tandy'], default='generic')
args = parser.parse_args()
fixture = ROOT / 'build/ci/tandy-system.img'
fixture.parent.mkdir(parents=True, exist_ok=True)
with urllib.request.urlopen(URL, timeout=60) as response:
    data = response.read()
expected = (ROOT / 'tools/ci/runtime.sha256').read_text().split()[0]
if hashlib.sha256(data).hexdigest() != expected:
    raise SystemExit('Tandy fixture checksum mismatch')
fixture.write_bytes(data)
(ROOT / 'dos').mkdir(exist_ok=True)
subprocess.run(['mcopy', '-o', '-i', str(fixture), '::/BASIC.EXE', str(ROOT / 'dos/GWBASIC.EXE')], check=True)
# Work only on a copy; retain DOS boot/system files and free room for the game.
base = ROOT / 'dos/DISK01.IMG'
base.write_bytes(data)
subprocess.run(['mdel', '-i', str(base), '::/BASIC.EXE', '::/LIB.EXE', '::/LINK.EXE'], check=True)
print(f'Prepared Tandy DOS/BASIC fixture at {REV}; sha256={expected}')

if args.basic == 'generic':
    url = 'https://archive.org/download/gwbasic_201909/gwbasic.exe'
    expected_basic = '49f116147df5ae16147bd11ab39c098446a13ce6fa2cab38f794b51fdc6a32b4'
    with urllib.request.urlopen(url, timeout=60) as response:
        interpreter = response.read()
    if hashlib.sha256(interpreter).hexdigest() != expected_basic:
        raise SystemExit('GW-BASIC 3.22 fixture checksum mismatch')
    (ROOT / 'dos/GWBASIC.EXE').write_bytes(interpreter)
    print(f'Prepared generic GW-BASIC 3.22; sha256={expected_basic}')
