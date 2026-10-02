"""Efeitos sonoros da Nina sintetizados por código (no estilo sfxr/rfxgen).

Nada de arquivo de terceiros: cada som nasce de seno + ruído + envelope, com
semente fixa — o mesmo roteiro sempre gera o mesmo áudio e não há licença a
conferir. Todos retornam float64 mono em SR (48 kHz) com pico próximo de 1;
quem mixa decide o volume.

eventos(ep, segs) devolve a lista (tempo, som, volume) que acompanha as
animações de motor/hyperframes.py (entrada do cartão, wipe, flash, ícones e
confete final).
"""
from __future__ import annotations

import numpy as np

SR = 48000


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _rng(seed):
    return np.random.default_rng(seed)


def _norm(x):
    p = np.max(np.abs(x)) or 1.0
    return x / p


def _lowpass(x, corte):
    """Passa-baixa de 1 polo com corte (Hz) fixo ou variável no tempo."""
    corte = np.broadcast_to(np.asarray(corte, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * corte / SR)
    y = np.empty_like(x)
    v = 0.0
    for i in range(len(x)):
        v += a[i] * (x[i] - v)
        y[i] = v
    return y


def whoosh(dur=0.5, grave=False, seed=1):
    t = _t(dur)
    n = _rng(seed).normal(size=len(t))
    p = t / dur
    sweep = (300 + 3200 * np.sin(np.pi * p) ** 2) * (0.45 if grave else 1.0)
    banda = _lowpass(n, sweep) - _lowpass(n, sweep * 0.25)
    env = np.sin(np.pi * np.clip(p * 1.15, 0, 1)) ** 2
    return _norm(banda * env)


def pop(seed=2):
    t = _t(0.12)
    f = 520 * np.exp(-t * 28) + 170
    tom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32)
    clique = _rng(seed).normal(size=len(t)) * np.exp(-t * 400) * 0.35
    return _norm(tom + clique)


def papel(seed=3):
    """Cartão de papel batendo: ruído agudo curtíssimo."""
    t = _t(0.09)
    n = _rng(seed).normal(size=len(t))
    agudo = np.diff(n, prepend=0)
    return _norm(agudo * np.exp(-t * 55))


def ping():
    """Notificação de celular: dois toques de sino."""
    out = np.zeros(int(0.42 * SR))
    for k, f in enumerate((1318.5, 1760.0)):
        t = _t(0.3)
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 14)
        i = int(k * 0.11 * SR)
        out[i:i + len(s)] += s[: len(out) - i]
    return _norm(out)


def tique(agudo=True):
    t = _t(0.035)
    f = 2400 if agudo else 1700
    return _norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 160))


def coracao():
    """Tum-tum grave."""
    out = np.zeros(int(0.55 * SR))
    for k, (atraso, g) in enumerate(((0.0, 1.0), (0.2, 0.7))):
        t = _t(0.22)
        f = 70 * np.exp(-t * 6) + 42
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * g
        i = int(atraso * SR)
        out[i:i + len(s)] += s
    return _norm(out)


def digitando(n=6, seed=4):
    rng = _rng(seed)
    out = np.zeros(int(0.12 * n * SR) + SR // 10)
    for k in range(n):
        t = _t(0.03)
        s = rng.normal(size=len(t)) * np.exp(-t * 220)
        i = int((k * 0.11 + rng.uniform(0, 0.03)) * SR)
        out[i:i + len(s)] += s * rng.uniform(0.6, 1.0)
    return _norm(np.diff(out, prepend=0))


def portao(dur=1.2, seed=5):
    t = _t(dur)
    n = _rng(seed).normal(size=len(t))
    ronco = _lowpass(n, 180) * (1 + 0.3 * np.sin(2 * np.pi * 9 * t))
    env = np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.3)
    return _norm(ronco * env)


