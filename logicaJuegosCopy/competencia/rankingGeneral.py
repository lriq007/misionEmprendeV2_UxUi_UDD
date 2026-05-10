from __future__ import annotations

import csv
from pathlib import Path

from competencia.equipo import Equipo
from puntajes.ranking import ordenarRankingGlobalBubbleMap


CAMPOS_RANKING_GENERAL = [
    "posicion",
    "nombreEquipo",
    "tokensEmpatia",
    "tokensCreatividad",
    "tokensEvaluacion",
    "tokensTotales",
    "tokensSopa",
    "tokensBubbleMap",
    "tokensLego",
    "tokensPitchCreacion",
    "tokensNegociacion",
    "subioImagenLego",
    "imagenLego",
    "mensajesLego",
    "tipoMensajeLego",
    "nombreProductoPitch",
    "finalizoPitchCreacion",
    "tiempoPitchCreacionSegundos",
    "ordenExposicion",
    "promedioEvaluacionRecibida",
    "evaluacionesRecibidas",
    "tiempoGlobalSegundos",
    "tiempoSopaSegundos",
    "tiempoBubbleMapSegundos",
    "porcentajeSopa",
    "posicionSopa",
    "finalizoBubbleMap",
    "bonusEspera",
    "ordenLlegada",
]


def cargarEquiposSesion(rutaCsv: Path) -> list[Equipo]:
    equipos: list[Equipo] = []
    with rutaCsv.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            equipos.append(
                Equipo(
                    nombreEquipo=fila["nombreEquipo"],
                    tokensEmpatia=int(fila["tokensEmpatia"]),
                    tokensCreatividad=int(fila["tokensCreatividad"]),
                    tokensEvaluacion=int(fila["tokensEvaluacion"]),
                    ordenLlegada=int(fila["ordenLlegada"]),
                )
            )
    return equipos


def cargarRankingGeneral(rutaCsv: Path, rutaSesion: Path) -> dict[str, Equipo]:
    if not rutaCsv.exists():
        equiposIniciales = cargarEquiposSesion(rutaSesion)
        exportarRankingGeneral(rutaCsv, equiposIniciales)
        return {equipo.nombreEquipo: equipo for equipo in equiposIniciales}

    equipos: dict[str, Equipo] = {}
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
                tiempoBubbleMapSegundos=(
                    int(fila["tiempoBubbleMapSegundos"]) if fila["tiempoBubbleMapSegundos"] else None
                ),
                porcentajeSopa=float(fila["porcentajeSopa"]) if fila["porcentajeSopa"] else 0,
                posicionSopa=int(fila["posicionSopa"]) if fila["posicionSopa"] else None,
                finalizoBubbleMap=fila["finalizoBubbleMap"] == "1",
                bonusEspera=int(fila["bonusEspera"]) if fila["bonusEspera"] else 0,
                ordenLlegada=int(fila["ordenLlegada"]) if fila["ordenLlegada"] else 0,
            )
            equipo.tokensSopa = int(fila.get("tokensSopa") or 0)
            equipo.tokensBubbleMap = int(fila.get("tokensBubbleMap") or 0)
            equipo.tokensLego = int(fila.get("tokensLego") or 0)
            equipo.tokensPitchCreacion = int(fila.get("tokensPitchCreacion") or 0)
            equipo.tokensNegociacion = int(fila.get("tokensNegociacion") or 0)
            equipo.subioImagenLego = fila.get("subioImagenLego", "0") == "1"
            equipo.imagenLego = fila.get("imagenLego", "")
            equipo.mensajesLego = int(fila.get("mensajesLego") or 0)
            equipo.tipoMensajeLego = fila.get("tipoMensajeLego", "")
            equipo.nombreProductoPitch = fila.get("nombreProductoPitch", "")
            equipo.finalizoPitchCreacion = fila.get("finalizoPitchCreacion", "0") == "1"
            equipo.tiempoPitchCreacionSegundos = (
                int(fila["tiempoPitchCreacionSegundos"])
                if fila.get("tiempoPitchCreacionSegundos")
                else None
            )
            equipo.ordenExposicion = int(fila["ordenExposicion"]) if fila.get("ordenExposicion") else None
            equipo.promedioEvaluacionRecibida = (
                float(fila["promedioEvaluacionRecibida"]) if fila.get("promedioEvaluacionRecibida") else 0
            )
            equipo.evaluacionesRecibidas = int(fila.get("evaluacionesRecibidas") or 0)
            equipos[equipo.nombreEquipo] = equipo
    return equipos


