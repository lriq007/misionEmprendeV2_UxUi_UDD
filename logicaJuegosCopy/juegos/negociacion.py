from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvaluacionNegociacion:
    evaluador: str
    evaluado: str
    puntajeEquipo: int
    puntajeEmpatia: int
    puntajeCreatividad: int
    puntajeComunicacion: int
    comentario: str = ""

    def puntajePromedioVisible(self) -> float:
        return (
            self.puntajeEquipo
            + self.puntajeEmpatia
            + self.puntajeCreatividad
            + self.puntajeComunicacion
        ) / 4


CRITERIOS_NEGOCIACION = {
    "equipo": "Se evalua trabajo conjunto, coordinacion y participacion equilibrada.",
    "empatia": "Se evalua conexion de la solucion con el dolor identificado en Bubble Map.",
    "creatividad": "Se evalua si la solucion LEGO es innovadora, tecnologica y original.",
    "comunicacion": "Se evalua claridad, entusiasmo y capacidad persuasiva.",
}
