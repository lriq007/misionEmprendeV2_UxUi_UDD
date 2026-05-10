from __future__ import annotations

import csv
from pathlib import Path

from competencia.equipo import Equipo


def cargarEquiposSimulados(rutaCsv: Path) -> list[Equipo]:
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
                tiempoSopaSegundos=int(fila["tiempoSopaSegundos"]) if fila["tiempoSopaSegundos"] else None,
                porcentajeSopa=float(fila["porcentajeSopa"]),
                bonusEspera=int(fila["bonusEspera"]),
                ordenLlegada=int(fila["ordenLlegada"]),
            )
            equipos.append(equipo)
    return equipos


def exportarRanking(rutaCsv: Path, ranking: list[Equipo]) -> None:
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
            "tiempoSopaSegundos",
            "porcentajeSopa",
            "bonusEspera",
            "posicionSopa",
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
                    "tiempoSopaSegundos": equipo.tiempoSopaSegundos,
                    "porcentajeSopa": f"{equipo.porcentajeSopa:.2f}",
                    "bonusEspera": equipo.bonusEspera,
                    "posicionSopa": equipo.posicionSopa,
                }
            )
