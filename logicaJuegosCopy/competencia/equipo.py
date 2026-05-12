from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Equipo:
    nombreEquipo: str
    tokensEmpatia: int = 0
    tokensCreatividad: int = 0
    tokensEvaluacion: int = 0
    tiempoGlobalSegundos: int | None = None
    tiempoSopaSegundos: int | None = None
    porcentajeSopa: float = 0
    bonusEspera: int = 0
    posicionSopa: int | None = None
    tokensSopa: int = 0
    ordenLlegada: int = 0
    tiempoBubbleMapSegundos: int | None = None
    finalizoBubbleMap: bool = False
    preguntasCompletas: int = 0
    preguntasDetalleIdeal: int = 0
    preguntasDesarrolladas: int = 0
    preguntasSuperficiales: int = 0
    apendicesBasura: int = 0
    apendicesExcesivos: int = 0
    puntajeContenidoBubbleMap: int = 0
    tokensBubbleMap: int = 0
    bonusExcelenciaVelocidad: int = 0
    penalizacionBajaProfundidad: int = 0
    penalizacionCalidadDeficiente: int = 0
    penalizacionExceso: int = 0
    tokensLego: int = 0
    subioImagenLego: bool = False
    imagenLego: str = ""
    mensajesLego: int = 0
    tipoMensajeLego: str = ""
    tokensPitchCreacion: int = 0
    nombreProductoPitch: str = ""
    desafioEmpatiaPitch: str = ""
    creatividadPitch: str = ""
    cierrePitch: str = ""
    finalizoPitchCreacion: bool = False
    tiempoPitchCreacionSegundos: int | None = None
    tokensNegociacion: int = 0
    ordenExposicion: int | None = None
    promedioEvaluacionRecibida: float = 0
    evaluacionesRecibidas: int = 0

    @property
    def tokensTotales(self) -> int:
        return self.tokensEmpatia + self.tokensCreatividad + self.tokensEvaluacion

    def sumarTokensEmpatia(self, cantidad: int) -> None:
        self.tokensEmpatia += cantidad

    def sumarTokensSopa(self, cantidad: int) -> None:
        self.tokensSopa += cantidad
        self.tokensEmpatia += cantidad

    def aplicarBonusEspera(self, cantidad: int) -> None:
        # El bonus de espera se acumula en empatia para simular la etapa 1 actual.
        self.bonusEspera += cantidad
        self.tokensEmpatia += cantidad

    def registrarBonusEspera(self, cantidad: int) -> None:
        # Registra el bonus pendiente; se suma al cerrar oficialmente la etapa.
        self.bonusEspera = cantidad

    def sumarTokensBubbleMap(self, cantidad: int) -> None:
        self.tokensBubbleMap += cantidad
        self.tokensEmpatia += cantidad

    def sumarTokensLego(self, cantidad: int) -> None:
        self.tokensLego += cantidad
        self.tokensCreatividad += cantidad

    def sumarTokensPitchCreacion(self, cantidad: int) -> None:
        self.tokensPitchCreacion += cantidad
        self.tokensCreatividad += cantidad

    def sumarTokensNegociacion(self, cantidad: int) -> None:
        self.tokensNegociacion += cantidad
        self.tokensEvaluacion += cantidad
