from __future__ import annotations

from dataclasses import dataclass

from competencia.equipo import Equipo


TOKENS_IMAGEN_LEGO = 3

MENSAJE_AYUDA_LEGO = (
    "¡Esten atentos! Trabajen en Equipo\n"
    "Envien a alguien de su equipo a la caja de legos\n"
    "Pueden escoger 1 pieza extra para su MVP"
)

MENSAJE_ADVERTENCIA_LEGO = (
    "¡Cuidado!\n"
    "¡Su equipo ha generado mucho valor!\n"
    "¡Los demas equipos recibiran ayuda!"
)


@dataclass
class PlanMensajesLego:
    tipoMensaje: str
    cantidadMensajes: int
    segundosProgramados: list[int]
    textoMensaje: str
    participacionEquipo: float


def calcularPlanMensajesLego(equipo: Equipo, equipos: list[Equipo], duracionEtapaSegundos: int) -> PlanMensajesLego:
    totalTokensSeccion = sum(equipoActual.tokensTotales for equipoActual in equipos)
    if totalTokensSeccion <= 0:
        return _crearPlanAyuda(1, duracionEtapaSegundos, 0)

    participacion = equipo.tokensTotales / totalTokensSeccion
    if participacion > 0.5:
        return PlanMensajesLego(
            tipoMensaje="advertencia",
            cantidadMensajes=1,
            segundosProgramados=[0],
            textoMensaje=MENSAJE_ADVERTENCIA_LEGO,
            participacionEquipo=participacion,
        )
    if participacion > 0.3:
        return _crearPlanAyuda(1, duracionEtapaSegundos, participacion)
    if participacion > 0.15:
        return _crearPlanAyuda(2, duracionEtapaSegundos, participacion)
    return _crearPlanAyuda(3, duracionEtapaSegundos, participacion)


def _crearPlanAyuda(cantidad: int, duracionEtapaSegundos: int, participacion: float) -> PlanMensajesLego:
    if cantidad == 1:
        segundos = [duracionEtapaSegundos // 2]
    elif cantidad == 2:
        segundos = [duracionEtapaSegundos // 3, (duracionEtapaSegundos * 2) // 3]
    else:
        segundos = [duracionEtapaSegundos // 4, duracionEtapaSegundos // 2, (duracionEtapaSegundos * 3) // 4]

    return PlanMensajesLego(
        tipoMensaje="ayuda",
        cantidadMensajes=cantidad,
        segundosProgramados=sorted(set(max(0, segundo) for segundo in segundos)),
        textoMensaje=MENSAJE_AYUDA_LEGO,
        participacionEquipo=participacion,
    )


def calcularTokensLego(subioImagen: bool) -> int:
    return TOKENS_IMAGEN_LEGO if subioImagen else 0
