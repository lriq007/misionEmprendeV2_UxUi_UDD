from __future__ import annotations

import argparse
import sys
from copy import copy
from pathlib import Path
from select import select
from time import sleep

from competencia.cronometro import formatearSegundos
from competencia.csvPitch import cargarPitchSimulado, exportarRankingPitch
from competencia.equipo import Equipo
from competencia.rankingGeneral import (
    aplicarRankingGeneralParaPitchCreacion,
    actualizarGeneralConPitchCreacion,
    cargarRankingGeneral,
    exportarRankingGeneral,
)
from competencia.sesionJuego import SesionJuego
from juegos.creacionPitch import CreacionPitch
from puntajes.ranking import imprimirRankingEstandar, ordenarRankingGlobalBubbleMap
from puntajes.reglaPuntajePitch import calcularTokensCreacionPitch


MENSAJE_ESPERA = (
    "Esperen que el tiempo acabe\n"
    "Parte de Emprender es jugartela toda\n"
    "En un solo momento"
)


def pedirEntradaConTiempo(mensaje: str, segundosDisponibles: int) -> tuple[str, bool]:
    if segundosDisponibles <= 0:
        return "", True
    print(mensaje, end="", flush=True)
    listo, _, _ = select([sys.stdin], [], [], segundosDisponibles)
    if not listo:
        print("\nTiempo agotado. No se aceptan mas entradas.")
        return "", True
    entrada = sys.stdin.readline()
    if entrada == "":
        print("\nEntrada cerrada. Se detiene la captura.")
        return "", True
    return entrada.strip(), False


def imprimirMenuPitch(sesion: SesionJuego, pitch: CreacionPitch) -> None:
    print("\n=== CREACION DEL PITCH ===")
    print(
        f"Tiempo etapa: {sesion.cronometroEtapa.textoTranscurrido()} | "
        f"Restante: {formatearSegundos(sesion.segundosRestantesEtapa())}"
    )
    print("\nCompleta el guion por partes. Se guarda lo que alcances a escribir.")
    for indice, (_, titulo, valor, limite) in enumerate(pitch.camposOrdenados(), start=1):
        vista = valor if valor else "Sin texto."
        print(f"\n{indice}. {titulo} (max. {limite} caracteres)")
        print(f"   {vista}")
    print("\nOpciones:")
    print("1. Editar nombre del producto")
    print("2. Editar desafio y empatia")
    print("3. Editar creatividad")
    print("4. Editar cierre")
    print("5. Finalizar")


def editarCampo(sesion: SesionJuego, pitch: CreacionPitch, campo: str, titulo: str, limite: int) -> bool:
    print(f"\n{titulo} (max. {limite} caracteres)")
    texto, tiempoAgotado = pedirEntradaConTiempo("> ", sesion.segundosRestantesEtapa())
    if tiempoAgotado or sesion.etapaTerminada():
        return False
    _, fueRecortado = pitch.actualizarCampo(campo, texto)
    if fueRecortado:
        print(f"El texto excedia {limite} caracteres. Se guardo recortado.")
    else:
        print("Campo guardado.")
    return True


def imprimirGuionFinal(pitch: CreacionPitch) -> None:
    print("\n=== GUION FINAL DEL PITCH ===")
    print(pitch.construirGuion())


def esperarCierrePitch(sesion: SesionJuego) -> None:
    while not sesion.etapaTerminada():
        print("\n" + MENSAJE_ESPERA)
        sleep(min(10, sesion.segundosRestantesEtapa()))


def ejecutarCreacionPitch(sesion: SesionJuego, equipoUsuario: Equipo, pitch: CreacionPitch) -> None:
    campos = pitch.camposOrdenados()
    while not sesion.etapaTerminada():
        imprimirMenuPitch(sesion, pitch)
        opcion, tiempoAgotado = pedirEntradaConTiempo("Selecciona una opcion: ", sesion.segundosRestantesEtapa())
        if tiempoAgotado or sesion.etapaTerminada():
            break
        if opcion in {"1", "2", "3", "4"}:
            campo, titulo, _, limite = campos[int(opcion) - 1]
            editarCampo(sesion, pitch, campo, titulo, limite)
        elif opcion == "5":
            equipoUsuario.finalizoPitchCreacion = True
            equipoUsuario.tiempoPitchCreacionSegundos = sesion.cronometroEtapa.segundosTranscurridos()
            imprimirGuionFinal(pitch)
            esperarCierrePitch(sesion)
            return
        else:
            print("Opcion no valida.")

    print("\nTiempo agotado. Se guarda lo escrito hasta ahora.")
    imprimirGuionFinal(pitch)


def aplicarPitchAEquipo(equipo: Equipo, pitch: CreacionPitch) -> None:
    equipo.nombreProductoPitch = pitch.nombreProducto
    equipo.desafioEmpatiaPitch = pitch.desafioEmpatia
    equipo.creatividadPitch = pitch.creatividad
    equipo.cierrePitch = pitch.cierre
    equipo.sumarTokensPitchCreacion(calcularTokensCreacionPitch(pitch))


