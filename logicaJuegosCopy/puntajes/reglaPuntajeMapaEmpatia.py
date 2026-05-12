from __future__ import annotations

from dataclasses import dataclass

from competencia.equipo import Equipo
from juegos.mapaEmpatia import MapaEmpatia


@dataclass
class ResultadoMapaEmpatia:
    preguntasCompletas: int
    preguntasDetalleIdeal: int
    preguntasDesarrolladas: int
    preguntasSuperficiales: int
    apendicesBasura: int
    apendicesExcesivos: int
    finalizoBubbleMap: bool
    ajusteFinalizacion: int
    bonusDetalleIdeal: int
    bonusSolidez: int
    penalizacionBajaProfundidad: int
    penalizacionCalidadDeficiente: int
    penalizacionExceso: int
    puntajeContenido: int
    tokensSinExcelencia: int
    fortalezas: list[str]
    debilidades: list[str]


def _contarCaracteres(apendice: str) -> int:
    return len(apendice.strip())


def evaluarMapaEmpatia(mapa: MapaEmpatia, finalizoBubbleMap: bool) -> ResultadoMapaEmpatia:
    preguntasCompletas = 0
    preguntasDetalleIdeal = 0
    preguntasDesarrolladas = 0
    preguntasSuperficiales = 0
    apendicesBasura = 0
    apendicesExcesivos = 0

    for pregunta in mapa.obtenerPreguntasOrdenadas():
        largos = [_contarCaracteres(apendice) for apendice in pregunta.apendices]
        largosRespondidos = [largo for largo in largos if largo > 0]
        largosValidos = [largo for largo in largosRespondidos if 8 <= largo <= 100]

        apendicesBasura += sum(1 for largo in largosRespondidos if 1 <= largo <= 7)
        apendicesExcesivos += sum(1 for largo in largosRespondidos if largo > 100)

        if largosValidos:
            preguntasCompletas += 1
        if len(largosValidos) == 1:
            preguntasSuperficiales += 1
        if len(largosValidos) >= 2:
            preguntasDesarrolladas += 1
        if largosRespondidos and all(40 <= largo <= 60 for largo in largosRespondidos):
            preguntasDetalleIdeal += 1

    ajusteFinalizacion = 1 if finalizoBubbleMap else -1
    bonusDetalleIdeal = 1 if preguntasDetalleIdeal >= 4 else 0
    bonusSolidez = 1 if preguntasDesarrolladas >= 3 else 0
    penalizacionBajaProfundidad = 1 if preguntasSuperficiales >= 3 else 0
    penalizacionCalidadDeficiente = 1 if apendicesBasura >= 3 else 0
    penalizacionExceso = 1 if apendicesExcesivos >= 3 else 0

    puntajeContenido = max(
        0,
        preguntasCompletas
        + bonusDetalleIdeal
        + bonusSolidez
        - penalizacionBajaProfundidad
        - penalizacionCalidadDeficiente
        - penalizacionExceso,
    )
    tokensSinExcelencia = max(
        0,
        puntajeContenido + ajusteFinalizacion,
    )

    fortalezas: list[str] = []
    debilidades: list[str] = []
    if preguntasCompletas == 5:
        fortalezas.append("Respondieron las 5 preguntas del mapa.")
    elif preguntasCompletas >= 3:
        fortalezas.append("Avanzaron en la mayoria de las preguntas.")
    else:
        debilidades.append("Faltaron preguntas por desarrollar.")

    if bonusDetalleIdeal:
        fortalezas.append("Varias respuestas mantuvieron una extension clara y enfocada.")
    if bonusSolidez:
        fortalezas.append("Desarrollaron varias preguntas con mas de un aporte valido.")
    if finalizoBubbleMap:
        fortalezas.append("Finalizaron explicitamente dentro del tiempo.")
    else:
        debilidades.append("No enviaron la senal de finalizacion.")
    if penalizacionBajaProfundidad:
        debilidades.append("Varias preguntas quedaron con una sola respuesta valida.")
    if penalizacionCalidadDeficiente:
        debilidades.append("Hubo varios apendices demasiado breves.")
    if penalizacionExceso:
        debilidades.append("Hubo varios apendices demasiado extensos.")
    if not fortalezas:
        fortalezas.append("No se detectaron fortalezas relevantes en esta demo.")
    if not debilidades:
        debilidades.append("No se detectaron debilidades criticas en esta demo.")

    return ResultadoMapaEmpatia(
        preguntasCompletas=preguntasCompletas,
        preguntasDetalleIdeal=preguntasDetalleIdeal,
        preguntasDesarrolladas=preguntasDesarrolladas,
        preguntasSuperficiales=preguntasSuperficiales,
        apendicesBasura=apendicesBasura,
        apendicesExcesivos=apendicesExcesivos,
        finalizoBubbleMap=finalizoBubbleMap,
        ajusteFinalizacion=ajusteFinalizacion,
        bonusDetalleIdeal=bonusDetalleIdeal,
        bonusSolidez=bonusSolidez,
        penalizacionBajaProfundidad=penalizacionBajaProfundidad,
        penalizacionCalidadDeficiente=penalizacionCalidadDeficiente,
        penalizacionExceso=penalizacionExceso,
        puntajeContenido=puntajeContenido,
        tokensSinExcelencia=tokensSinExcelencia,
        fortalezas=fortalezas,
        debilidades=debilidades,
    )


def aplicarResultadoMapa(equipo: Equipo, resultado: ResultadoMapaEmpatia) -> None:
    equipo.finalizoBubbleMap = resultado.finalizoBubbleMap
    equipo.preguntasCompletas = resultado.preguntasCompletas
    equipo.preguntasDetalleIdeal = resultado.preguntasDetalleIdeal
    equipo.preguntasDesarrolladas = resultado.preguntasDesarrolladas
    equipo.preguntasSuperficiales = resultado.preguntasSuperficiales
    equipo.apendicesBasura = resultado.apendicesBasura
    equipo.apendicesExcesivos = resultado.apendicesExcesivos
    equipo.puntajeContenidoBubbleMap = resultado.puntajeContenido
    equipo.penalizacionBajaProfundidad = resultado.penalizacionBajaProfundidad
    equipo.penalizacionCalidadDeficiente = resultado.penalizacionCalidadDeficiente
    equipo.penalizacionExceso = resultado.penalizacionExceso


def asignarTokensMapaEmpatia(equipos: list[Equipo]) -> None:
    rankingContenido = sorted(
        equipos,
        key=lambda equipo: (-equipo.puntajeContenidoBubbleMap, equipo.ordenLlegada, equipo.nombreEquipo),
    )
    topContenido = {equipo.nombreEquipo for equipo in rankingContenido[:3]}

    equiposFinalizados = [equipo for equipo in equipos if equipo.finalizoBubbleMap and equipo.tiempoBubbleMapSegundos is not None]
    rankingTiempo = sorted(equiposFinalizados, key=lambda equipo: (equipo.tiempoBubbleMapSegundos, equipo.ordenLlegada))
    topTiempo = {equipo.nombreEquipo for equipo in rankingTiempo[:3]}

    for equipo in equipos:
        equipo.bonusExcelenciaVelocidad = (
            2 if equipo.nombreEquipo in topContenido and equipo.nombreEquipo in topTiempo else 0
        )
        tokens = max(
            0,
            equipo.puntajeContenidoBubbleMap
            + (1 if equipo.finalizoBubbleMap else -1)
            + equipo.bonusExcelenciaVelocidad
            + equipo.bonusEspera,
        )
        equipo.sumarTokensBubbleMap(tokens)
