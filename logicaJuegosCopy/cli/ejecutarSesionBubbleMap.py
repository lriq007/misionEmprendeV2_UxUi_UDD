from __future__ import annotations

import argparse
import sys
from pathlib import Path
from select import select
from time import sleep

from competencia.cronometro import formatearSegundos
from competencia.csvBubbleMap import cargarEquiposSimuladosBubbleMap, exportarRankingBubbleMap
from competencia.equipo import Equipo
from competencia.rankingGeneral import (
    aplicarRankingGeneralParaBubbleMap,
    actualizarGeneralConBubbleMap,
    cargarRankingGeneral,
    exportarRankingGeneral,
)
from competencia.sesionJuego import SesionJuego
from espera.buscaminasEspera import BuscaminasEspera
from juegos.mapaEmpatia import MapaEmpatia, PreguntaMapaEmpatia
from puntajes.ranking import imprimirRankingEstandar, ordenarRankingGlobalBubbleMap
from puntajes.reglaPuntajeMapaEmpatia import (
    ResultadoMapaEmpatia,
    aplicarResultadoMapa,
    asignarTokensMapaEmpatia,
    evaluarMapaEmpatia,
)


SEGUNDOS_MINIMOS_BUSCAMINAS = 5


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
        print("\nEntrada cerrada. Se detiene la captura de respuestas.")
        return "", True
    return entrada.strip(), False


def imprimirCriteriosBreves() -> None:
    print("\nEvaluacion breve:")
    print("- Completa las 5 preguntas con aportes claros.")
    print("- Se premia buen desarrollo, finalizacion y contenido consistente.")
    print("- Evita respuestas muy cortas, repetidas o excesivamente largas.")


def imprimirCriteriosDetallados() -> None:
    print("\n=== CRITERIOS DE EVALUACION ===")
    print("- Cada pregunta suma si tiene al menos un aporte valido.")
    print("- Un aporte valido tiene entre 8 y 100 caracteres.")
    print("- Un aporte ideal tiene entre 40 y 60 caracteres.")
    print("- Varias preguntas con 2 o mas aportes validos pueden dar bonus.")
    print("- Finalizar dentro del tiempo permite optar a bonus y buscaminas.")
    print("- El ranking final depende de tokensTotales.")


def imprimirMenuPrincipal(mapa: MapaEmpatia, sesion: SesionJuego) -> None:
    print("\n=== BUBBLE MAP ===")
    print(
        f"Tiempo global: {sesion.cronometroGlobal.textoTranscurrido()} | "
        f"Tiempo etapa: {sesion.cronometroEtapa.textoTranscurrido()} | "
        f"Restante: {formatearSegundos(sesion.segundosRestantesEtapa())}"
    )
    imprimirCriteriosBreves()
    mapa.imprimirResumenRespuestas()
    print("\nOpciones:")
    print("1. Responder gustos y disgustos")
    print("2. Responder problemas")
    print("3. Responder miedos")
    print("4. Responder contexto")
    print("5. Responder hobbies")
    print("6. Finalizar etapa")
    print("7. Ver criterios detallados")


def imprimirPregunta(pregunta: PreguntaMapaEmpatia) -> None:
    print(f"\n=== {pregunta.titulo} ===")
    print(pregunta.texto)
    print("\nRespuestas actuales:")
    if not pregunta.apendices:
        print("Sin respuestas todavia.")
        return
    for indice, apendice in enumerate(pregunta.apendices, start=1):
        print(f"{indice}. {apendice}")


def responderPregunta(sesion: SesionJuego, pregunta: PreguntaMapaEmpatia) -> bool:
    while not sesion.etapaTerminada():
        imprimirPregunta(pregunta)
        print("\nOpciones:")
        print("1. Agregar apendice")
        print("2. Ver criterios")
        print("3. Volver al menu")
        opcion, tiempoAgotado = pedirEntradaConTiempo("Selecciona una opcion: ", sesion.segundosRestantesEtapa())
        if tiempoAgotado or sesion.etapaTerminada():
            return False
        if opcion == "1":
            texto, tiempoAgotado = pedirEntradaConTiempo("Escribe el nuevo apendice: ", sesion.segundosRestantesEtapa())
            if tiempoAgotado or sesion.etapaTerminada():
                return False
            pregunta.agregarApendice(texto)
            print("Apendice guardado.")
        elif opcion == "2":
            imprimirCriteriosDetallados()
        elif opcion == "3":
            return True
        else:
            print("Opcion no valida.")
    return False


def confirmarFinalizacion(sesion: SesionJuego, mapa: MapaEmpatia) -> bool:
    print("\n=== RESUMEN ANTES DE FINALIZAR ===")
    mapa.imprimirResumenRespuestas()
    respuesta, tiempoAgotado = pedirEntradaConTiempo(
        "\nConfirmas finalizar la etapa? (s/n): ",
        sesion.segundosRestantesEtapa(),
    )
    if tiempoAgotado or sesion.etapaTerminada():
        return False
    return respuesta.lower() == "s"


