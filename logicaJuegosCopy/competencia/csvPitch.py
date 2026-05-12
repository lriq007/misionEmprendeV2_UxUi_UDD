from __future__ import annotations

import csv
from pathlib import Path

from competencia.equipo import Equipo
from juegos.creacionPitch import CreacionPitch
from puntajes.reglaPuntajePitch import calcularTokensCreacionPitch


def cargarPitchSimulado(rutaCsv: Path) -> dict[str, Equipo]:
    equipos: dict[str, Equipo] = {}
    with rutaCsv.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            equipo = Equipo(
                nombreEquipo=fila["nombreEquipo"],
                nombreProductoPitch=fila["nombreProductoPitch"],
                desafioEmpatiaPitch=fila["desafioEmpatiaPitch"],
                creatividadPitch=fila["creatividadPitch"],
                cierrePitch=fila["cierrePitch"],
                finalizoPitchCreacion=fila["finalizoPitchCreacion"] == "1",
                tiempoPitchCreacionSegundos=(
                    int(fila["tiempoPitchCreacionSegundos"]) if fila["tiempoPitchCreacionSegundos"] else None
                ),
            )
            pitch = CreacionPitch(
                nombreProducto=equipo.nombreProductoPitch,
                desafioEmpatia=equipo.desafioEmpatiaPitch,
                creatividad=equipo.creatividadPitch,
                cierre=equipo.cierrePitch,
            )
            equipo.tokensPitchCreacion = calcularTokensCreacionPitch(pitch)
            equipos[equipo.nombreEquipo] = equipo
    return equipos


def exportarRankingPitch(rutaCsv: Path, ranking: list[Equipo]) -> None:
    rutaCsv.parent.mkdir(parents=True, exist_ok=True)
    with rutaCsv.open("w", encoding="utf-8", newline="") as archivo:
        campos = [
            "posicion",
            "nombreEquipo",
            "tokensEmpatia",
            "tokensCreatividad",
            "tokensEvaluacion",
            "tokensTotales",
            "tokensPitchCreacion",
            "nombreProductoPitch",
            "desafioEmpatiaPitch",
            "creatividadPitch",
            "cierrePitch",
            "finalizoPitchCreacion",
            "tiempoPitchCreacionSegundos",
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
                    "tokensPitchCreacion": equipo.tokensPitchCreacion,
                    "nombreProductoPitch": equipo.nombreProductoPitch,
                    "desafioEmpatiaPitch": equipo.desafioEmpatiaPitch,
                    "creatividadPitch": equipo.creatividadPitch,
                    "cierrePitch": equipo.cierrePitch,
                    "finalizoPitchCreacion": int(equipo.finalizoPitchCreacion),
                    "tiempoPitchCreacionSegundos": equipo.tiempoPitchCreacionSegundos,
                }
            )