def aplicarRankingGeneral(equiposEtapa: list[Equipo], rankingGeneral: dict[str, Equipo]) -> None:
    for equipo in equiposEtapa:
        acumulado = rankingGeneral.get(equipo.nombreEquipo)
        if acumulado is None:
            continue
        # Solo se importan tokens acumulados. Las metricas propias de la etapa
        # se mantienen desde el CSV simulado o desde la jugada actual.
        equipo.tokensEmpatia = acumulado.tokensEmpatia
        equipo.tokensCreatividad = acumulado.tokensCreatividad
        equipo.tokensEvaluacion = acumulado.tokensEvaluacion
        equipo.tokensSopa = acumulado.tokensSopa
        equipo.tokensBubbleMap = acumulado.tokensBubbleMap
        equipo.tokensLego = acumulado.tokensLego
        equipo.tokensPitchCreacion = acumulado.tokensPitchCreacion
        equipo.tokensNegociacion = acumulado.tokensNegociacion
        equipo.ordenLlegada = acumulado.ordenLlegada or equipo.ordenLlegada


def aplicarRankingGeneralParaSopa(equiposEtapa: list[Equipo], rankingGeneral: dict[str, Equipo]) -> None:
    aplicarRankingGeneral(equiposEtapa, rankingGeneral)
    for equipo in equiposEtapa:
        # La etapa se recalcula; se descuenta su aporte anterior para no duplicarlo.
        equipo.tokensEmpatia -= equipo.tokensSopa
        equipo.tokensSopa = 0


def aplicarRankingGeneralParaBubbleMap(equiposEtapa: list[Equipo], rankingGeneral: dict[str, Equipo]) -> None:
    aplicarRankingGeneral(equiposEtapa, rankingGeneral)
    for equipo in equiposEtapa:
        # La etapa se recalcula; se descuenta su aporte anterior para no duplicarlo.
        equipo.tokensEmpatia -= equipo.tokensBubbleMap
        equipo.tokensBubbleMap = 0


def aplicarRankingGeneralParaLego(equiposEtapa: list[Equipo], rankingGeneral: dict[str, Equipo]) -> None:
    aplicarRankingGeneral(equiposEtapa, rankingGeneral)
    for equipo in equiposEtapa:
        # La etapa se recalcula; se descuenta su aporte anterior para no duplicarlo.
        equipo.tokensCreatividad -= equipo.tokensLego
        equipo.tokensLego = 0
        equipo.subioImagenLego = False
        equipo.imagenLego = ""
        equipo.mensajesLego = 0
        equipo.tipoMensajeLego = ""


def aplicarRankingGeneralParaPitchCreacion(equiposEtapa: list[Equipo], rankingGeneral: dict[str, Equipo]) -> None:
    aplicarRankingGeneral(equiposEtapa, rankingGeneral)
    for equipo in equiposEtapa:
        # La etapa se recalcula; se descuenta su aporte anterior para no duplicarlo.
        equipo.tokensCreatividad -= equipo.tokensPitchCreacion
        equipo.tokensPitchCreacion = 0
        equipo.nombreProductoPitch = ""
        equipo.desafioEmpatiaPitch = ""
        equipo.creatividadPitch = ""
        equipo.cierrePitch = ""
        equipo.finalizoPitchCreacion = False
        equipo.tiempoPitchCreacionSegundos = None


def aplicarRankingGeneralParaNegociacion(equiposEtapa: list[Equipo], rankingGeneral: dict[str, Equipo]) -> None:
    aplicarRankingGeneral(equiposEtapa, rankingGeneral)
    for equipo in equiposEtapa:
        equipo.tokensEvaluacion -= equipo.tokensNegociacion
        equipo.tokensNegociacion = 0
        equipo.ordenExposicion = None
        equipo.promedioEvaluacionRecibida = 0
        equipo.evaluacionesRecibidas = 0


