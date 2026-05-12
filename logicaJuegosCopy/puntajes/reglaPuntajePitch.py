from __future__ import annotations

from juegos.creacionPitch import CreacionPitch


def calcularTokensCreacionPitch(pitch: CreacionPitch) -> int:
    tokens = 0
    for _, _, valor, _ in pitch.camposOrdenados():
        if valor.strip():
            tokens += 1
    return tokens
