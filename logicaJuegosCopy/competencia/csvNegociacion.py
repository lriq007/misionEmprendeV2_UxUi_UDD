from __future__ import annotations

import csv
from pathlib import Path

from competencia.equipo import Equipo
from juegos.negociacion import EvaluacionNegociacion


def cargarPerfilesNegociacion(rutaCsv: Path) -> dict[str, dict[str, str]]:
    perfiles: dict[str, dict[str, str]] = {}
    with rutaCsv.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            perfiles[fila["nombreEquipo"]] = dict(fila)
    return perfiles


def cargarEvaluacionesNegociacion(rutaCsv: Path) -> list[EvaluacionNegociacion]:
    evaluaciones: list[EvaluacionNegociacion] = []
    with rutaCsv.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            evaluaciones.append(
                EvaluacionNegociacion(
                    evaluador=fila["evaluador"],
                    evaluado=fila["evaluado"],
                    puntajeEquipo=int(fila["puntajeEquipo"]),
                    puntajeEmpatia=int(fila["puntajeEmpatia"]),
                    puntajeCreatividad=int(fila["puntajeCreatividad"]),
                    puntajeComunicacion=int(fila["puntajeComunicacion"]),
                    comentario=fila["comentario"],
                )
            )
    return evaluaciones


def exportarRankingNegociacion(rutaCsv: Path, ranking: list[Equipo]) -> None:
    rutaCsv.parent.mkdir(parents=True, exist_ok=True)
    with rutaCsv.open("w", encoding="utf-8", newline="") as archivo:
        campos = [
            "posicion",
            "nombreEquipo",
            "tokensEmpatia",
            "tokensCreatividad",
            "tokensEvaluacion",
            "tokensTotales",
            "ordenExposicion",
            "promedioEvaluacionRecibida",
            "evaluacionesRecibidas",
            "tokensNegociacion",
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
                    "ordenExposicion": equipo.ordenExposicion,
                    "promedioEvaluacionRecibida": f"{equipo.promedioEvaluacionRecibida:.2f}",
                    "evaluacionesRecibidas": equipo.evaluacionesRecibidas,
                    "tokensNegociacion": equipo.tokensNegociacion,
                }
            )