def actualizarGeneralConSopa(rankingGeneral: dict[str, Equipo], equiposEtapa: list[Equipo]) -> list[Equipo]:
    for equipoEtapa in equiposEtapa:
        equipoGeneral = rankingGeneral.setdefault(equipoEtapa.nombreEquipo, Equipo(equipoEtapa.nombreEquipo))
        diferenciaSopa = equipoEtapa.tokensSopa - equipoGeneral.tokensSopa
        equipoGeneral.tokensEmpatia += diferenciaSopa
        equipoGeneral.tokensSopa = equipoEtapa.tokensSopa
        equipoGeneral.tiempoSopaSegundos = equipoEtapa.tiempoSopaSegundos
        equipoGeneral.porcentajeSopa = equipoEtapa.porcentajeSopa
        equipoGeneral.posicionSopa = equipoEtapa.posicionSopa
        equipoGeneral.bonusEspera = equipoEtapa.bonusEspera
        if not equipoGeneral.ordenLlegada:
            equipoGeneral.ordenLlegada = equipoEtapa.ordenLlegada
        equipoGeneral.tiempoGlobalSegundos = equipoEtapa.tiempoGlobalSegundos
    return list(rankingGeneral.values())


def actualizarGeneralConBubbleMap(rankingGeneral: dict[str, Equipo], equiposEtapa: list[Equipo]) -> list[Equipo]:
    for equipoEtapa in equiposEtapa:
        equipoGeneral = rankingGeneral.setdefault(equipoEtapa.nombreEquipo, Equipo(equipoEtapa.nombreEquipo))
        diferenciaBubble = equipoEtapa.tokensBubbleMap - equipoGeneral.tokensBubbleMap
        equipoGeneral.tokensEmpatia += diferenciaBubble
        equipoGeneral.tokensBubbleMap = equipoEtapa.tokensBubbleMap
        equipoGeneral.tiempoBubbleMapSegundos = equipoEtapa.tiempoBubbleMapSegundos
        equipoGeneral.finalizoBubbleMap = equipoEtapa.finalizoBubbleMap
        equipoGeneral.bonusEspera = equipoEtapa.bonusEspera
        if not equipoGeneral.ordenLlegada:
            equipoGeneral.ordenLlegada = equipoEtapa.ordenLlegada
        equipoGeneral.tiempoGlobalSegundos = equipoEtapa.tiempoGlobalSegundos
    return list(rankingGeneral.values())


def actualizarGeneralConLego(rankingGeneral: dict[str, Equipo], equiposEtapa: list[Equipo]) -> list[Equipo]:
    for equipoEtapa in equiposEtapa:
        equipoGeneral = rankingGeneral.setdefault(equipoEtapa.nombreEquipo, Equipo(equipoEtapa.nombreEquipo))
        diferenciaLego = equipoEtapa.tokensLego - equipoGeneral.tokensLego
        equipoGeneral.tokensCreatividad += diferenciaLego
        equipoGeneral.tokensLego = equipoEtapa.tokensLego
        equipoGeneral.subioImagenLego = equipoEtapa.subioImagenLego
        equipoGeneral.imagenLego = equipoEtapa.imagenLego
        equipoGeneral.mensajesLego = equipoEtapa.mensajesLego
        equipoGeneral.tipoMensajeLego = equipoEtapa.tipoMensajeLego
        if not equipoGeneral.ordenLlegada:
            equipoGeneral.ordenLlegada = equipoEtapa.ordenLlegada
        equipoGeneral.tiempoGlobalSegundos = equipoEtapa.tiempoGlobalSegundos
    return list(rankingGeneral.values())


