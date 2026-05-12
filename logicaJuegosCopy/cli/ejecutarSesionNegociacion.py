from __future__ import annotations

import argparse
import random
from copy import copy
from pathlib import Path
from time import sleep

from competencia.csvNegociacion import (
    cargarEvaluacionesNegociacion,
    cargarPerfilesNegociacion,
    exportarRankingNegociacion,
)
from competencia.equipo import Equipo
from competencia.rankingGeneral import (
    aplicarRankingGeneralParaNegociacion,
    actualizarGeneralConNegociacion,
    cargarRankingGeneral,
    exportarRankingGeneral,
)
from competencia.sesionJuego import SesionJuego
from juegos.negociacion import CRITERIOS_NEGOCIACION, EvaluacionNegociacion
from puntajes.ranking import imprimirRankingEstandar, ordenarRankingGlobalBubbleMap
from puntajes.reglaPuntajeNegociacion import asignarTokensNegociacion


MENSAJE_ESPERA_EXPUESTO = (
    "Espera a que el resto termine\n"
    "Pronto sabremos\n"
    "El emprendimiento ganador"
)


def imprimirOrdenExposicion(equipos: list[Equipo], nombreEquipoActual: str) -> None:
    print("\n=== ORDEN DE EXPOSICION ===")
    for equipo in sorted(equipos, key=lambda item: item.ordenExposicion or 999):
        marca = " <== TU EQUIPO" if equipo.nombreEquipo == nombreEquipoActual else ""
        print(f"{equipo.ordenExposicion}. {equipo.nombreEquipo}{marca}")


def imprimirFichaEquipo(nombreEquipo: str, perfiles: dict[str, dict[str, str]]) -> None:
    perfil = perfiles.get(nombreEquipo, {})
    print("\n=== FICHA DEL EMPRENDIMIENTO ===")
    print(f"Equipo: {nombreEquipo}")
    print(f"Emprendimiento: {perfil.get('nombreEmprendimiento', '-')}")
    print(f"Producto: {perfil.get('nombreProducto', '-')}")
    print(f"Integrantes: {perfil.get('integrantes', '-')}")
    print(f"Imagen equipo: {perfil.get('imagenEquipo', '-')}")
    print(f"Imagen MVP: {perfil.get('imagenMvp', '-')}")


def ejecutarExposicionPropia(duracionSegundos: int, toleranciaOcultaSegundos: int) -> None:
    print("\n=== TU TURNO DE EXPONER ===")
    print(f"Temporizador pausado: {duracionSegundos} segundos.")
    input("Presiona Enter para iniciar la exposicion...")
    for restante in range(duracionSegundos, 0, -1):
        print(f"Tiempo restante exposicion: {restante:02d}s")
        sleep(1)
    print("\nTiempo oficial agotado.")
    if toleranciaOcultaSegundos > 0:
        sleep(toleranciaOcultaSegundos)
    print("\nEstan diciendo sobre su emprendimiento")


def imprimirVistaEvaluacion(equipoExpositor: str, perfiles: dict[str, dict[str, str]]) -> None:
    imprimirFichaEquipo(equipoExpositor, perfiles)
    print("\n=== EVALUACION DEL EQUIPO EXPOSITOR ===")
    print("Equipo:")
    print(CRITERIOS_NEGOCIACION["equipo"])
    print("\nEmpatia:")
    print(CRITERIOS_NEGOCIACION["empatia"])
    print("\nCreatividad:")
    print(CRITERIOS_NEGOCIACION["creatividad"])
    print("\nComunicacion:")
    print(CRITERIOS_NEGOCIACION["comunicacion"])
    print("\nEn esta demo, los puntajes se cargan desde CSV simulado.")


def filtrarAutoevaluaciones(evaluaciones: list[EvaluacionNegociacion]) -> list[EvaluacionNegociacion]:
    return [evaluacion for evaluacion in evaluaciones if evaluacion.evaluador != evaluacion.evaluado]


def crearArgumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una sesion demo de negociacion.")
    parser.add_argument("--duracion-exposicion", type=int, default=30, help="Duracion de cada exposicion.")
    parser.add_argument(
        "--tolerancia-oculta",
        type=int,
        default=6,
        help="Segundos ocultos antes de abrir evaluacion.",
    )
    parser.add_argument("--semilla", type=int, default=7, help="Semilla para orden aleatorio.")
    parser.add_argument(
        "--mostrar-ranking",
        type=int,
        default=15,
        help="Segundos que se muestra el ranking final. Por defecto: 15.",
    )
    return parser.parse_args()


