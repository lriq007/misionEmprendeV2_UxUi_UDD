from __future__ import annotations

import csv
from pathlib import Path

from competencia.equipo import Equipo


def cargarEntregaLegoSimulada(rutaCsv: Path) -> dict[str, tuple[bool, str]]:
    entregas: dict[str, tuple[bool, str]] = {}
    with rutaCsv.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            entregas[fila["nombreEquipo"]] = (fila["subioImagenLego"] == "1", fila["imagenLego"])
    return entregas


def exportarRankingLego(rutaCsv: Path, ranking: list[Equipo]) -> None:
    rutaCsv.parent.mkdir(parents=True, exist_ok=True)
    with rutaCsv.open("w", encoding="utf-8", newline="") as archivo:
        campos = [
            "posicion",
            "nombreEquipo",
            "tokensEmpatia",
            "tokensCreatividad",
            "tokensEvaluacion",
            "tokensTotales",
            "tokensLego",
            "subioImagenLego",
            "imagenLego",
            "mensajesLego",
            "tipoMensajeLego",
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
                    "tokensLego": equipo.tokensLego,
                    "subioImagenLego": int(equipo.subioImagenLego),
                    "imagenLego": equipo.imagenLego,
                    "mensajesLego": equipo.mensajesLego,
                    "tipoMensajeLego": equipo.tipoMensajeLego,
                }
            )
