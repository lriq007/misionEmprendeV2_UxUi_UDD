from __future__ import annotations

from dataclasses import dataclass, field
from random import choice, randint, shuffle
from string import ascii_uppercase


@dataclass
class JuegoSopaLetras:
    palabras: list[str]
    filas: int = 15
    columnas: int = 15
    tablero: list[list[str]] = field(default_factory=list)
    ubicaciones: dict[str, list[tuple[int, int]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 8 <= len(self.palabras) <= 15:
            raise ValueError("La sopa de letras debe tener entre 8 y 15 palabras.")
        self.palabras = [palabra.upper().strip() for palabra in self.palabras]

    def generarTablero(self) -> None:
        self.tablero = [["" for _ in range(self.columnas)] for _ in range(self.filas)]
        self.ubicaciones = {}
        for palabra in sorted(self.palabras, key=len, reverse=True):
            self._ubicarPalabra(palabra)
        self._rellenarVacios()

    def _ubicarPalabra(self, palabra: str) -> None:
        direcciones = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        for _ in range(300):
            deltaFila, deltaColumna = choice(direcciones)
            fila = randint(0, self.filas - 1)
            columna = randint(0, self.columnas - 1)
            posiciones = self._calcularPosiciones(palabra, fila, columna, deltaFila, deltaColumna)
            if posiciones and self._puedeUbicar(palabra, posiciones):
                for letra, (filaActual, columnaActual) in zip(palabra, posiciones):
                    self.tablero[filaActual][columnaActual] = letra
                self.ubicaciones[palabra] = posiciones
                return
        raise ValueError(f"No se pudo ubicar la palabra {palabra}.")

    def _calcularPosiciones(
        self,
        palabra: str,
        fila: int,
        columna: int,
        deltaFila: int,
        deltaColumna: int,
    ) -> list[tuple[int, int]] | None:
        posiciones = []
        for indice in range(len(palabra)):
            filaActual = fila + deltaFila * indice
            columnaActual = columna + deltaColumna * indice
            if not (0 <= filaActual < self.filas and 0 <= columnaActual < self.columnas):
                return None
            posiciones.append((filaActual, columnaActual))
        return posiciones

    def _puedeUbicar(self, palabra: str, posiciones: list[tuple[int, int]]) -> bool:
        for letra, (fila, columna) in zip(palabra, posiciones):
            celda = self.tablero[fila][columna]
            if celda not in ("", letra):
                return False
        return True

    def _rellenarVacios(self) -> None:
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna] == "":
                    self.tablero[fila][columna] = choice(ascii_uppercase)

    def validarPalabra(self, palabra: str) -> bool:
        return palabra.upper().strip() in self.ubicaciones

    def imprimirTablero(self) -> None:
        print("\nSopa de letras:")
        for fila in self.tablero:
            print(" ".join(fila))

    def imprimirPistas(self, encontradas: set[str]) -> None:
        pendientes = [palabra for palabra in self.palabras if palabra not in encontradas]
        shuffle(pendientes)
        print("\nPalabras pendientes:")
        for palabra in pendientes:
            print(f"- {palabra}")
