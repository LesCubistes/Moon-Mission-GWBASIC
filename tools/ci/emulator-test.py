#!/usr/bin/env python3
"""Assert a real keyboard/screen journey; do not patch or instrument game code."""
import argparse
from difflib import SequenceMatcher
import json
import os
from pathlib import Path
import re
import subprocess
import time
from PIL import Image, ImageGrab, ImageOps

p = argparse.ArgumentParser()
p.add_argument('--machine', choices=['cga', 'tandy', 'pcjr'], required=True)
p.add_argument('--cycles', type=int, default=1200)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
out = root / 'build/ci' / f'{a.machine}-{a.cycles}'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, SDL_AUDIODRIVER='dummy')
conf = out / 'dosbox.conf'
conf.write_text(f'''[sdl]
fullscreen=false
output=surface
[dosbox]
machine={a.machine}
memsize=1
[cpu]
core=normal
cycles=fixed {a.cycles}
[render]
aspect=false
scaler=normal2x
[sblaster]
sbtype=none
[autoexec]
imgmount a "{root}/disks/START.IMG" -t floppy
imgmount b "{root}/disks/LANDING.IMG" -t floppy
a:
gwbasic moon
exit
''')
checks = []
log = (out / 'emulator.log').open('w')
proc = subprocess.Popen(['dosbox', '-conf', str(conf), '-noconsole'], env=env, stdout=log, stderr=log)
window = None

def key(name):
    subprocess.run(['xdotool', 'windowfocus', window, 'key', '--clearmodifiers', name], env=env, check=True)

def screenshot(label):
    image = ImageGrab.grab()
    image.save(out / f'{label}.png')
    # OCR a monochrome copy; evidence always retains the original palette.
    geometry = subprocess.run(['xdotool', 'getwindowgeometry', '--shell', window], env=env, capture_output=True, text=True, check=True).stdout
    g = dict(line.split('=', 1) for line in geometry.splitlines() if '=' in line)
    x, y, width, height = (int(g[k]) for k in ['X', 'Y', 'WIDTH', 'HEIGHT'])
    crop = image.crop((x, y, x + width, y + height))
    crop = crop.resize((width * 3, height * 3), Image.Resampling.NEAREST)
    channels = crop.convert('RGB').split()
    from PIL import ImageChops
    bright = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    gray = bright.point(lambda x: 0 if x > 80 else 255)
    regions = {'title': (0, 0, 1, .4), 'menu': (.225, .74, .775, .99),
               'return-menu': (.225, .74, .775, .99),
               'orbit': (0, 0, 1, .09), 'return-orbit': (0, 0, 1, .09),
               'flight': (0, 0, 1, .12), 'retry': (0, 0, 1, .12),
               'crash': (.2, .3, .8, .55)}
    left, top, right, bottom = regions[label]
    gray = gray.crop((int(gray.width * left), int(gray.height * top),
                      int(gray.width * right), int(gray.height * bottom)))
    gray = ImageOps.expand(gray, border=40, fill=255)
    gray.save(out / 'ocr.png')
    result = subprocess.run(['tesseract', str(out / 'ocr.png'), 'stdout', '--psm', '6'], capture_output=True, text=True, check=True)
    text = result.stdout.upper()
    (out / f'{label}.txt').write_text(text)
    return re.sub(r'[^A-Z0-9]', '', text)

def contains(text, expected):
    # The IBM bitmap font produces occasional OCR substitutions. Require >=85%
    # agreement within a short substring, never a whole-screen similarity score.
    for size in range(max(1, len(expected) - 2), len(expected) + 3):
        for start in range(len(text) - size + 1):
            if SequenceMatcher(None, expected, text[start:start + size]).ratio() >= .85:
                return True
    return False


def wait_for(label, patterns, timeout=100):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if proc.poll() is not None:
            raise AssertionError(f'Emulator exited before {label}: {proc.returncode}')
        text = screenshot(label)
        if any(re.search(x, text) for x in ['SYNTAXERROR', 'ILLEGALFUNCTION', 'OUTOFMEMORY', 'FILENOTFOUND', 'UNDEFINEDLINE']):
            raise AssertionError(f'BASIC error during {label}: {text}')
        if all(contains(text, pattern) for pattern in patterns):
            checks.append(label)
            print(f'PASS {a.machine}/{a.cycles}: {label}', flush=True)
            return
        time.sleep(1)
    raise AssertionError(f'Timed out waiting for {label}; see screenshot and OCR text')

try:
    for _ in range(100):
        found = subprocess.run(['xdotool', 'search', '--pid', str(proc.pid)], env=env, capture_output=True, text=True).stdout.split()
        if found:
            window = found[-1]
            break
        time.sleep(.1)
    if window is None:
        raise AssertionError('No DOSBox window')
    wait_for('title', ['MOONMISSION'])
    key('space')
    wait_for('menu', ['SELECTMISSION', 'MOONLANDING'])
    key('Return')
    wait_for('orbit', ['SELECTLANDINGSITE', 'DESCEND'])
    key('Return')
    wait_for('flight', ['FUEL', 'LANDER'])
    # An unpowered descent must reach the crash/report path rather than hang.
    wait_for('crash', ['LANDERSLEFT', 'ENTER'], timeout=120)
    key('Return')
    wait_for('retry', ['FUEL', 'LANDER'])
    key('Escape')
    wait_for('return-orbit', ['SELECTLANDINGSITE'])
    key('Escape')
    wait_for('return-menu', ['SELECTMISSION'])
    key('Escape')
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        raise AssertionError('Exit to DOS did not close emulator')
    if proc.returncode != 0:
        raise AssertionError(f'Unexpected emulator exit: {proc.returncode}')
    checks.append('exit')
finally:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    log.close()
    (out / 'results.json').write_text(json.dumps({'machine': a.machine, 'cycles': a.cycles, 'passed': checks}, indent=2) + '\n')
