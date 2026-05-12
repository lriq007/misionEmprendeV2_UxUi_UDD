from __future__ import annotations

from collections import defaultdict

from competencia.equipo import Equipo
from juegos.negociacion import EvaluacionNegociacion


def calcularTokensPorPromedio(promedio: float) -> int:
    if promedio < 2.5:
        return 0
    if promedio < 3.5:
        return 2
    if promedio < 4.5:
        return 4
    return 6


def asignarTokensNegociacion(equipos: list[Equipo], evaluaciones: list[EvaluacionNegociacion]) -> None:
    puntajesPorEquipo: dict[str, list[int]] = defaultdict(list)
    for evaluacion in evaluaciones:
        if evaluacion.evaluador == evaluacion.evaluado:
            continue
        puntajesPorEquipo[evaluacion.evaluado].append(evaluacion.puntajeEquipo)

    for equipo in equipos:
        puntajes = puntajesPorEquipo.get(equipo.nombreEquipo, [])
        equipo.evaluacionesRecibidas = len(puntajes)
        if not puntajes:
            equipo.promedioEvaluacionRecibida = 0
            equipo.sumarTokensNegociacion(0)
            continue
        promedio = sum(puntajes) / len(puntajes)
        equipo.promedioEvaluacionRecibida = promedio
        equipo.sumarTokensNegociacion(calcularTokensPorPromedio(promedio))