def aplicarPitchesSimulados(equipos: list[Equipo], pitches: dict[str, Equipo]) -> None:
    for equipo in equipos:
        simulado = pitches.get(equipo.nombreEquipo)
        if simulado is None:
            continue
        equipo.nombreProductoPitch = simulado.nombreProductoPitch
        equipo.desafioEmpatiaPitch = simulado.desafioEmpatiaPitch
        equipo.creatividadPitch = simulado.creatividadPitch
        equipo.cierrePitch = simulado.cierrePitch
        equipo.finalizoPitchCreacion = simulado.finalizoPitchCreacion
        equipo.tiempoPitchCreacionSegundos = simulado.tiempoPitchCreacionSegundos
        equipo.sumarTokensPitchCreacion(simulado.tokensPitchCreacion)


def crearArgumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una sesion demo de creacion del pitch.")
    parser.add_argument("--duracion", type=int, default=90, help="Duracion de la etapa en segundos.")
    parser.add_argument(
        "--mostrar-ranking",
        type=int,
        default=15,
        help="Segundos que se muestra el ranking final. Por defecto: 15.",
    )
    return parser.parse_args()


def ejecutarEtapaPitchCreacion(
    raiz: Path,
    rankingGeneral: dict[str, Equipo] | None = None,
    duracion: int = 90,
    mostrarRanking: int = 15,
    sesion: SesionJuego | None = None,
) -> list[Equipo]:
    rutaSesion = raiz / "data" / "equiposSesion.csv"
    rutaSimulados = raiz / "data" / "equiposSimuladosPitch.csv"
    rutaRankingGeneral = raiz / "output" / "RankingGeneral.csv"
    rutaRankingPitch = raiz / "output" / "RankingPitchCreacion.csv"

    if rankingGeneral is None:
        rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)
    equipos = [copy(equipo) for equipo in rankingGeneral.values()]
    aplicarRankingGeneralParaPitchCreacion(equipos, rankingGeneral)
    pitchesSimulados = cargarPitchSimulado(rutaSimulados)
    aplicarPitchesSimulados(equipos, pitchesSimulados)

    equipoUsuario = next((equipo for equipo in equipos if equipo.nombreEquipo == "Equipo Usuario"), None)
    if equipoUsuario is None:
        equipoUsuario = Equipo("Equipo Usuario", ordenLlegada=99)
        equipos.append(equipoUsuario)
    # El usuario real reemplaza su pitch simulado en cada ejecucion.
    equipoUsuario.tokensCreatividad -= equipoUsuario.tokensPitchCreacion
    equipoUsuario.tokensPitchCreacion = 0
    equipoUsuario.nombreProductoPitch = ""
    equipoUsuario.desafioEmpatiaPitch = ""
    equipoUsuario.creatividadPitch = ""
    equipoUsuario.cierrePitch = ""
    equipoUsuario.finalizoPitchCreacion = False
    equipoUsuario.tiempoPitchCreacionSegundos = None

    sesionCompartida = sesion is not None
    if sesion is None:
        sesion = SesionJuego(
            nombreSesion="Sesion demo creacion pitch",
            duracionEtapaSegundos=duracion,
            equipos=equipos,
        )
        sesion.iniciarSesion()
    else:
        sesion.duracionEtapaSegundos = duracion
        sesion.equipos = equipos
    pitch = CreacionPitch()

    print("=== SESION CREACION PITCH INICIADA ===")
    print(f"Duracion etapa demo: {duracion} segundos.")
    sesion.iniciarEtapa()

    ejecutarCreacionPitch(sesion, equipoUsuario, pitch)
    if sesionCompartida:
        sesion.finalizarEtapa()
        sesion.registrarTiempoGlobal()
    else:
        sesion.finalizarSesion()
    aplicarPitchAEquipo(equipoUsuario, pitch)

    rankingFinal = ordenarRankingGlobalBubbleMap(equipos)
    imprimirRankingEstandar(rankingFinal, equipoUsuario.nombreEquipo)
    exportarRankingPitch(rutaRankingPitch, rankingFinal)
    equiposGenerales = actualizarGeneralConPitchCreacion(rankingGeneral, equipos)
    exportarRankingGeneral(rutaRankingGeneral, equiposGenerales)

    print(f"\nRanking Pitch exportado en: {rutaRankingPitch}")
    print(f"Ranking general actualizado en: {rutaRankingGeneral}")
    if mostrarRanking > 0:
        print(f"\nEl ranking se mostrara durante {mostrarRanking} segundos.")
        sleep(mostrarRanking)
    return equiposGenerales


def main() -> None:
    argumentos = crearArgumentos()
    raiz = Path(__file__).resolve().parents[1]
    ejecutarEtapaPitchCreacion(
        raiz=raiz,
        duracion=argumentos.duracion,
        mostrarRanking=argumentos.mostrar_ranking,
    )


if __name__ == "__main__":
    main()