def jugarBubbleMap(sesion: SesionJuego, equipoUsuario: Equipo, mapa: MapaEmpatia) -> bool:
    preguntas = mapa.obtenerPreguntasOrdenadas()
    while not sesion.etapaTerminada():
        imprimirMenuPrincipal(mapa, sesion)
        opcion, tiempoAgotado = pedirEntradaConTiempo("Selecciona una opcion: ", sesion.segundosRestantesEtapa())
        if tiempoAgotado or sesion.etapaTerminada():
            break
        if opcion in {"1", "2", "3", "4", "5"}:
            responderPregunta(sesion, preguntas[int(opcion) - 1])
        elif opcion == "6":
            if confirmarFinalizacion(sesion, mapa):
                equipoUsuario.finalizoBubbleMap = True
                equipoUsuario.tiempoBubbleMapSegundos = sesion.cronometroEtapa.segundosTranscurridos()
                print(f"\nEtapa finalizada en {formatearSegundos(equipoUsuario.tiempoBubbleMapSegundos)}.")
                return True
            print("Finalizacion cancelada.")
        elif opcion == "7":
            imprimirCriteriosDetallados()
        else:
            print("Opcion no valida.")

    print("\nTiempo agotado. Se guardan las respuestas ingresadas.")
    equipoUsuario.finalizoBubbleMap = False
    return False


def jugarBuscaminasSiCorresponde(sesion: SesionJuego, equipoUsuario: Equipo) -> None:
    if not equipoUsuario.finalizoBubbleMap:
        return
    segundosRestantes = sesion.segundosRestantesEtapa()
    if segundosRestantes < SEGUNDOS_MINIMOS_BUSCAMINAS:
        print("\nQuedan menos de 5 segundos. Pasas directo a espera de ranking.")
        return

    print("\n=== BUSCAMINAS DE ESPERA ===")
    print("Se habilita porque finalizaste antes de cerrar la etapa.")
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


def imprimirResultadoEquipo(resultado: ResultadoMapaEmpatia, equipo: Equipo) -> None:
    print("\n=== RESULTADO BUBBLE MAP ===")
    print(f"Tokens Bubble Map: {equipo.tokensBubbleMap}")
    print(f"Bonus excelencia y velocidad: {equipo.bonusExcelenciaVelocidad}")
    print(f"Bonus buscaminas: {equipo.bonusEspera}")
    print(f"Preguntas respondidas con aporte valido: {resultado.preguntasCompletas}/5")
    print("\nFortalezas:")
    for fortaleza in resultado.fortalezas:
        print(f"- {fortaleza}")
    print("\nA mejorar:")
    for debilidad in resultado.debilidades:
        print(f"- {debilidad}")


def crearArgumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta una sesion demo de Bubble Map.")
    parser.add_argument("--duracion", type=int, default=120, help="Duracion de la etapa en segundos.")
    parser.add_argument(
        "--mostrar-ranking",
        type=int,
        default=15,
        help="Segundos que se muestra el ranking final. Por defecto: 15.",
    )
    return parser.parse_args()


def ejecutarEtapaBubbleMap(
    raiz: Path,
    rankingGeneral: dict[str, Equipo] | None = None,
    duracion: int = 120,
    mostrarRanking: int = 15,
    sesion: SesionJuego | None = None,
) -> list[Equipo]:
    rutaSimulados = raiz / "data" / "equiposSimuladosBubbleMap.csv"
    rutaSesion = raiz / "data" / "equiposSesion.csv"
    rutaRanking = raiz / "output" / "RankingBubbleMap.csv"
    rutaRankingGeneral = raiz / "output" / "RankingGeneral.csv"

    equipoUsuario = Equipo(nombreEquipo="Equipo Usuario", ordenLlegada=99)
    equipos = cargarEquiposSimuladosBubbleMap(rutaSimulados)
    equipos.append(equipoUsuario)
    if rankingGeneral is None:
        rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)
    aplicarRankingGeneralParaBubbleMap(equipos, rankingGeneral)

    sesionCompartida = sesion is not None
    if sesion is None:
        sesion = SesionJuego(
            nombreSesion="Sesion demo Bubble Map",
            duracionEtapaSegundos=duracion,
            equipos=equipos,
        )
        sesion.iniciarSesion()
    else:
        sesion.duracionEtapaSegundos = duracion
        sesion.equipos = equipos
    mapa = MapaEmpatia.crearBase()

    print("=== SESION BUBBLE MAP INICIADA ===")
    print(f"Duracion etapa demo: {duracion} segundos.")
    sesion.iniciarEtapa()

    jugarBubbleMap(sesion, equipoUsuario, mapa)
    jugarBuscaminasSiCorresponde(sesion, equipoUsuario)
    esperarCierreEtapa(sesion)

    print("\nTiempo agotado. Cerrando etapa...")
    if sesionCompartida:
        sesion.finalizarEtapa()
        sesion.registrarTiempoGlobal()
    else:
        sesion.finalizarSesion()

    resultadoUsuario = evaluarMapaEmpatia(mapa, equipoUsuario.finalizoBubbleMap)
    aplicarResultadoMapa(equipoUsuario, resultadoUsuario)
    asignarTokensMapaEmpatia(equipos)

    rankingFinal = ordenarRankingGlobalBubbleMap(equipos)
    imprimirRankingEstandar(rankingFinal, equipoUsuario.nombreEquipo)
    imprimirResultadoEquipo(resultadoUsuario, equipoUsuario)
    exportarRankingBubbleMap(rutaRanking, rankingFinal)
    equiposGenerales = actualizarGeneralConBubbleMap(rankingGeneral, equipos)
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
    ejecutarEtapaBubbleMap(
        raiz=raiz,
        duracion=argumentos.duracion,
        mostrarRanking=argumentos.mostrar_ranking,
    )


if __name__ == "__main__":
    main()
