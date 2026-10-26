#!/usr/bin/env python3
"""The BLOAD wrapper carries a 16-bit length; compare its complete payload."""
from pathlib import Path
import struct
import subprocess
root = Path(__file__).resolve().parents[2]
out = root / 'build/ci/ckpit.bin'
out.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['nasm', '-f', 'bin', str(root / 'asm/ckpit.asm'), '-o', str(out)], check=True)
data = (root / 'assets/CKPIT.BIN').read_bytes()
marker, segment, offset, length = struct.unpack('<BHHH', data[:7])
assert marker == 0xFD, 'Invalid BLOAD marker'
assert len(data) in (7 + length, 8 + length), 'Invalid BLOAD length'
assert len(data) == 7 + length or data[-1] == 0x1A, 'Unexpected trailing data'
assert data[7:7 + length] == out.read_bytes(), 'Cockpit assembly differs from committed BLOAD payload'
print(f'8086 cockpit assembly matches all {length} payload bytes')
