from __future__ import annotations

import csv
from pathlib import Path

from competencia.equipo import Equipo


def cargarEquiposSimuladosBubbleMap(rutaCsv: Path) -> list[Equipo]:
    equipos: list[Equipo] = []
    with rutaCsv.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            equipo = Equipo(
                nombreEquipo=fila["nombreEquipo"],
                tokensEmpatia=int(fila["tokensEmpatia"]),
                tokensCreatividad=int(fila["tokensCreatividad"]),
                tokensEvaluacion=int(fila["tokensEvaluacion"]),
                tiempoGlobalSegundos=int(fila["tiempoGlobalSegundos"]) if fila["tiempoGlobalSegundos"] else None,
                tiempoBubbleMapSegundos=(
                    int(fila["tiempoBubbleMapSegundos"]) if fila["tiempoBubbleMapSegundos"] else None
                ),
                finalizoBubbleMap=fila["finalizoBubbleMap"] == "1",
                preguntasCompletas=int(fila["preguntasCompletas"]),
                preguntasDetalleIdeal=int(fila["preguntasDetalleIdeal"]),
                preguntasDesarrolladas=int(fila["preguntasDesarrolladas"]),
                preguntasSuperficiales=int(fila["preguntasSuperficiales"]),
                apendicesBasura=int(fila["apendicesBasura"]),
                apendicesExcesivos=int(fila["apendicesExcesivos"]),
                bonusEspera=int(fila["bonusEspera"]),
                ordenLlegada=int(fila["ordenLlegada"]),
            )
            equipo.penalizacionBajaProfundidad = 1 if equipo.preguntasSuperficiales >= 3 else 0
            equipo.penalizacionCalidadDeficiente = 1 if equipo.apendicesBasura >= 3 else 0
            equipo.penalizacionExceso = 1 if equipo.apendicesExcesivos >= 3 else 0
            equipo.puntajeContenidoBubbleMap = max(
                0,
                equipo.preguntasCompletas
                + (1 if equipo.preguntasDetalleIdeal >= 4 else 0)
                + (1 if equipo.preguntasDesarrolladas >= 3 else 0)
                - equipo.penalizacionBajaProfundidad
                - equipo.penalizacionCalidadDeficiente
                - equipo.penalizacionExceso,
            )
            equipos.append(equipo)
    return equipos


def exportarRankingBubbleMap(rutaCsv: Path, ranking: list[Equipo]) -> None:
    rutaCsv.parent.mkdir(parents=True, exist_ok=True)
    with rutaCsv.open("w", encoding="utf-8", newline="") as archivo:
        campos = [
            "posicion",
            "nombreEquipo",
            "tokensEmpatia",
            "tokensCreatividad",
            "tokensEvaluacion",
            "tokensTotales",
            "tiempoGlobalSegundos",
            "tiempoBubbleMapSegundos",
            "finalizoBubbleMap",
            "preguntasCompletas",
            "preguntasDetalleIdeal",
            "preguntasDesarrolladas",
            "preguntasSuperficiales",
            "apendicesBasura",
            "apendicesExcesivos",
            "puntajeContenidoBubbleMap",
            "bonusExcelenciaVelocidad",
            "bonusEspera",
            "tokensBubbleMap",
        ]
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for posicion, equipo in enumerate(ranking, start=1):
            escritor.writerow(
                {
                    "posicion": posicion,
                    "nombreEquipo": equipo.nombreEquipo,
                    "tokensEmpatia": equipo.tokensEmpatia,
                    "tokensCreatividad": equipo.tokensCreatividad,
                    "tokensEvaluacion": equipo.tokensEvaluacion,
                    "tokensTotales": equipo.tokensTotales,
                    "tiempoGlobalSegundos": equipo.tiempoGlobalSegundos,
                    "tiempoBubbleMapSegundos": equipo.tiempoBubbleMapSegundos,
                    "finalizoBubbleMap": int(equipo.finalizoBubbleMap),
                    "preguntasCompletas": equipo.preguntasCompletas,
                    "preguntasDetalleIdeal": equipo.preguntasDetalleIdeal,
                    "preguntasDesarrolladas": equipo.preguntasDesarrolladas,
                    "preguntasSuperficiales": equipo.preguntasSuperficiales,
                    "apendicesBasura": equipo.apendicesBasura,
                    "apendicesExcesivos": equipo.apendicesExcesivos,
                    "puntajeContenidoBubbleMap": equipo.puntajeContenidoBubbleMap,
                    "bonusExcelenciaVelocidad": equipo.bonusExcelenciaVelocidad,
                    "bonusEspera": equipo.bonusEspera,
                    "tokensBubbleMap": equipo.tokensBubbleMap,
                }
            )
