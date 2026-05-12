import json
import random

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from etapasJuego.models import Evaluation, GameSession, Team, TeamStageProgress
from etapasJuego.progress import advance_to_stage, build_game_context, ensure_project_from_progress, never_cache, redirect_if_stage_is_past

EVALUACION_DURACION_SEG = 90
RANKING_DURACION_SEG = 300


def coevaluacion_home(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_COEVALUACION)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    equipos = Team.objects.filter(sesion=sesion).exclude(id=team.id).order_by("nombre")
    return never_cache(render(request, 'etapaFinal/index.html', {
        "equipos_a_evaluar": equipos,
        "team_actual": team,
        "sesion": sesion,
        "project": project,
    })
    )


@csrf_exempt
def save_coevaluacion(request):
    sesion, team, _ = build_game_context(request)
    payload = json.loads(request.body.decode("utf-8") or "{}")
    evaluaciones = payload.get("evaluaciones", [])
    updated_teams = set()

    for item in evaluaciones:
        evaluado = Team.objects.filter(id=item.get("evaluado_id"), sesion=sesion).exclude(id=team.id).first()
        if not evaluado:
            return JsonResponse({"ok": False, "msg": "Equipo evaluado inválido"}, status=400)

        scores = {
            "puntaje_equipo": int(item.get("puntaje_equipo") or 0),
            "puntaje_empatia": int(item.get("puntaje_empatia") or 0),
            "puntaje_creatividad": int(item.get("puntaje_creatividad") or 0),
            "puntaje_comunicacion": int(item.get("puntaje_comunicacion") or 0),
        }
        if any(value < 1 or value > 5 for value in scores.values()):
            return JsonResponse({"ok": False, "msg": "Los puntajes deben estar entre 1 y 5"}, status=400)

        Evaluation.objects.update_or_create(
            sesion=sesion,
            evaluador=team,
            evaluado=evaluado,
            defaults={**scores, "comentario": item.get("comentario", "")},
        )
        updated_teams.add(evaluado.id)

    for evaluado in Team.objects.filter(id__in=updated_teams):
        evaluado.update_tokens()

    advance_to_stage(team, TeamStageProgress.STAGE_RESULTADOS, "etapaFinal:final_resultados", "coevaluacion_completed")
    return JsonResponse({
        "status": "ok",
        "ok": True,
        "msg": "Coevaluaciones guardadas",
        "redirect_url": reverse("etapaFinal:final_resultados"),
    })


def final_resultados(request):
    sesion, team, _ = build_game_context(request)
    ranking = Team.objects.filter(sesion=sesion).order_by("-tokens_totales", "nombre")
    return never_cache(render(request, 'etapaFinal/final_resultados.html', {
        "ranking": ranking,
        "ganador": ranking.first(),
        "sesion": sesion,
        "team_actual": team,
    })
    )


def cierre_final(request):
    sesion, team, _ = build_game_context(request)
    return never_cache(render(request, 'etapaFinal/cierre_final.html', {
        "team": team,
        "sesion": sesion,
    }))


@csrf_exempt
def upload_foto_grupal(request):
    _, _, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    if not project or "foto_grupal" not in request.FILES:
        return JsonResponse({"ok": False, "msg": "No hay foto para guardar"}, status=400)
    project.foto_grupal = request.FILES["foto_grupal"]
    project.save(update_fields=["foto_grupal"])
    return JsonResponse({"ok": True, "msg": "Foto grupal guardada", "foto_url": project.foto_grupal.url})


# ---------------------------------------------------------------------------
# Negociación secuencial (pitches por turno + coevaluación)
# ---------------------------------------------------------------------------

def _presentador_data(presentador_team):
    """Builds the JSON-serializable dict for the current presenter."""
    project = getattr(presentador_team, "proyecto", None)
    pitch = getattr(project, "pitch", None) if project else None
    foto_grupal_url = project.foto_grupal.url if project and project.foto_grupal else None
    foto_prototipo_url = project.foto_prototipo.url if project and project.foto_prototipo else None
    pitch_data = {}
    pitch_duracion = 90
    if pitch:
        pitch_data = {
            "nombre_producto": pitch.nombre_producto,
            "desafio_empatia": pitch.desafio_empatia,
            "campo_creatividad": pitch.campo_creatividad,
            "cierre": pitch.cierre,
        }
        pitch_duracion = pitch.tiempo_presentacion_seg
    return {
        "id": presentador_team.id,
        "nombre": presentador_team.nombre,
        "nombre_emprendimiento": pitch.nombre_producto if pitch else "",
        "foto_grupal_url": foto_grupal_url,
        "foto_prototipo_url": foto_prototipo_url,
        "pitch": pitch_data,
        "pitch_duracion_seg": pitch_duracion,
    }