def impacto(seed=6):
    """Choque: batida grave + ar."""
    t = _t(0.6)
    f = 110 * np.exp(-t * 9) + 38
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    ar = _lowpass(_rng(seed).normal(size=len(t)), 900) * np.exp(-t * 10) * 2
    return _norm(boom + ar)


def brilho():
    """Arpejo cintilante do confete final."""
    notas = (1046.5, 1318.5, 1568.0, 2093.0)
    out = np.zeros(int(1.3 * SR))
    for k, f in enumerate(notas):
        t = _t(0.7)
        s = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 3 * f * t)) * np.exp(-t * 7)
        i = int(k * 0.09 * SR)
        out[i:i + len(s)] += s
    return _norm(out)


SONS = {
    "whoosh": whoosh, "whoosh_grave": lambda: whoosh(0.7, grave=True, seed=7),
    "pop": pop, "papel": papel, "ping": ping, "tique": tique, "taque": lambda: tique(False),
    "coracao": coracao, "digitando": digitando, "portao": portao,
    "impacto": impacto, "brilho": brilho,
}

# volume de cada som na mixagem (pico); a voz fica perto de 0.85
VOLUME = {
    "whoosh": 0.16, "whoosh_grave": 0.18, "pop": 0.11, "papel": 0.10, "ping": 0.12,
    "tique": 0.06, "taque": 0.06, "coracao": 0.26, "digitando": 0.07, "portao": 0.16,
    "impacto": 0.24, "brilho": 0.10,
}


def tem_wipe(b, i):
    return bool(i and (b.get("zoom") or i % 4 == 0))


def tem_flash(b, i):
    return b.get("expr") == "chocada"


def eventos(ep, segs):
    """(tempo, som, volume) alinhados às animações do compor()."""
    ev = []
    for i, (b, s) in enumerate(zip(ep["batidas"], segs)):
        a, z = float(s["ini"]), float(s["fim"])
        d = z - a
        tipo = (b.get("arte") or [None])[0]
        if i:
            ev.append((a, "papel", VOLUME["papel"]))
            ev.append((a + 0.05, "pop", VOLUME["pop"]))
        if tem_wipe(b, i):
            ev.append((max(0.0, a - 0.05), "whoosh", VOLUME["whoosh"]))
        if tem_flash(b, i):
            ev.append((a, "impacto", VOLUME["impacto"]))
        if tipo in ("celular", "notificacao", "direct"):
            ev.append((a + 0.2, "ping", VOLUME["ping"]))
        elif tipo == "conversa":
            ev.append((a + 0.25, "digitando", VOLUME["digitando"]))
            ev.append((a + 1.0, "ping", VOLUME["ping"] * 0.8))
        elif tipo == "relogio":
            k, t = 0, a + 0.1
            while t < min(z, a + 4.0):
                ev.append((t, "tique" if k % 2 == 0 else "taque", VOLUME["tique"]))
                t += 0.5
                k += 1
        elif tipo == "coracao":
            for k in range(min(3, max(1, int(d / 1.0)))):
                ev.append((a + 0.1 + k * 0.9, "coracao", VOLUME["coracao"]))
        elif tipo == "porta":
            ev.append((a + 0.1, "portao", VOLUME["portao"]))
        elif tipo == "carro":
            ev.append((a, "whoosh_grave", VOLUME["whoosh_grave"]))
    ev.append((float(segs[-1]["fim"]), "brilho", VOLUME["brilho"]))
    return ev


def trilha_sfx(ep, segs, dur):
    """Pista só de efeitos, já com volume, na duração do vídeo."""
    out = np.zeros(int(np.ceil(dur * SR)))
    cache = {}
    for t0, nome, vol in eventos(ep, segs):
        if nome not in cache:
            cache[nome] = SONS[nome]()
        s = cache[nome] * vol
        i = int(t0 * SR)
        n = min(len(s), len(out) - i)
        if n > 0 and i >= 0:
            out[i:i + n] += s[:n]
    return out
