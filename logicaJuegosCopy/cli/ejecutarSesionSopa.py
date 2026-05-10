from __future__ import annotations

import argparse
import sys
from select import select
from pathlib import Path
from time import sleep

from competencia.cronometro import formatearSegundos
from competencia.csvRanking import cargarEquiposSimulados, exportarRanking
from competencia.equipo import Equipo
from competencia.rankingGeneral import (
    aplicarRankingGeneralParaSopa,
    actualizarGeneralConSopa,
    cargarRankingGeneral,
    exportarRankingGeneral,
)
from competencia.sesionJuego import SesionJuego
from espera.buscaminasEspera import BuscaminasEspera
from juegos.juegoSopaLetras import JuegoSopaLetras
from puntajes.ranking import imprimirRanking, obtenerPosicionEquipo, ordenarRankingGlobal
from puntajes.reglaPuntajeSopaLetras import asignarTokensSopa, ordenarRankingSopa


PALABRAS_SOPA = [
    "cliente",
    "problema",
    "idea",
    "prototipo",
    "empatia",
    "equipo",
    "pitch",
    "valor",
]


def pedirEntrada(mensaje: str) -> str:
    try:
        return input(mensaje).strip()
    except EOFError:
        return ""


def pedirEntradaConTiempo(mensaje: str, segundosDisponibles: int) -> tuple[str, bool]:
    if segundosDisponibles <= 0:
        return "", True

    print(mensaje, end="", flush=True)
    listo, _, _ = select([sys.stdin], [], [], segundosDisponibles)
    if not listo:
        print("\nTiempo agotado. No se aceptan mas jugadas.")
        return "", True

    entrada = sys.stdin.readline()
    if entrada == "":
        print("\nEntrada cerrada. Se detiene la captura de jugadas.")
        return "", True
    return entrada.strip(), False


def jugarSopa(
    sesion: SesionJuego,
    equipoUsuario: Equipo,
    juego: JuegoSopaLetras,
) -> set[str]:
    encontradas: set[str] = set()
    ordenLlegadaUsuario = 0

    while not sesion.etapaTerminada() and len(encontradas) < len(juego.palabras):
        print(
            f"\nTiempo global: {sesion.cronometroGlobal.textoTranscurrido()} | "
            f"Tiempo etapa: {sesion.cronometroEtapa.textoTranscurrido()} | "
            f"Restante: {formatearSegundos(sesion.segundosRestantesEtapa())}"
        )
        juego.imprimirPistas(encontradas)
        palabra, tiempoAgotado = pedirEntradaConTiempo(
            "Ingresa palabra encontrada ('salir' para cerrar prueba): ",
            sesion.segundosRestantesEtapa(),
        )

        if tiempoAgotado or sesion.etapaTerminada():
            break

        if palabra.lower() == "salir":
            break
        if not palabra:
            continue

        palabraNormalizada = palabra.upper()
        if palabraNormalizada in encontradas:
            print("Esa palabra ya fue registrada.")
            continue
        if juego.validarPalabra(palabraNormalizada):
            encontradas.add(palabraNormalizada)
            ordenLlegadaUsuario += 1
            porcentaje = (len(encontradas) / len(juego.palabras)) * 100
            equipoUsuario.porcentajeSopa = porcentaje
            equipoUsuario.ordenLlegada = 99 + ordenLlegadaUsuario
            print(f"Correcto. Progreso: {len(encontradas)}/{len(juego.palabras)} ({porcentaje:.0f}%).")
        else:
            print("Palabra no valida para esta sopa.")

    if len(encontradas) == len(juego.palabras):
        equipoUsuario.tiempoSopaSegundos = sesion.cronometroEtapa.segundosTranscurridos()
        equipoUsuario.porcentajeSopa = 100
        print(f"\nTerminaste la sopa en {formatearSegundos(equipoUsuario.tiempoSopaSegundos)}.")
    else:
        print("\nLa sopa quedo incompleta para el equipo en sesion.")

    return encontradas