def _advance_to_next_or_ranking(sesion):
    """After evaluation round ends: go to next presenter (ORDEN) or final RANKING."""
    next_idx = sesion.negociacion_presentador_idx + 1
    if next_idx < len(sesion.negociacion_orden):
        sesion.negociacion_presentador_idx = next_idx
        sesion.negociacion_fase = "ORDEN"
        sesion.negociacion_fase_inicio = None
    else:
        sesion.negociacion_fase = "RANKING"
        sesion.negociacion_fase_inicio = timezone.now()
    sesion.save(update_fields=["negociacion_presentador_idx", "negociacion_fase", "negociacion_fase_inicio"])


def negociacion_view(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_COEVALUACION)
    if redirect_response:
        return redirect_response
    sesion, team, _ = build_game_context(request)

    # Initialize presentation order once (atomic to avoid race condition)
    if not sesion.negociacion_orden:
        with transaction.atomic():
            sesion.refresh_from_db(fields=["negociacion_orden"])
            if not sesion.negociacion_orden:
                team_ids = list(sesion.equipos.values_list("id", flat=True))
                random.shuffle(team_ids)
                sesion.negociacion_orden = team_ids
                sesion.negociacion_presentador_idx = 0
                sesion.negociacion_fase = "ORDEN"
                sesion.negociacion_fase_inicio = None
                sesion.save(update_fields=["negociacion_orden", "negociacion_presentador_idx", "negociacion_fase", "negociacion_fase_inicio"])

    return never_cache(render(request, "etapaFinal/negociacion.html", {
        "team": team,
        "sesion": sesion,
        "estado_url": reverse("etapaFinal:api_negociacion_estado"),
        "iniciar_pitch_url": reverse("etapaFinal:api_negociacion_iniciar_pitch"),
        "timeup_pitch_url": reverse("etapaFinal:api_negociacion_timeup_pitch"),
        "guardar_eval_url": reverse("etapaFinal:api_negociacion_guardar_evaluacion"),
        "timeup_eval_url": reverse("etapaFinal:api_negociacion_timeup_evaluacion"),
    }))


def api_negociacion_estado(request):
    sesion, team, _ = build_game_context(request)

    with transaction.atomic():
        sesion = GameSession.objects.select_for_update().get(pk=sesion.pk)

        # Auto-advance EVALUANDO when time is up (handles single-team testing and
        # the case where the presenter's screen has no eval timer)
        if sesion.negociacion_fase == "EVALUANDO" and sesion.negociacion_fase_inicio:
            elapsed = (timezone.now() - sesion.negociacion_fase_inicio).total_seconds()
            if elapsed >= EVALUACION_DURACION_SEG:
                _advance_to_next_or_ranking(sesion)

        # Auto-advance RANKING after 12 s
        if sesion.negociacion_fase == "RANKING" and sesion.negociacion_fase_inicio:
            elapsed = (timezone.now() - sesion.negociacion_fase_inicio).total_seconds()
            if elapsed >= RANKING_DURACION_SEG:
                # Advance all teams to RESULTADOS
                for progress_obj in TeamStageProgress.objects.select_related("team").filter(game_session=sesion):
                    if progress_obj.current_stage == TeamStageProgress.STAGE_COEVALUACION:
                        advance_to_stage(progress_obj.team, TeamStageProgress.STAGE_RESULTADOS,
                                         "etapaFinal:cierre_final", "coevaluacion_completed")
                return JsonResponse({
                    "all_done": True,
                    "redirect_url": reverse("etapaFinal:cierre_final"),
                })

        orden = sesion.negociacion_orden or []
        idx = sesion.negociacion_presentador_idx
        presentador_id = orden[idx] if orden and idx < len(orden) else None
        presentador_team = Team.objects.select_related("proyecto__pitch").filter(id=presentador_id).first() if presentador_id else None

        yo_ya_evalue = False
        if presentador_team and sesion.negociacion_fase == "EVALUANDO":
            yo_ya_evalue = Evaluation.objects.filter(
                sesion=sesion, evaluador=team, evaluado=presentador_team
            ).exists()

        # Ranking data (only in RANKING phase)
        ranking = []
        if sesion.negociacion_fase == "RANKING":
            ranking_qs = (
                Team.objects.filter(sesion=sesion)
                .select_related("proyecto__pitch")
                .order_by("-tokens_totales", "nombre")
            )
            for eq in ranking_qs:
                project = getattr(eq, "proyecto", None)
                pitch = getattr(project, "pitch", None) if project else None
                foto_url = project.foto_grupal.url if project and project.foto_grupal else None
                ranking.append({
                    "id": eq.id,
                    "nombre": eq.nombre,
                    "tokens": eq.tokens_totales,
                    "nombre_emprendimiento": pitch.nombre_producto if pitch else "",
                    "foto_grupal_url": foto_url,
                })

        orden_data = []
        for pos, tid in enumerate(orden):
            eq = Team.objects.filter(id=tid).first()
            if eq:
                orden_data.append({"id": eq.id, "nombre": eq.nombre, "posicion": pos + 1})

        fase_inicio_ts = None
        if sesion.negociacion_fase_inicio:
            fase_inicio_ts = sesion.negociacion_fase_inicio.timestamp()

        presentador_payload = _presentador_data(presentador_team) if presentador_team else {}

        return JsonResponse({
            "fase": sesion.negociacion_fase,
            "presentador_idx": idx,
            "total": len(orden),
            "soy_presentador": team.id == presentador_id,
            "presentador": presentador_payload,
            "orden": orden_data,
            "evaluacion_duracion_seg": EVALUACION_DURACION_SEG,
            "fase_inicio_ts": fase_inicio_ts,
            "yo_ya_evalue": yo_ya_evalue,
            "ranking": ranking,
            "ranking_duracion_seg": RANKING_DURACION_SEG,
            "all_done": False,
            "redirect_url": None,
        })


