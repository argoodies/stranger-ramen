# a 30 s soundtrack in the game's own synthesis (as botc-video/make.py): soft pad chords, a scattered pentatonic melody, a few event chimes, the tower bell on the title
import numpy as np, wave, math, random
SR = 44100; T = 30.0; n = int(T * SR); L = np.zeros(n); R = np.zeros(n); TAU = 2 * math.pi
mtof = lambda m: 440 * 2 ** ((m - 69) / 12); tt = lambda d: np.arange(int(d * SR)) / SR
def add(sig, t0, amp=1.0, pan=.5):
    i = int(t0 * SR); sig = sig[:n - i]; L[i:i + len(sig)] += sig * amp * math.cos(pan * math.pi / 2); R[i:i + len(sig)] += sig * amp * math.sin(pan * math.pi / 2)
def chime(m, dur=3.0, dec=.8):
    f = mtof(m); t = tt(dur); s = np.sin(TAU * f * t) * np.exp(-t / dec) + .32 * np.sin(TAU * 2 * f * t) * np.exp(-t / (dec * .45)) + .14 * np.sin(TAU * 4.2 * f * t) * np.exp(-t / .07)
    return s * np.minimum(1, t / .004)
def bell(f, dur=6.0):
    t = tt(dur); s = np.zeros_like(t)
    for rat, a, d in [(.5, .55, 4.5), (1, 1, 3.4), (1.19, .55, 2.6), (1.5, .32, 2), (2, .45, 1.5), (2.74, .22, 1), (4.07, .1, .45)]: s += a * np.sin(TAU * f * rat * t + rat) * np.exp(-t / d)
    return s * np.minimum(1, t / .006)
def pad(notes, t0, dur, amp):
    t = tt(dur); env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2); env = env * env * (3 - 2 * env)
    for side, det in ((.15, 1.0035), (.85, .9965)):
        s = np.zeros_like(t)
        for j, m in enumerate(notes): f = mtof(m); s += (1 / (1 + j * .35)) * (np.sin(TAU * f * t + j) + .6 * np.sin(TAU * f * det * t + 2 * j))
        add(s * env, t0, amp / len(notes) * 2, side)
WARM = [[38, 45, 50, 54, 57, 64], [35, 42, 47, 50, 54, 61], [43, 50, 55, 59, 62], [40, 47, 52, 55, 62]]
for k in range(6): pad(WARM[k % 4], k * 3.3, 4.6, .09)                                  # ramen, the walk out, coffee: warm (0-18)
pad([36, 43, 48, 51, 55], 17.4, 4.6, .1); pad([33, 40, 45, 48, 52], 21.6, 5.4, .1)       # the torch and the whirlwinds; the farewell and the rain: darker
pad([38, 45, 50, 54, 57, 64], 26.8, 3.2, .1)                                             # the title
SC = [62, 64, 66, 69, 71, 74, 76, 78]; rng = random.Random(7); idx = 3; t = .6
while t < 26.4:
    if rng.random() < .5: idx = max(0, min(len(SC) - 1, idx + rng.choice([-2, -1, 1, 2]))); add(chime(SC[idx] if t < 17.4 else SC[idx] - 3), t, rng.uniform(.05, .085), rng.uniform(.3, .7))
    t += .6
for at, m in [(.3, 74), (11.4, 79), (13.6, 69)]: add(chime(m, 3, .9), at, .14, .5)        # a soft chime at each cut
for at, m in [(.6, 67), (3.6, 72), (4.3, 74), (5.0, 69), (5.6, 74), (6.3, 76), (6.9, 74), (7.6, 78), (8.2, 74), (8.9, 71), (9.5, 74), (10.3, 76), (10.3, 79)]: add(chime(m, 1.4, .3), at, .07, .45)   # each tap in the ramen shop
add(chime(86, 2, .5), 3.2, .08, .6); add(chime(90, 2, .5), 3.3, .06, .6)                  # the noodles are done
add(bell(110.0), 18.4, .22)                                                              # the torch is lit
add(bell(98.0, 7), 21.6, .14)                                                            # the farewell
add(bell(146.8), 26.85, .3)                                                              # the title
for j, m in enumerate([74, 78, 81, 86]): add(chime(m, 3, 1.0), 26.95 + .12 * j, .1, .6)
x = np.stack([L, R], 1); x /= max(1e-9, np.abs(x).max()) / .85
fo = np.ones(n); fo[-int(1.4 * SR):] = np.linspace(1, 0, int(1.4 * SR)); x *= fo[:, None]
w = wave.open('music.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close(); print('ok')
