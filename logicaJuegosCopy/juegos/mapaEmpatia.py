from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PreguntaMapaEmpatia:
    clave: str
    titulo: str
    texto: str
    apendices: list[str] = field(default_factory=list)

    def agregarApendice(self, textoApendice: str) -> None:
        textoLimpio = textoApendice.strip()
        if textoLimpio:
            self.apendices.append(textoLimpio)


@dataclass
class MapaEmpatia:
    preguntas: dict[str, PreguntaMapaEmpatia] = field(default_factory=dict)

    @classmethod
    def crearBase(cls) -> "MapaEmpatia":
        preguntas = {
            "gustos": PreguntaMapaEmpatia(
                "gustos",
                "Gustos y disgustos",
                "Que le gusta y que no le gusta?",
            ),
            "problemas": PreguntaMapaEmpatia(
                "problemas",
                "Problemas",
                "Que obstaculos esta enfrentando?",
            ),
            "miedos": PreguntaMapaEmpatia(
                "miedos",
                "Miedos",
                "Que siente respecto a lo que le esta pasando?",
            ),
            "contexto": PreguntaMapaEmpatia(
                "contexto",
                "Contexto",
                "Que le dicen los demas?",
            ),
            "hobbies": PreguntaMapaEmpatia(
                "hobbies",
                "Hobbies",
                "Cuales son sus hobbies?",
            ),
        }
        return cls(preguntas)

    def obtenerPreguntasOrdenadas(self) -> list[PreguntaMapaEmpatia]:
        orden = ["gustos", "problemas", "miedos", "contexto", "hobbies"]
        return [self.preguntas[clave] for clave in orden]

    def imprimirResumenRespuestas(self) -> None:
        for indice, pregunta in enumerate(self.obtenerPreguntasOrdenadas(), start=1):
            print(f"\n{indice}. {pregunta.titulo}")
            if not pregunta.apendices:
                print("   Sin respuestas todavia.")
                continue
            for indiceApendice, apendice in enumerate(pregunta.apendices, start=1):
                print(f"   {indiceApendice}. {apendice}")
