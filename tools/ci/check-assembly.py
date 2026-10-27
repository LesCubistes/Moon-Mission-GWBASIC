#!/usr/bin/env python3
"""The BLOAD wrapper carries a 16-bit length; compare its complete payload with fresh NASM output."""
from pathlib import Path
import struct
import subprocess
root = Path(__file__).resolve().parents[2]
out = root / 'build/ci'
out.mkdir(parents=True, exist_ok=True)
for source, committed, what in [('ckpit', 'CKPIT.BIN', 'cockpit'), ('roll', 'ROLL.BIN', 'rolling moonscape')]:
    binary = out / f'{source}.bin'
    subprocess.run(['nasm', '-f', 'bin', str(root / f'asm/{source}.asm'), '-o', str(binary)], check=True)
    data = (root / 'assets' / committed).read_bytes()
    marker, segment, offset, length = struct.unpack('<BHHH', data[:7])
    assert marker == 0xFD, f'{committed}: invalid BLOAD marker'
    assert len(data) in (7 + length, 8 + length), f'{committed}: invalid BLOAD length'
    assert len(data) == 7 + length or data[-1] == 0x1A, f'{committed}: unexpected trailing data'
    payload, code = data[7:7 + length], binary.read_bytes()
    # The builders pad an odd-sized routine with one zero byte so it fills whole integers.
    assert payload == code or payload == code + b'\0', f'{what} assembly differs from committed {committed}'
    print(f'8086 {what} assembly matches all {len(code)} bytes of {committed}')