def jugarBuscaminasSiCorresponde(sesion: SesionJuego, equipoUsuario: Equipo) -> None:
    if equipoUsuario.porcentajeSopa < 100 or sesion.etapaTerminada():
        return

    print("\n=== BUSCAMINAS DE ESPERA ===")
    print("Se habilita porque el equipo termino antes de cerrar la etapa.")
    print("Tablero dificil: 4x4 con 8 minas. Bonus maximo: 1 token.")
    buscaminas = BuscaminasEspera()
    buscaminas.generarTablero()

    while not sesion.etapaTerminada() and not buscaminas.juegoTerminado:
        print(f"\nTiempo restante etapa: {formatearSegundos(sesion.segundosRestantesEtapa())}")
        buscaminas.imprimirTableroVisible()
        entrada, tiempoAgotado = pedirEntradaConTiempo(
            "Abrir casilla fila,columna ('fin' para esperar cierre): ",
            sesion.segundosRestantesEtapa(),
        )
        if tiempoAgotado or sesion.etapaTerminada():
            break
        if entrada.lower() == "fin":
            break
        try:
            filaTexto, columnaTexto = entrada.split(",")
            fila = int(filaTexto.strip())
            columna = int(columnaTexto.strip())
        except ValueError:
            print("Formato invalido. Usa fila,columna. Ejemplo: 1,2")
            continue
        _, mensaje = buscaminas.abrirCasilla(fila, columna)
        print(mensaje)

    bonus = buscaminas.calcularBonus()
    equipoUsuario.registrarBonusEspera(bonus)
    print(f"Bonus de espera obtenido: {bonus} token.")


def esperarCierreEtapa(sesion: SesionJuego) -> None:
    while not sesion.etapaTerminada():
        print(f"Esperando cierre de etapa... restante {formatearSegundos(sesion.segundosRestantesEtapa())}")
        sleep(min(5, sesion.segundosRestantesEtapa()))


def crearArgumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una sesion demo de sopa de letras.")
    parser.add_argument(
        "--duracion",
        type=int,
        default=120,
        help="Duracion de la etapa en segundos. Por defecto: 120.",
    )
    return parser.parse_args()


def ejecutarEtapaSopa(
    raiz: Path,
    rankingGeneral: dict[str, Equipo] | None = None,
    duracion: int = 120,
    mostrarRanking: int = 0,
    sesion: SesionJuego | None = None,
) -> list[Equipo]:
    rutaSimulados = raiz / "data" / "equiposSimulados.csv"
    rutaSesion = raiz / "data" / "equiposSesion.csv"
    rutaRanking = raiz / "output" / "Ranking.csv"
    rutaRankingGeneral = raiz / "output" / "RankingGeneral.csv"

    equipoUsuario = Equipo(nombreEquipo="Equipo Usuario", ordenLlegada=99)
    equipos = cargarEquiposSimulados(rutaSimulados)
    equipos.append(equipoUsuario)
    if rankingGeneral is None:
        rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)
    aplicarRankingGeneralParaSopa(equipos, rankingGeneral)

    sesionCompartida = sesion is not None
    if sesion is None:
        sesion = SesionJuego(
            nombreSesion="Sesion demo sopa de letras",
            duracionEtapaSegundos=duracion,
            equipos=equipos,
        )
        sesion.iniciarSesion()
    else:
        sesion.duracionEtapaSegundos = duracion
        sesion.equipos = equipos
    juego = JuegoSopaLetras(PALABRAS_SOPA)
    juego.generarTablero()

    print("=== SESION INICIADA ===")
    print(f"Duracion etapa demo: {duracion} segundos.")
    sesion.iniciarEtapa()

    juego.imprimirTablero()
    jugarSopa(sesion, equipoUsuario, juego)

    rankingLlegada = ordenarRankingSopa(equipos)
    posicionInmediata = obtenerPosicionEquipo(rankingLlegada, equipoUsuario.nombreEquipo)
    print(f"Posicion inmediata estimada de sopa: {posicionInmediata}")

    jugarBuscaminasSiCorresponde(sesion, equipoUsuario)
    esperarCierreEtapa(sesion)

    print("\nTiempo agotado. Cerrando etapa...")
    if sesionCompartida:
        sesion.finalizarEtapa()
        sesion.registrarTiempoGlobal()
    else:
        sesion.finalizarSesion()
    asignarTokensSopa(equipos)

    rankingFinal = ordenarRankingGlobal(equipos)
    imprimirRanking(rankingFinal, equipoUsuario.nombreEquipo)
    exportarRanking(rutaRanking, rankingFinal)
    equiposGenerales = actualizarGeneralConSopa(rankingGeneral, equipos)
    exportarRankingGeneral(rutaRankingGeneral, equiposGenerales)
    print(f"\nRanking exportado en: {rutaRanking}")
    print(f"Ranking general actualizado en: {rutaRankingGeneral}")
    if mostrarRanking > 0:
        print(f"\nEl ranking se mostrara durante {mostrarRanking} segundos.")
        sleep(mostrarRanking)
    return equiposGenerales


def main() -> None:
    argumentos = crearArgumentos()
    raiz = Path(__file__).resolve().parents[1]
    ejecutarEtapaSopa(raiz=raiz, duracion=argumentos.duracion)


if __name__ == "__main__":
    main()
