from __future__ import annotations

from dataclasses import dataclass, field

from competencia.cronometro import Cronometro
from competencia.equipo import Equipo


@dataclass
class SesionJuego:
    nombreSesion: str
    duracionEtapaSegundos: int
    equipos: list[Equipo] = field(default_factory=list)
    cronometroGlobal: Cronometro = field(default_factory=lambda: Cronometro("global"))
    cronometroEtapa: Cronometro = field(default_factory=lambda: Cronometro("etapa"))

    def iniciarSesion(self) -> None:
        self.cronometroGlobal.iniciar()

    def iniciarEtapa(self) -> None:
        self.cronometroEtapa.iniciar()

    def finalizarEtapa(self) -> None:
        self.cronometroEtapa.detener()

    def registrarTiempoGlobal(self) -> None:
        tiempoGlobal = self.cronometroGlobal.segundosTranscurridos()
        for equipo in self.equipos:
            equipo.tiempoGlobalSegundos = tiempoGlobal

    def finalizarSesion(self) -> None:
        if self.cronometroEtapa.inicio is not None and self.cronometroEtapa.fin is None:
            self.finalizarEtapa()
        self.cronometroGlobal.detener()
        self.registrarTiempoGlobal()

    def agregarEquipo(self, equipo: Equipo) -> None:
        self.equipos.append(equipo)

    def segundosRestantesEtapa(self) -> int:
        usados = self.cronometroEtapa.segundosTranscurridos()
        return max(0, self.duracionEtapaSegundos - usados)

    def etapaTerminada(self) -> bool:
        return self.segundosRestantesEtapa() <= 0
