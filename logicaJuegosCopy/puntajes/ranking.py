from __future__ import annotations

from competencia.equipo import Equipo


def ordenarRankingGlobal(equipos: list[Equipo]) -> list[Equipo]:
    # Criterio principal compatible con Django: tokensTotales.
    return sorted(
        equipos,
        key=lambda equipo: (
            -equipo.tokensTotales,
            equipo.tiempoGlobalSegundos if equipo.tiempoGlobalSegundos is not None else 10**9,
            equipo.posicionSopa if equipo.posicionSopa is not None else 10**9,
            -equipo.porcentajeSopa,
            equipo.ordenLlegada,
        ),
    )


def ordenarRankingGlobalBubbleMap(equipos: list[Equipo]) -> list[Equipo]:
    return sorted(
        equipos,
        key=lambda equipo: (
            -equipo.tokensTotales,
            equipo.tiempoGlobalSegundos if equipo.tiempoGlobalSegundos is not None else 10**9,
            equipo.tiempoBubbleMapSegundos if equipo.tiempoBubbleMapSegundos is not None else 10**9,
            equipo.nombreEquipo,
        ),
    )


def obtenerPosicionEquipo(equiposOrdenados: list[Equipo], nombreEquipo: str) -> int | None:
    for indice, equipo in enumerate(equiposOrdenados, start=1):
        if equipo.nombreEquipo == nombreEquipo:
            return indice
    return None


def imprimirRanking(ranking: list[Equipo], nombreEquipoActual: str | None = None) -> None:
    print("\n=== RANKING GLOBAL ===")
    for posicion, equipo in enumerate(ranking, start=1):
        marca = " <== equipo en sesion" if equipo.nombreEquipo == nombreEquipoActual else ""
        print(
            f"{posicion}. {equipo.nombreEquipo} | "
            f"tokens={equipo.tokensTotales} | "
            f"sopa={equipo.porcentajeSopa:.0f}% | "
            f"bonus={equipo.bonusEspera}{marca}"
        )


def imprimirRankingEstandar(ranking: list[Equipo], nombreEquipoActual: str) -> None:
    print("\n=== RANKING GLOBAL ===")
    posicionActual = obtenerPosicionEquipo(ranking, nombreEquipoActual)
    for posicion, equipo in enumerate(ranking, start=1):
        marca = " <== TU EQUIPO" if equipo.nombreEquipo == nombreEquipoActual else ""
        print(f"{posicion}. {equipo.nombreEquipo} | tokens={equipo.tokensTotales}{marca}")
    if posicionActual is not None:
        print(f"\nTu equipo esta en la posicion {posicionActual} de {len(ranking)}.")