@csrf_exempt
def api_negociacion_iniciar_pitch(request):
    sesion, team, _ = build_game_context(request)
    with transaction.atomic():
        sesion = GameSession.objects.select_for_update().get(pk=sesion.pk)
        orden = sesion.negociacion_orden or []
        idx = sesion.negociacion_presentador_idx
        if not orden or idx >= len(orden) or orden[idx] != team.id:
            return JsonResponse({"ok": False, "msg": "No eres el presentador actual"}, status=403)
        if sesion.negociacion_fase == "PITCH":
            return JsonResponse({"ok": True})
        sesion.negociacion_fase = "PITCH"
        sesion.negociacion_fase_inicio = timezone.now()
        sesion.save(update_fields=["negociacion_fase", "negociacion_fase_inicio"])
    return JsonResponse({"ok": True})


@csrf_exempt
def api_negociacion_timeup_pitch(request):
    sesion, _, _ = build_game_context(request)
    with transaction.atomic():
        sesion = GameSession.objects.select_for_update().get(pk=sesion.pk)
        if sesion.negociacion_fase == "EVALUANDO":
            return JsonResponse({"ok": True})
        orden = sesion.negociacion_orden or []
        idx = sesion.negociacion_presentador_idx
        presentador_id = orden[idx] if idx < len(orden) else None
        n_necesarios = sesion.equipos.exclude(id=presentador_id).count() if presentador_id else 0
        if n_necesarios == 0:
            # Nadie puede evaluar (equipo único o sin otros equipos) → avanzar de inmediato
            _advance_to_next_or_ranking(sesion)
        else:
            sesion.negociacion_fase = "EVALUANDO"
            sesion.negociacion_fase_inicio = timezone.now()
            sesion.save(update_fields=["negociacion_fase", "negociacion_fase_inicio"])
    return JsonResponse({"ok": True})


@csrf_exempt
def api_negociacion_guardar_evaluacion(request):
    sesion, team, _ = build_game_context(request)
    payload = json.loads(request.body.decode("utf-8") or "{}")

    with transaction.atomic():
        sesion = GameSession.objects.select_for_update().get(pk=sesion.pk)
        orden = sesion.negociacion_orden or []
        idx = sesion.negociacion_presentador_idx
        if not orden or idx >= len(orden):
            return JsonResponse({"ok": False, "msg": "No hay presentador activo"}, status=400)

        presentador_id = orden[idx]
        if team.id == presentador_id:
            return JsonResponse({"ok": False, "msg": "El presentador no puede evaluarse a sí mismo"}, status=400)

        presentador = Team.objects.filter(id=presentador_id, sesion=sesion).first()
        if not presentador:
            return JsonResponse({"ok": False, "msg": "Presentador no encontrado"}, status=400)

        scores = {
            "puntaje_equipo": int(payload.get("puntaje_equipo") or 0),
            "puntaje_empatia": int(payload.get("puntaje_empatia") or 0),
            "puntaje_creatividad": int(payload.get("puntaje_creatividad") or 0),
            "puntaje_comunicacion": int(payload.get("puntaje_comunicacion") or 0),
        }
        if any(v < 1 or v > 5 for v in scores.values()):
            return JsonResponse({"ok": False, "msg": "Los puntajes deben estar entre 1 y 5"}, status=400)

        Evaluation.objects.update_or_create(
            sesion=sesion,
            evaluador=team,
            evaluado=presentador,
            defaults={**scores, "comentario": payload.get("comentario", "")},
        )
        presentador.update_tokens()

        n_necesarios = sesion.equipos.exclude(id=presentador_id).count()
        n_enviados = Evaluation.objects.filter(sesion=sesion, evaluado=presentador).count()
        if n_enviados >= n_necesarios:
            _advance_to_next_or_ranking(sesion)
        else:
            sesion.refresh_from_db(fields=["negociacion_fase"])

    return JsonResponse({"ok": True, "fase": sesion.negociacion_fase})


@csrf_exempt
def api_negociacion_timeup_evaluacion(request):
    sesion, _, _ = build_game_context(request)
    with transaction.atomic():
        sesion = GameSession.objects.select_for_update().get(pk=sesion.pk)
        if sesion.negociacion_fase in ("ORDEN", "RANKING"):
            return JsonResponse({"ok": True})
        _advance_to_next_or_ranking(sesion)
    return JsonResponse({"ok": True})
