from __future__ import annotations

import argparse
from pathlib import Path

from competencia.rankingGeneral import cargarRankingGeneral, exportarRankingGeneral
from competencia.sesionJuego import SesionJuego
from cli.ejecutarSesionBubbleMap import ejecutarEtapaBubbleMap
from cli.ejecutarSesionLego import ejecutarEtapaLego
from cli.ejecutarSesionNegociacion import ejecutarEtapaNegociacion
from cli.ejecutarSesionPitchCreacion import ejecutarEtapaPitchCreacion
from cli.ejecutarSesionSopa import ejecutarEtapaSopa
from puntajes.ranking import imprimirRankingEstandar, ordenarRankingGlobalBubbleMap


def crearArgumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta la sesion completa de logica de juegos.")
    parser.add_argument("--duracion-sopa", type=int, default=120, help="Duracion de sopa de letras en segundos.")
    parser.add_argument("--duracion-bubble", type=int, default=120, help="Duracion de Bubble Map en segundos.")
    parser.add_argument("--duracion-lego", type=int, default=120, help="Duracion de LEGO MVP en segundos.")
    parser.add_argument("--duracion-pitch", type=int, default=90, help="Duracion de creacion del pitch en segundos.")
    parser.add_argument("--duracion-exposicion", type=int, default=30, help="Duracion de cada exposicion.")
    parser.add_argument(
        "--tolerancia-oculta",
        type=int,
        default=6,
        help="Segundos ocultos despues de la exposicion propia.",
    )
    parser.add_argument("--semilla-negociacion", type=int, default=7, help="Semilla para orden de exposicion.")
    parser.add_argument(
        "--mostrar-ranking",
        type=int,
        default=0,
        help="Segundos que se mantiene visible cada ranking parcial. Por defecto: 0.",
    )
    return parser.parse_args()


def imprimirSeparadorEtapa(nombreEtapa: str) -> None:
    print("\n" + "=" * 72)
    print(f"INICIO ETAPA: {nombreEtapa}")
    print("=" * 72)


def main() -> None:
    argumentos = crearArgumentos()
    raiz = Path(__file__).resolve().parents[1]
    rutaSesion = raiz / "data" / "equiposSesion.csv"
    rutaRankingGeneral = raiz / "output" / "RankingGeneral.csv"
    rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)

    sesion = SesionJuego(
        nombreSesion="Sesion completa logica de juegos",
        duracionEtapaSegundos=argumentos.duracion_sopa,
        equipos=[],
    )

    print("=== SESION COMPLETA INICIADA ===")
    print("Cronometro global iniciado una sola vez para todas las etapas.")
    sesion.iniciarSesion()

    imprimirSeparadorEtapa("Sopa de letras")
    ejecutarEtapaSopa(
        raiz=raiz,
        rankingGeneral=rankingGeneral,
        duracion=argumentos.duracion_sopa,
        mostrarRanking=argumentos.mostrar_ranking,
        sesion=sesion,
    )

    imprimirSeparadorEtapa("Bubble Map")
    ejecutarEtapaBubbleMap(
        raiz=raiz,
        rankingGeneral=rankingGeneral,
        duracion=argumentos.duracion_bubble,
        mostrarRanking=argumentos.mostrar_ranking,
        sesion=sesion,
    )

    imprimirSeparadorEtapa("LEGO MVP")
    ejecutarEtapaLego(
        raiz=raiz,
        rankingGeneral=rankingGeneral,
        duracion=argumentos.duracion_lego,
        mostrarRanking=argumentos.mostrar_ranking,
        sesion=sesion,
    )

    imprimirSeparadorEtapa("Creacion del Pitch")
    ejecutarEtapaPitchCreacion(
        raiz=raiz,
        rankingGeneral=rankingGeneral,
        duracion=argumentos.duracion_pitch,
        mostrarRanking=argumentos.mostrar_ranking,
        sesion=sesion,
    )

    imprimirSeparadorEtapa("Negociacion")
    ejecutarEtapaNegociacion(
        raiz=raiz,
        rankingGeneral=rankingGeneral,
        duracionExposicion=argumentos.duracion_exposicion,
        toleranciaOculta=argumentos.tolerancia_oculta,
        semilla=argumentos.semilla_negociacion,
        mostrarRanking=argumentos.mostrar_ranking,
        sesion=sesion,
    )

    sesion.finalizarSesion()
    tiempoGlobal = sesion.cronometroGlobal.segundosTranscurridos()
    for equipo in rankingGeneral.values():
        equipo.tiempoGlobalSegundos = tiempoGlobal

    equiposFinales = list(rankingGeneral.values())
    rankingFinal = ordenarRankingGlobalBubbleMap(equiposFinales)
    print("\n=== RANKING FINAL SESION COMPLETA ===")
    imprimirRankingEstandar(rankingFinal, "Equipo Usuario")
    exportarRankingGeneral(rutaRankingGeneral, equiposFinales)
    print(f"\nTiempo global real: {tiempoGlobal} segundos.")
    print(f"Ranking general actualizado en: {rutaRankingGeneral}")


if __name__ == "__main__":
    main()