def actualizarGeneralConPitchCreacion(rankingGeneral: dict[str, Equipo], equiposEtapa: list[Equipo]) -> list[Equipo]:
    for equipoEtapa in equiposEtapa:
        equipoGeneral = rankingGeneral.setdefault(equipoEtapa.nombreEquipo, Equipo(equipoEtapa.nombreEquipo))
        diferenciaPitch = equipoEtapa.tokensPitchCreacion - equipoGeneral.tokensPitchCreacion
        equipoGeneral.tokensCreatividad += diferenciaPitch
        equipoGeneral.tokensPitchCreacion = equipoEtapa.tokensPitchCreacion
        equipoGeneral.nombreProductoPitch = equipoEtapa.nombreProductoPitch
        equipoGeneral.desafioEmpatiaPitch = equipoEtapa.desafioEmpatiaPitch
        equipoGeneral.creatividadPitch = equipoEtapa.creatividadPitch
        equipoGeneral.cierrePitch = equipoEtapa.cierrePitch
        equipoGeneral.finalizoPitchCreacion = equipoEtapa.finalizoPitchCreacion
        equipoGeneral.tiempoPitchCreacionSegundos = equipoEtapa.tiempoPitchCreacionSegundos
        if not equipoGeneral.ordenLlegada:
            equipoGeneral.ordenLlegada = equipoEtapa.ordenLlegada
        equipoGeneral.tiempoGlobalSegundos = equipoEtapa.tiempoGlobalSegundos
    return list(rankingGeneral.values())


def actualizarGeneralConNegociacion(rankingGeneral: dict[str, Equipo], equiposEtapa: list[Equipo]) -> list[Equipo]:
    for equipoEtapa in equiposEtapa:
        equipoGeneral = rankingGeneral.setdefault(equipoEtapa.nombreEquipo, Equipo(equipoEtapa.nombreEquipo))
        diferenciaNegociacion = equipoEtapa.tokensNegociacion - equipoGeneral.tokensNegociacion
        equipoGeneral.tokensEvaluacion += diferenciaNegociacion
        equipoGeneral.tokensNegociacion = equipoEtapa.tokensNegociacion
        equipoGeneral.ordenExposicion = equipoEtapa.ordenExposicion
        equipoGeneral.promedioEvaluacionRecibida = equipoEtapa.promedioEvaluacionRecibida
        equipoGeneral.evaluacionesRecibidas = equipoEtapa.evaluacionesRecibidas
        if not equipoGeneral.ordenLlegada:
            equipoGeneral.ordenLlegada = equipoEtapa.ordenLlegada
        equipoGeneral.tiempoGlobalSegundos = equipoEtapa.tiempoGlobalSegundos
    return list(rankingGeneral.values())


def exportarRankingGeneral(rutaCsv: Path, equipos: list[Equipo]) -> None:
    rutaCsv.parent.mkdir(parents=True, exist_ok=True)
    ranking = ordenarRankingGlobalBubbleMap(equipos)
    with rutaCsv.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_RANKING_GENERAL)
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
                    "tokensSopa": equipo.tokensSopa,
                    "tokensBubbleMap": equipo.tokensBubbleMap,
                    "tokensLego": equipo.tokensLego,
                    "tokensPitchCreacion": equipo.tokensPitchCreacion,
                    "tokensNegociacion": equipo.tokensNegociacion,
                    "subioImagenLego": int(equipo.subioImagenLego),
                    "imagenLego": equipo.imagenLego,
                    "mensajesLego": equipo.mensajesLego,
                    "tipoMensajeLego": equipo.tipoMensajeLego,
                    "nombreProductoPitch": equipo.nombreProductoPitch,
                    "finalizoPitchCreacion": int(equipo.finalizoPitchCreacion),
                    "tiempoPitchCreacionSegundos": equipo.tiempoPitchCreacionSegundos,
                    "ordenExposicion": equipo.ordenExposicion,
                    "promedioEvaluacionRecibida": f"{equipo.promedioEvaluacionRecibida:.2f}",
                    "evaluacionesRecibidas": equipo.evaluacionesRecibidas,
                    "tiempoGlobalSegundos": equipo.tiempoGlobalSegundos,
                    "tiempoSopaSegundos": equipo.tiempoSopaSegundos,
                    "tiempoBubbleMapSegundos": equipo.tiempoBubbleMapSegundos,
                    "porcentajeSopa": f"{equipo.porcentajeSopa:.2f}",
                    "posicionSopa": equipo.posicionSopa,
                    "finalizoBubbleMap": int(equipo.finalizoBubbleMap),
                    "bonusEspera": equipo.bonusEspera,
                    "ordenLlegada": equipo.ordenLlegada,
                }
            )
