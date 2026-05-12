from __future__ import annotations

import argparse
import sys
from copy import copy
from pathlib import Path
from select import select
from time import sleep

from competencia.cronometro import formatearSegundos
from competencia.csvLego import cargarEntregaLegoSimulada, exportarRankingLego
from competencia.equipo import Equipo
from competencia.rankingGeneral import (
    aplicarRankingGeneralParaLego,
    actualizarGeneralConLego,
    cargarRankingGeneral,
    exportarRankingGeneral,
)
from competencia.sesionJuego import SesionJuego
from puntajes.ranking import imprimirRankingEstandar, ordenarRankingGlobalBubbleMap
from puntajes.reglaPuntajeLego import calcularPlanMensajesLego, calcularTokensLego


def pedirEntradaConTiempo(mensaje: str, segundosDisponibles: int) -> tuple[str, bool]:
    if segundosDisponibles <= 0:
        return "", True

    print(mensaje, end="", flush=True)
    listo, _, _ = select([sys.stdin], [], [], segundosDisponibles)
    if not listo:
        return "", True

    entrada = sys.stdin.readline()
    if entrada == "":
        print("\nEntrada cerrada. Se detiene la captura.")
        sleep(segundosDisponibles)
        return "", True
    return entrada.strip(), False


def imprimirMensajeLego(textoMensaje: str) -> None:
    print("\n=== MENSAJE DE ETAPA ===")
    print(textoMensaje)
    print("========================")


def imprimirEstadoEtapa(sesion: SesionJuego, equipo: Equipo) -> None:
    print("\n=== ETAPA LEGO MVP ===")
    print(
        f"Tiempo etapa: {sesion.cronometroEtapa.textoTranscurrido()} | "
        f"Restante: {formatearSegundos(sesion.segundosRestantesEtapa())}"
    )
    estadoImagen = equipo.imagenLego if equipo.subioImagenLego else "Sin imagen cargada."
    print(f"Imagen MVP LEGO: {estadoImagen}")
    print("\nOpciones:")
    print("1. Subir imagen MVP LEGO")
    print("2. Ver ranking actual")
    print("3. Esperar")


def ejecutarInteraccionLego(
    sesion: SesionJuego,
    equipoUsuario: Equipo,
    rankingPrevio: list[Equipo],
    segundosMensajes: list[int],
    textoMensaje: str,
) -> None:
    mensajesMostrados: set[int] = set()

    while not sesion.etapaTerminada():
        segundoActual = sesion.cronometroEtapa.segundosTranscurridos()
        for segundoMensaje in segundosMensajes:
            if segundoActual >= segundoMensaje and segundoMensaje not in mensajesMostrados:
                imprimirMensajeLego(textoMensaje)
                mensajesMostrados.add(segundoMensaje)

        imprimirEstadoEtapa(sesion, equipoUsuario)
        proximosMensajes = [segundo for segundo in segundosMensajes if segundo not in mensajesMostrados]
        if proximosMensajes:
            esperaHastaMensaje = max(1, min(proximosMensajes) - segundoActual)
        else:
            esperaHastaMensaje = sesion.segundosRestantesEtapa()
        timeout = max(1, min(sesion.segundosRestantesEtapa(), esperaHastaMensaje))

        opcion, tiempoAgotado = pedirEntradaConTiempo("Selecciona una opcion: ", timeout)
        if tiempoAgotado:
            continue
        if sesion.etapaTerminada():
            break
        if opcion == "1":
            imagen, imagenTiempoAgotado = pedirEntradaConTiempo(
                "Ingresa nombre/ruta de la imagen MVP LEGO: ",
                sesion.segundosRestantesEtapa(),
            )
            if imagenTiempoAgotado or sesion.etapaTerminada():
                break
            if imagen:
                equipoUsuario.subioImagenLego = True
                equipoUsuario.imagenLego = imagen
                print("Imagen MVP LEGO registrada.")
            else:
                print("No se registro imagen.")
        elif opcion == "2":
            imprimirRankingEstandar(rankingPrevio, equipoUsuario.nombreEquipo)
        elif opcion == "3" or not opcion:
            continue
        else:
            print("Opcion no valida.")


def aplicarEntregasSimuladas(equipos: list[Equipo], entregas: dict[str, tuple[bool, str]]) -> None:
    for equipo in equipos:
        entrega = entregas.get(equipo.nombreEquipo)
        if entrega is None:
            continue
        subioImagen, imagen = entrega
        equipo.subioImagenLego = subioImagen
        equipo.imagenLego = imagen


def calcularTokensEtapa(equipos: list[Equipo]) -> None:
    for equipo in equipos:
        equipo.sumarTokensLego(calcularTokensLego(equipo.subioImagenLego))


def crearArgumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una sesion demo de etapa LEGO MVP.")
    parser.add_argument("--duracion", type=int, default=120, help="Duracion de la etapa en segundos.")
    parser.add_argument(
        "--mostrar-ranking",
        type=int,
        default=15,
        help="Segundos que se muestra el ranking final. Por defecto: 15.",
    )
    return parser.parse_args()


def ejecutarEtapaLego(
    raiz: Path,
    rankingGeneral: dict[str, Equipo] | None = None,
    duracion: int = 120,
    mostrarRanking: int = 15,
    sesion: SesionJuego | None = None,
) -> list[Equipo]:
    rutaSesion = raiz / "data" / "equiposSesion.csv"
    rutaSimulados = raiz / "data" / "equiposSimuladosLego.csv"
    rutaRankingGeneral = raiz / "output" / "RankingGeneral.csv"
    rutaRankingLego = raiz / "output" / "RankingLego.csv"

    if rankingGeneral is None:
        rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)
    equipos = [copy(equipo) for equipo in rankingGeneral.values()]
    aplicarRankingGeneralParaLego(equipos, rankingGeneral)
    entregasSimuladas = cargarEntregaLegoSimulada(rutaSimulados)
    aplicarEntregasSimuladas(equipos, entregasSimuladas)

    equipoUsuario = next((equipo for equipo in equipos if equipo.nombreEquipo == "Equipo Usuario"), None)
    if equipoUsuario is None:
        equipoUsuario = Equipo("Equipo Usuario", ordenLlegada=99)
        equipos.append(equipoUsuario)

    rankingPrevio = ordenarRankingGlobalBubbleMap(equipos)
    planesMensajes = {
        equipo.nombreEquipo: calcularPlanMensajesLego(equipo, equipos, duracion) for equipo in equipos
    }
    for equipo in equipos:
        planEquipo = planesMensajes[equipo.nombreEquipo]
        equipo.mensajesLego = planEquipo.cantidadMensajes
        equipo.tipoMensajeLego = planEquipo.tipoMensaje
    planMensajes = planesMensajes[equipoUsuario.nombreEquipo]

    sesionCompartida = sesion is not None
    if sesion is None:
        sesion = SesionJuego(
            nombreSesion="Sesion demo LEGO MVP",
            duracionEtapaSegundos=duracion,
            equipos=equipos,
        )
        sesion.iniciarSesion()
    else:
        sesion.duracionEtapaSegundos = duracion
        sesion.equipos = equipos

    print("=== SESION LEGO MVP INICIADA ===")
    print("Ranking previo antes de sumar esta etapa:")
    imprimirRankingEstandar(rankingPrevio, equipoUsuario.nombreEquipo)
    print(
        f"\nParticipacion previa del equipo: {planMensajes.participacionEquipo * 100:.1f}% | "
        f"mensajes programados: {planMensajes.cantidadMensajes} ({planMensajes.tipoMensaje})"
    )

    sesion.iniciarEtapa()
    if planMensajes.tipoMensaje == "advertencia":
        imprimirMensajeLego(planMensajes.textoMensaje)

    ejecutarInteraccionLego(
        sesion,
        equipoUsuario,
        rankingPrevio,
        planMensajes.segundosProgramados if planMensajes.tipoMensaje == "ayuda" else [],
        planMensajes.textoMensaje,
    )

    print("\nTiempo agotado. Cerrando etapa LEGO...")
    if sesionCompartida:
        sesion.finalizarEtapa()
        sesion.registrarTiempoGlobal()
    else:
        sesion.finalizarSesion()
    calcularTokensEtapa(equipos)

    rankingFinal = ordenarRankingGlobalBubbleMap(equipos)
    imprimirRankingEstandar(rankingFinal, equipoUsuario.nombreEquipo)
    exportarRankingLego(rutaRankingLego, rankingFinal)
    equiposGenerales = actualizarGeneralConLego(rankingGeneral, equipos)
    exportarRankingGeneral(rutaRankingGeneral, equiposGenerales)

    print(f"\nRanking LEGO exportado en: {rutaRankingLego}")
    print(f"Ranking general actualizado en: {rutaRankingGeneral}")
    if mostrarRanking > 0:
        print(f"\nEl ranking se mostrara durante {mostrarRanking} segundos.")
        sleep(mostrarRanking)
    return equiposGenerales


def main() -> None:
    argumentos = crearArgumentos()
    raiz = Path(__file__).resolve().parents[1]
    ejecutarEtapaLego(
        raiz=raiz,
        duracion=argumentos.duracion,
        mostrarRanking=argumentos.mostrar_ranking,
    )


if __name__ == "__main__":
    main()
