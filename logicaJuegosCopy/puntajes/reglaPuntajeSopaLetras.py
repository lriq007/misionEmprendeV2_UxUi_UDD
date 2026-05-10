from __future__ import annotations

from competencia.equipo import Equipo


def ordenarRankingSopa(equipos: list[Equipo]) -> list[Equipo]:
    # Terminados primero por tiempo; no terminados por porcentaje y orden de llegada.
    return sorted(
        equipos,
        key=lambda equipo: (
            0 if equipo.porcentajeSopa >= 100 else 1,
            equipo.tiempoSopaSegundos if equipo.porcentajeSopa >= 100 and equipo.tiempoSopaSegundos is not None else 10**9,
            -equipo.porcentajeSopa,
            equipo.ordenLlegada,
        ),
    )


def calcularTokensSopa(equipo: Equipo, posicion: int) -> int:
    if equipo.porcentajeSopa >= 100:
        if posicion == 1:
            return 5
        if posicion == 2:
            return 4
        return 3
    if equipo.porcentajeSopa >= 80:
        return 2
    if equipo.porcentajeSopa >= 40:
        return 1
    return 0


def asignarTokensSopa(equipos: list[Equipo]) -> list[Equipo]:
    rankingSopa = ordenarRankingSopa(equipos)
    tokensPorPorcentajeNoTerminado: dict[float, int] = {}

    for posicion, equipo in enumerate(rankingSopa, start=1):
        equipo.posicionSopa = posicion
        if equipo.porcentajeSopa < 100:
            # Si no terminaron y empatan en porcentaje, reciben los mismos tokens.
            tokens = tokensPorPorcentajeNoTerminado.setdefault(
                equipo.porcentajeSopa,
                calcularTokensSopa(equipo, posicion),
            )
        else:
            tokens = calcularTokensSopa(equipo, posicion)
        equipo.sumarTokensSopa(tokens)
        if equipo.bonusEspera > 0:
            equipo.sumarTokensSopa(equipo.bonusEspera)

    return rankingSopa
