from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass
class Cronometro:
    nombre: str
    inicio: float | None = None
    fin: float | None = None

    def iniciar(self) -> None:
        # Usa monotonic para medir duraciones sin depender del reloj del sistema.
        self.inicio = monotonic()
        self.fin = None

    def detener(self) -> None:
        if self.inicio is None:
            raise ValueError(f"El cronometro {self.nombre} no ha iniciado.")
        self.fin = monotonic()

    def segundosTranscurridos(self) -> int:
        if self.inicio is None:
            return 0
        referencia = self.fin if self.fin is not None else monotonic()
        return int(referencia - self.inicio)

    def textoTranscurrido(self) -> str:
        segundos = self.segundosTranscurridos()
        minutos = segundos // 60
        restoSegundos = segundos % 60
        return f"{minutos:02d}:{restoSegundos:02d}"


def formatearSegundos(segundos: int | None) -> str:
    if segundos is None:
        return "-"
    minutos = segundos // 60
    restoSegundos = segundos % 60
    return f"{minutos:02d}:{restoSegundos:02d}"
