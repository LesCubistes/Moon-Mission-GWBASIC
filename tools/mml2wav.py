# Render GW-BASIC PLAY strings to a square-wave WAV (PC speaker approximation).
import re, sys, wave, struct
src = open(sys.argv[1], newline='').read()
chunks = re.findall(r'"([^"]*)"', ''.join(l for l in src.splitlines() if re.match(r'\d+ DATA', l)))
mml = ''.join(chunks).upper()
RATE = 22050; o, l, t = 4, 4, 120; out = []
SEMI = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)
i = 0
def num():
    global i
    m = re.match(r'\d+', mml[i:]); 
    if not m: return None
    i += len(m.group()); return int(m.group())
while i < len(mml):
    c = mml[i]; i += 1
    if c in 'MB' and mml[i-1:i+1] in ('MB',) : i += 1; continue
    if c == 'M': i += 1; continue
    if c == 'O': o = num()
    elif c == 'L': l = num()
    elif c == 'T': t = num()
    elif c in SEMI or c == 'P':
        n = SEMI.get(c, None)
        while i < len(mml) and mml[i] in '-+#':
            n += -1 if mml[i] == '-' else 1; i += 1
        ln = num() or l; dots = 0
        while i < len(mml) and mml[i] == '.': dots += 1; i += 1
        dur = 60 / t * 4 / ln * (1.5 ** dots)
        f = None if n is None else 261.63 * 2 ** ((o - 3) + n / 12)
        on = int(dur * RATE * 7 / 8); off = int(dur * RATE) - on
        for k in range(on):
            out.append(0 if f is None else (5000 if (k * f / RATE) % 1 < .5 else -5000))
        out += [0] * off
w = wave.open(sys.argv[2], 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
w.writeframes(b''.join(struct.pack('<h', s) for s in out)); w.close()
print(f"{len(out)/RATE:.1f} seconds")
