from __future__ import annotations

from dataclasses import dataclass, field
from random import sample


@dataclass
class BuscaminasEspera:
    filas: int = 4
    columnas: int = 4
    minas: int = 8
    bonusMaximo: int = 1
    minasUbicadas: set[tuple[int, int]] = field(default_factory=set)
    casillasAbiertas: set[tuple[int, int]] = field(default_factory=set)
    juegoTerminado: bool = False

    def generarTablero(self) -> None:
        posiciones = [(fila, columna) for fila in range(self.filas) for columna in range(self.columnas)]
        self.minasUbicadas = set(sample(posiciones, self.minas))

    def abrirCasilla(self, fila: int, columna: int) -> tuple[bool, str]:
        if self.juegoTerminado:
            return False, "El buscaminas ya termino."
        if not (0 <= fila < self.filas and 0 <= columna < self.columnas):
            return False, "Casilla fuera del tablero."
        posicion = (fila, columna)
        if posicion in self.minasUbicadas:
            self.juegoTerminado = True
            return False, "Pisaste una mina. Bonus obtenido: 0."
        self.casillasAbiertas.add(posicion)
        return True, "Casilla segura."

    def calcularBonus(self) -> int:
        # Dificil por diseno: basta poco avance para optar al bonus, pero hay muchas minas.
        casillasSeguras = (self.filas * self.columnas) - self.minas
        if casillasSeguras <= 0:
            return 0
        porcentajeSeguro = len(self.casillasAbiertas) / casillasSeguras
        return self.bonusMaximo if porcentajeSeguro >= 0.5 else 0

    def imprimirTableroVisible(self) -> None:
        print("\nBuscaminas:")
        print("   " + " ".join(str(columna) for columna in range(self.columnas)))
        for fila in range(self.filas):
            celdas = []
            for columna in range(self.columnas):
                celdas.append("O" if (fila, columna) in self.casillasAbiertas else ".")
            print(f"{fila}  " + " ".join(celdas))