def ejecutarEtapaNegociacion(
    raiz: Path,
    rankingGeneral: dict[str, Equipo] | None = None,
    duracionExposicion: int = 30,
    toleranciaOculta: int = 6,
    semilla: int = 7,
    mostrarRanking: int = 15,
    sesion: SesionJuego | None = None,
) -> list[Equipo]:
    rutaSesion = raiz / "data" / "equiposSesion.csv"
    rutaRankingGeneral = raiz / "output" / "RankingGeneral.csv"
    rutaPerfiles = raiz / "data" / "equiposNegociacion.csv"
    rutaEvaluaciones = raiz / "data" / "evaluacionesNegociacion.csv"
    rutaRankingNegociacion = raiz / "output" / "RankingNegociacion.csv"

    if rankingGeneral is None:
        rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)
    equipos = [copy(equipo) for equipo in rankingGeneral.values()]
    aplicarRankingGeneralParaNegociacion(equipos, rankingGeneral)
    perfiles = cargarPerfilesNegociacion(rutaPerfiles)
    evaluaciones = filtrarAutoevaluaciones(cargarEvaluacionesNegociacion(rutaEvaluaciones))

    random.Random(semilla).shuffle(equipos)
    for indice, equipo in enumerate(equipos, start=1):
        equipo.ordenExposicion = indice

    nombreEquipoActual = "Equipo Usuario"
    yaExpusoUsuario = False
    sesionCompartida = sesion is not None
    if sesion is None:
        sesion = SesionJuego(
            nombreSesion="Sesion demo negociacion",
            duracionEtapaSegundos=max(1, len(equipos) * (duracionExposicion + toleranciaOculta + 1)),
            equipos=equipos,
        )
        sesion.iniciarSesion()
    else:
        sesion.duracionEtapaSegundos = max(1, len(equipos) * (duracionExposicion + toleranciaOculta + 1))
        sesion.equipos = equipos

    print("=== SESION NEGOCIACION INICIADA ===")
    imprimirOrdenExposicion(equipos, nombreEquipoActual)
    sesion.iniciarEtapa()

    for equipoExpositor in sorted(equipos, key=lambda item: item.ordenExposicion or 999):
        print(f"\n--- Turno {equipoExpositor.ordenExposicion}: {equipoExpositor.nombreEquipo} ---")
        if equipoExpositor.nombreEquipo == nombreEquipoActual:
            ejecutarExposicionPropia(duracionExposicion, toleranciaOculta)
            yaExpusoUsuario = True
        elif yaExpusoUsuario:
            print("\n" + MENSAJE_ESPERA_EXPUESTO)
            sleep(1)
        else:
            imprimirVistaEvaluacion(equipoExpositor.nombreEquipo, perfiles)
            sleep(1)

    if sesionCompartida:
        sesion.finalizarEtapa()
        sesion.registrarTiempoGlobal()
    else:
        sesion.finalizarSesion()
    asignarTokensNegociacion(equipos, evaluaciones)

    rankingFinal = ordenarRankingGlobalBubbleMap(equipos)
    imprimirRankingEstandar(rankingFinal, nombreEquipoActual)
    exportarRankingNegociacion(rutaRankingNegociacion, rankingFinal)
    equiposGenerales = actualizarGeneralConNegociacion(rankingGeneral, equipos)
    exportarRankingGeneral(rutaRankingGeneral, equiposGenerales)

    print(f"\nRanking Negociacion exportado en: {rutaRankingNegociacion}")
    print(f"Ranking general actualizado en: {rutaRankingGeneral}")
    if mostrarRanking > 0:
        print(f"\nEl ranking se mostrara durante {mostrarRanking} segundos.")
        sleep(mostrarRanking)
    return equiposGenerales


def main() -> None:
    argumentos = crearArgumentos()
    raiz = Path(__file__).resolve().parents[1]
    ejecutarEtapaNegociacion(
        raiz=raiz,
        duracionExposicion=argumentos.duracion_exposicion,
        toleranciaOculta=argumentos.tolerancia_oculta,
        semilla=argumentos.semilla,
        mostrarRanking=argumentos.mostrar_ranking,
    )


if __name__ == "__main__":
    main()
