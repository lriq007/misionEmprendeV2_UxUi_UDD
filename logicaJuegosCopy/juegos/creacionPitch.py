from __future__ import annotations

from dataclasses import dataclass


LIMITES_CARACTERES_PITCH = {
    "nombreProducto": 40,
    "desafioEmpatia": 220,
    "creatividad": 220,
    "cierre": 160,
}


@dataclass
class CreacionPitch:
    nombreProducto: str = ""
    desafioEmpatia: str = ""
    creatividad: str = ""
    cierre: str = ""

    def actualizarCampo(self, campo: str, texto: str) -> tuple[str, bool]:
        limite = LIMITES_CARACTERES_PITCH[campo]
        textoLimpio = texto.strip()
        fueRecortado = len(textoLimpio) > limite
        textoFinal = textoLimpio[:limite]
        setattr(self, campo, textoFinal)
        return textoFinal, fueRecortado

    def camposOrdenados(self) -> list[tuple[str, str, str, int]]:
        return [
            ("nombreProducto", "Nombre del producto", self.nombreProducto, LIMITES_CARACTERES_PITCH["nombreProducto"]),
            (
                "desafioEmpatia",
                "Desafio y empatia",
                self.desafioEmpatia,
                LIMITES_CARACTERES_PITCH["desafioEmpatia"],
            ),
            ("creatividad", "Creatividad", self.creatividad, LIMITES_CARACTERES_PITCH["creatividad"]),
            ("cierre", "Cierre", self.cierre, LIMITES_CARACTERES_PITCH["cierre"]),
        ]

    def construirGuion(self) -> str:
        return (
            f"Producto:\n{self.nombreProducto}\n\n"
            f"Desafio y empatia:\n{self.desafioEmpatia}\n\n"
            f"Creatividad:\n{self.creatividad}\n\n"
            f"Cierre:\n{self.cierre}"
        )
