import os
import random
import secrets
import string
import json

from django.core.files.base import File as DjangoFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .models import Challenge, Desafio, EmpathyMap, Pitch, Project, TeamGameSession, TeamStageProgress, Topic
from .services import RouletteEngine, generate_board
from .progress import (
    advance_to_stage,
    build_game_context,
    ensure_project_from_progress,
    get_progress_for_team,
    never_cache,
    parse_selected_challenge,
    redirect_if_stage_is_past,
    set_current_stage,
)

DEFAULT_SOPA_WORDS = [
    "EMPATIA", "STARTUP", "EQUIPO", "VALOR", "RIESGO",
    "PITCH", "LEAN", "IDEA", "LIDER", "AGIL",
]

# ---------------------------------------------------------------------------
# Datos estáticos de demostración
# ---------------------------------------------------------------------------

DEMO_SQUAD_TOPICS = [
    {
        "topic": {"id": 1, "nombre": "Salud y Bienestar"},
        "style": {
            "class": "squad-card--red",
            "image": "/media/imgHistoria/escuadronRojo.png",
            "label": "Rojo",
        },
        "desafios": [
            {
                "id": 1,
                "titulo": "Tecnología para adultos mayores",
                "historia": "Don Miguel (72) quiere conectarse con su familia pero no sabe usar su teléfono.",
                "challenge": {
                    "id": 1,
                    "descripcion": "Mejorar autonomía digital de adultos mayores.",
                    "video_file": None,
                },
                "topic_id": 1,
                "challenge_id": 1,
            },
            {
                "id": 2,
                "titulo": "Acceso a salud mental",
                "historia": "Andrea (25) necesita apoyo psicológico pero los costos son prohibitivos.",
                "challenge": {
                    "id": 1,
                    "descripcion": "Democratizar el acceso a salud mental.",
                    "video_file": None,
                },
                "topic_id": 1,
                "challenge_id": 1,
            },
            {
                "id": 3,
                "titulo": "Nutrición en zonas vulnerables",
                "historia": "La familia López no puede acceder a alimentación saludable.",
                "challenge": {
                    "id": 1,
                    "descripcion": "Mejorar nutrición en comunidades de bajos recursos.",
                    "video_file": None,
                },
                "topic_id": 1,
                "challenge_id": 1,
            },
        ],
    },
    {
        "topic": {"id": 2, "nombre": "Sustentabilidad"},
        "style": {
            "class": "squad-card--blue",
            "image": "/media/imgHistoria/escuadronAzul.png",
            "label": "Azul",
        },
        "desafios": [
            {
                "id": 4,
                "titulo": "Residuos domiciliarios",
                "historia": "El barrio de Carla genera 2 toneladas de basura semanal sin reciclar.",
                "challenge": {
                    "id": 2,
                    "descripcion": "Reducir el impacto ambiental de residuos domiciliarios.",
                    "video_file": None,
                },
                "topic_id": 2,
                "challenge_id": 2,
            },
            {
                "id": 5,
                "titulo": "Energía renovable local",
                "historia": "La villa San Pedro paga cuentas eléctricas altísimas.",
                "challenge": {
                    "id": 2,
                    "descripcion": "Facilitar acceso a energías renovables para comunidades.",
                    "video_file": None,
                },
                "topic_id": 2,
                "challenge_id": 2,
            },
            {
                "id": 6,
                "titulo": "Agua y sequía",
                "historia": "Los agricultores del norte pierden cosechas por la escasez de agua.",
                "challenge": {
                    "id": 2,
                    "descripcion": "Optimizar el uso del agua en contextos de sequía.",
                    "video_file": None,
                },
                "topic_id": 2,
                "challenge_id": 2,
            },
        ],
    },
    {
        "topic": {"id": 3, "nombre": "Educación"},
        "style": {
            "class": "squad-card--yellow",
            "image": "/media/imgHistoria/escuadronAmarillo.png",
            "label": "Amarillo",
        },
        "desafios": [
            {
                "id": 7,
                "titulo": "Brecha digital en colegios",
                "historia": "En el colegio de María no hay computadores para todos los alumnos.",
                "challenge": {
                    "id": 3,
                    "descripcion": "Reducir la brecha digital en establecimientos educacionales.",
                    "video_file": None,
                },
                "topic_id": 3,
                "challenge_id": 3,
            },
            {
                "id": 8,
                "titulo": "Deserción escolar",
                "historia": "Felipe (16) trabaja para ayudar a su familia y no puede seguir estudiando.",
                "challenge": {
                    "id": 3,
                    "descripcion": "Combatir la deserción escolar en jóvenes vulnerables.",
                    "video_file": None,
                },
                "topic_id": 3,
                "challenge_id": 3,
            },
            {
                "id": 9,
                "titulo": "Aprendizaje inclusivo",
                "historia": "Sofía tiene dislexia y el sistema escolar no está adaptado para ella.",
                "challenge": {
                    "id": 3,
                    "descripcion": "Crear herramientas de aprendizaje inclusivo.",
                    "video_file": None,
                },
                "topic_id": 3,
                "challenge_id": 3,
            },
        ],
    },
]

DEMO_WORDS = ["INNOVACION", "STARTUP", "LIDERAZGO", "CREATIVIDAD", "EMPATIA"]

DEMO_TIPS = [
    "Describe el problema que resuelves en una sola oración.",
    "¿Quién es tu cliente? Sé específico.",
    "Menciona tu propuesta de valor única.",
    "¿Cómo genera valor tu solución?",
    "Termina con un llamado a la acción claro.",
]

SQUAD_STYLES = [
    {"class": "squad-card--red", "image": "/media/imgHistoria/escuadronRojo.png", "label": "Rojo"},
    {"class": "squad-card--blue", "image": "/media/imgHistoria/escuadronAzul.png", "label": "Azul"},
    {"class": "squad-card--yellow", "image": "/media/imgHistoria/escuadronAmarillo.png", "label": "Amarillo"},
]


def _make_demo_board():
    letters = list(string.ascii_uppercase)
    return [[random.choice(letters) for _ in range(10)] for _ in range(10)]


# ---------------------------------------------------------------------------
# Ranking helpers
# ---------------------------------------------------------------------------

_STATUS_LABELS = {
    TeamGameSession.STATUS_FINISHED: "Completado",
    TeamGameSession.STATUS_TIME_UP:  "Tiempo agotado",
    TeamGameSession.STATUS_PLAYING:  "En curso",
    TeamGameSession.STATUS_PENDING:  "Pendiente",
}


def _format_elapsed(seconds):
    if seconds is None:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _build_ranking_entries(sessions):
    sessions = list(sessions)
    finished = [s for s in sessions if s.status == TeamGameSession.STATUS_FINISHED]
    entries = []
    for item in sessions:
        if item.status == TeamGameSession.STATUS_FINISHED and item.elapsed_seconds is not None:
            position = sum(
                1 for f in finished
                if f.elapsed_seconds is not None and f.elapsed_seconds < item.elapsed_seconds
            ) + 1
        else:
            position = None
        entries.append({
            "team_id":      item.team_id,
            "team_name":    item.equipo.nombre if item.equipo else item.team_id,
            "position":     position,
            "elapsed_label": _format_elapsed(item.elapsed_seconds),
            "status_label": _STATUS_LABELS.get(item.status, item.status),
            "progress_pct": item.progress_pct,
            "elapsed_seconds": item.elapsed_seconds,
            "status":       item.status,
        })
    return entries


# ---------------------------------------------------------------------------
# Vistas principales
# ---------------------------------------------------------------------------

def etapas_index(request):
    return redirect("etapa1")


def _render_game(request, template, context):
    response = render(request, template, context)
    return never_cache(response)


def _build_squad_topics():
    topics = list(Topic.objects.filter(activo=True).order_by("id"))
    topic_rule_error = None
    desafio_rule_error = None

    if len(topics) != 3:
        topic_rule_error = "Debe haber exactamente 3 temas activos para iniciar la misión."

    slots = []
    for index, topic in enumerate(topics[:3]):
        desafios = list(
            Desafio.objects.filter(activo=True, challenge__topic=topic, challenge__activo=True)
            .select_related("challenge", "challenge__topic")
            .order_by("numero", "id")
        )
        if len(desafios) > 3:
            desafio_rule_error = "Cada tema debe tener maximo 3 desafios activos."
        slots.append({
            "topic": topic,
            "style": SQUAD_STYLES[index % len(SQUAD_STYLES)],
            "desafios": desafios[:3],
        })

    if not slots:
        slots = DEMO_SQUAD_TOPICS
    return slots, topic_rule_error, desafio_rule_error


def _bubble_questions(empathy_map=None):
    def answer_for(answers, js_key, model_value, spanish_key):
        value = model_value or answers.get(js_key) or answers.get(spanish_key) or ""
        if isinstance(value, list):
            return "\n".join(str(item).strip() for item in value if str(item).strip())
        return value

    answers = {}
    if empathy_map:
        answers = empathy_map.datos_extra or {}
        answers.update({
            "likes_dislikes": answer_for(answers, "likes_dislikes", empathy_map.gustos, "gustos"),
            "obstacles": answer_for(answers, "obstacles", empathy_map.problemas, "problemas"),
            "feelings": answer_for(answers, "feelings", empathy_map.miedos, "miedos"),
            "others_say": answer_for(answers, "others_say", empathy_map.contexto, "contexto"),
            "hobbies": answer_for(answers, "hobbies", empathy_map.hobbies, "hobbies"),
        })
    return [
        {"key": "likes_dislikes", "label": "¿Qué le gusta o le disgusta?", "answer": answers.get("likes_dislikes", "")},
        {"key": "obstacles", "label": "¿Qué obstáculos enfrenta?", "answer": answers.get("obstacles", "")},
        {"key": "feelings", "label": "¿Qué siente o teme?", "answer": answers.get("feelings", "")},
        {"key": "others_say", "label": "¿Qué dice su entorno?", "answer": answers.get("others_say", "")},
        {"key": "hobbies", "label": "¿Qué hace en su día a día?", "answer": answers.get("hobbies", "")},
    ]


def seleccion_modalidad(request):
    return render(request, "etapasJuego/seleccion_modalidad.html")


def rompehielo(request):
    engine = RouletteEngine()
    modality = engine.normalize_modality(request.GET.get("modalidad"))
    wants_json = (
        request.GET.get("format") == "json"
        or "application/json" in request.headers.get("Accept", "")
    )
    if wants_json:
        preguntas = engine.get_questions(modality)
        return JsonResponse({
            "success": True,
            "modality": modality,
            "requires_intro": modality == RouletteEngine.MODALITY_NEW_TEAM,
            "questions": preguntas,
        })
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_ROMPEHIELO)
    if redirect_response:
        return redirect_response
    sesion, team, _ = build_game_context(request)
    students = list(team.estudiantes.order_by("id").values("id", "nombre_apellido", "carrera"))
    player_count = len(students) or 1
    return _render_game(request, "etapasJuego/rompehielo.html", {
        "rompehielo_bootstrap_url": f"{request.path}?format=json&modalidad={modality}",
        "rompehielo_duration_seconds": 5,
        "rompehielo_modality": modality,
        "rompehielo_requires_intro": modality == RouletteEngine.MODALITY_NEW_TEAM,
        "rompehielo_player_count": player_count,
        "rompehielo_players": students or [{"id": None, "nombre_apellido": "Integrante 1", "carrera": ""}],
        "sesion": sesion,
        "team": team,
    })


def etapa1(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_ETAPA1)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    if progress.current_stage == TeamStageProgress.STAGE_ROMPEHIELO:
        set_current_stage(team, TeamStageProgress.STAGE_ETAPA1, "etapa1")
    return _render_game(request, "etapasJuego/etapa1.html", {
        "sesion": sesion,
        "team": team,
        "stage1_session": None,
        "ranking_url": reverse("espera_etapa", args=[1]),
        "api_init_url": reverse("api_init"),
        "api_start_url": reverse("api_stage1_start"),
        "api_timeup_url": reverse("api_stage1_timeup"),
        "api_select_start_url": reverse("api_select_start"),
        "api_select_extend_url": reverse("api_select_extend"),
        "api_select_commit_url": reverse("api_select_commit"),
    })


def etapa1_ranking(request):
    sesion, team, _ = build_game_context(request)
    sessions = (
        TeamGameSession.objects
        .filter(equipo__sesion=sesion)
        .select_related("equipo")
        .order_by("-progress_pct", "elapsed_seconds", "equipo__nombre")
    )
    ranking_entries = _build_ranking_entries(sessions)
    all_finished = all(
        e["status"] in (TeamGameSession.STATUS_FINISHED, TeamGameSession.STATUS_TIME_UP)
        for e in ranking_entries
    ) if ranking_entries else False
    return _render_game(request, "etapasJuego/ranking_etapa1.html", {
        "sesion": sesion,
        "team": team,
        "ranking_entries": ranking_entries,
        "ranking_api_url": reverse("api_stage1_ranking"),
        "all_finished": all_finished,
        "next_url": reverse("inicioHistoria"),
    })


def inicioHistoria(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_HISTORIA)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    if progress.current_stage == TeamStageProgress.STAGE_ETAPA1:
        advance_to_stage(team, TeamStageProgress.STAGE_HISTORIA, "inicioHistoria", "etapa1_completed")
    squad_topics, topic_rule_error, desafio_rule_error = _build_squad_topics()
    return _render_game(request, "etapasJuego/inicioHistoria.html", {
        "sesion": sesion,
        "team": team,
        "squad_topics": squad_topics,
        "topic_rule_error": topic_rule_error,
        "desafio_rule_error": desafio_rule_error,
        "config_blocker": bool(topic_rule_error or desafio_rule_error),
    })


def etapa2_tema(request):
    sesion, team, progress = build_game_context(request)
    if request.method == "POST":
        topic_id = request.POST.get("topic_id")
        if topic_id:
            progress.selected_topic = get_object_or_404(Topic, id=topic_id, activo=True)
            progress.current_stage = TeamStageProgress.STAGE_ETAPA2
            progress.current_route = "etapa2"
            progress.save(update_fields=["selected_topic", "current_stage", "current_route", "updated_at"])
        return redirect("etapa2")
    return _render_game(request, "etapasJuego/etapa2_0.html", {
        "sesion": sesion,
        "team": team,
        "topics": Topic.objects.filter(activo=True).order_by("id"),
    })


def etapa2(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_ETAPA2)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    if progress.current_stage in [TeamStageProgress.STAGE_HISTORIA, TeamStageProgress.STAGE_ETAPA1]:
        set_current_stage(team, TeamStageProgress.STAGE_ETAPA2, "etapa2")
    topic = progress.selected_topic
    desafios = Desafio.objects.filter(activo=True, challenge__activo=True).select_related("challenge")
    if topic:
        desafios = desafios.filter(challenge__topic=topic)
    return _render_game(request, "etapasJuego/etapa2.html", {
        "sesion": sesion,
        "team": team,
        "desafios": desafios.order_by("numero", "id"),
        "topic": topic,
    })


def etapa2_seleccionar(request):
    if request.method == "POST":
        sesion, team, progress = build_game_context(request)
        topic, challenge, desafio = parse_selected_challenge(
            request.POST.get("topic_id"),
            request.POST.get("challenge_id"),
            request.POST.get("desafio_id"),
        )
        project, _ = Project.objects.update_or_create(
            equipo=team,
            defaults={"desafio": challenge, "selected_desafio": desafio},
        )
        # Attach the team photo uploaded during squad selection (stored in session)
        _tmp_foto = request.session.pop("tmp_foto_equipo_path", None)
        if _tmp_foto and default_storage.exists(_tmp_foto):
            _ext = os.path.splitext(_tmp_foto)[-1] or ".jpg"
            _filename = f"foto_grupal_equipo_{team.id}{_ext}"
            try:
                with default_storage.open(_tmp_foto, "rb") as _f:
                    project.foto_grupal.save(_filename, DjangoFile(_f), save=False)
                project.save(update_fields=["foto_grupal"])
                default_storage.delete(_tmp_foto)
            except Exception:
                pass
        progress.selected_topic = topic
        progress.selected_challenge = challenge
        progress.selected_desafio = desafio
        progress.project = project
        progress.current_stage = TeamStageProgress.STAGE_ETAPA2_MAPA
        progress.current_route = "etapa2_1"
        progress.save()
        request.session["topic_id"] = topic.id
        request.session["project_id"] = project.id
        request.session["etapa2_desafio_numero"] = desafio.id
        return redirect("etapa2_1")
    return redirect("etapa2_1")


def etapa2_1(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_ETAPA2_MAPA)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    desafio = progress.selected_desafio or (project.selected_desafio if project else None)
    empathy_map = getattr(project, "mapa_empatia", None) if project else None
    # Global timer: elapsed since sopa session started
    sopa_session = team.wordsearch_sessions.order_by("-id").first()
    global_elapsed = 0
    if sopa_session and sopa_session.started_at:
        from django.utils import timezone
        global_elapsed = int((timezone.now() - sopa_session.started_at).total_seconds())
    return _render_game(request, "etapasJuego/etapa2_1.html", {
        "sesion": sesion,
        "team": team,
        "desafio": desafio,
        "desafio_persona_image": desafio.imagen_personaje.url if desafio and desafio.imagen_personaje else "",
        "project": project,
        "bubble_questions": _bubble_questions(empathy_map),
        "save_url": reverse("etapa2_guardar_mapa"),
        "stage_duration_seconds": sesion.duracion_etapa2_segundos,
        "timeup_url": reverse("api_etapa2_timeup"),
        "global_elapsed_seconds": global_elapsed,
    })


@csrf_exempt
def etapa2_guardar_mapa(request):
    _, team, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    if not project:
        return JsonResponse({"ok": False, "msg": "No hay proyecto seleccionado"}, status=400)
    payload = json.loads(request.body.decode("utf-8") or "{}")
    respuestas = payload.get("respuestas", {})

    # Map JS keys → Spanish model field names; split by newline → list of apéndices
    key_map = {
        "likes_dislikes": "gustos",
        "obstacles": "problemas",
        "feelings": "miedos",
        "others_say": "contexto",
        "hobbies": "hobbies",
    }
    parsed = {
        es: [line.strip() for line in respuestas.get(js, "").split("\n") if line.strip()]
        for js, es in key_map.items()
    }

    EmpathyMap.objects.update_or_create(
        proyecto=project,
        defaults={
            "gustos":    respuestas.get("likes_dislikes", ""),
            "problemas": respuestas.get("obstacles", ""),
            "miedos":    respuestas.get("feelings", ""),
            "contexto":  respuestas.get("others_say", ""),
            "hobbies":   respuestas.get("hobbies", ""),
            "datos_extra": parsed,  # {campo_es: [apendice1, apendice2, …]}
        },
    )
    # Mark completed but do NOT advance stage or compute tokens yet
    progress.etapa2_completed = True
    progress.save(update_fields=["etapa2_completed", "updated_at"])
    return JsonResponse({"ok": True, "redirect_url": reverse("espera_etapa", args=[2])})


def etapa3(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_ETAPA3)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    if progress.current_stage == TeamStageProgress.STAGE_ETAPA2_MAPA:
        set_current_stage(team, TeamStageProgress.STAGE_ETAPA3, "etapa3")
    project = ensure_project_from_progress(progress)
    sopa_session = team.wordsearch_sessions.order_by("-id").first()
    global_elapsed = 0
    if sopa_session and sopa_session.started_at:
        from django.utils import timezone
        global_elapsed = int((timezone.now() - sopa_session.started_at).total_seconds())
    return _render_game(request, "etapasJuego/etapa3.html", {
        "sesion": sesion,
        "team": team,
        "project": project,
        "save_url": reverse("etapa3_guardar_foto"),
        "stage_duration_seconds": sesion.duracion_etapa3_segundos,
        "timeup_url": reverse("api_etapa3_timeup"),
        "global_elapsed_seconds": global_elapsed,
    })


@csrf_exempt
def etapa3_guardar_foto(request):
    _, team, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    if not project:
        return redirect("etapa2")
    resumen = (request.POST.get("resumen_idea") or "").strip()[:280]
    project.resumen_idea = resumen
    if request.FILES.get("lego_image"):
        project.foto_prototipo = request.FILES["lego_image"]
    project.save()
    # Mark completed but do NOT advance stage or compute tokens yet
    progress.etapa3_completed = True
    progress.save(update_fields=["etapa3_completed", "updated_at"])
    return redirect(reverse("espera_etapa", args=[3]))


@csrf_exempt
def api_guardar_foto_equipo(request):
    """Receives the team group photo taken during squad selection.
    Saves it to a temp location and stores the path in the session so
    etapa2_seleccionar can attach it to the project once the challenge is chosen.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "msg": "Método no permitido"}, status=405)
    _, team, _ = build_game_context(request)
    nombre_equipo = (request.POST.get("nombre_equipo") or "").strip()
    if not nombre_equipo:
        return JsonResponse({"ok": False, "msg": "Ingresen un nombre creativo para el equipo"}, status=400)
    foto = request.FILES.get("foto_equipo")
    if not foto:
        return JsonResponse({"ok": False, "msg": "No se recibió archivo"}, status=400)
    if foto.size > 8 * 1024 * 1024:
        return JsonResponse({"ok": False, "msg": "Archivo demasiado grande (máx 8 MB)"}, status=400)
    ext = os.path.splitext(foto.name)[-1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    tmp_name = f"fotos_grupales/tmp/equipo_{team.id}{ext}"
    if default_storage.exists(tmp_name):
        default_storage.delete(tmp_name)
    saved_path = default_storage.save(tmp_name, foto)
    team.nombre = nombre_equipo[:100]
    team.save(update_fields=["nombre", "tablet"])
    request.session["tmp_foto_equipo_path"] = saved_path
    return JsonResponse({"ok": True, "msg": "Foto y nombre del equipo guardados correctamente"})


PITCH_FIELDS = [
    {
        "key": "nombre_producto",
        "label": "Nombre del producto",
        "description": "Nombren la idea que van a defender.",
        "max_length": 40,
        "placeholder": "¿Cómo se llama su solución?",
        "rows": 2,
    },
    {
        "key": "desafio_empatia",
        "label": "El problema",
        "description": "Declaren el dolor humano que quieren resolver.",
        "max_length": 220,
        "placeholder": "¿Qué miedo, bloqueo o necesidad enfrenta el usuario?",
        "rows": 4,
    },
    {
        "key": "campo_creatividad",
        "label": "La solución",
        "description": "Expliquen por qué su propuesta puede cambiar la situación.",
        "max_length": 220,
        "placeholder": "¿Qué hace única y valiosa su idea?",
        "rows": 4,
    },
    {
        "key": "cierre",
        "label": "Cierre",
        "description": "Cierren con una invitación clara a apoyar la propuesta.",
        "max_length": 160,
        "placeholder": "¿Por qué esta idea merece apoyo ahora?",
        "rows": 3,
    },
]


def etapa4(request):
    redirect_response = redirect_if_stage_is_past(request, TeamStageProgress.STAGE_ETAPA4)
    if redirect_response:
        return redirect_response
    sesion, team, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    pitch = None
    if project:
        pitch, _ = Pitch.objects.get_or_create(proyecto=project)
    sopa_session = team.wordsearch_sessions.order_by("-id").first()
    global_elapsed = 0
    if sopa_session and sopa_session.started_at:
        from django.utils import timezone
        global_elapsed = int((timezone.now() - sopa_session.started_at).total_seconds())
    # Build pitch fields with pre-filled values
    pitch_fields_with_values = []
    for field_def in PITCH_FIELDS:
        value = getattr(pitch, field_def["key"], "") if pitch else ""
        pitch_fields_with_values.append({**field_def, "value": value or ""})

    return _render_game(request, "etapasJuego/etapa4.html", {
        "sesion": sesion,
        "team": team,
        "project": project,
        "pitch": pitch,
        "pitch_fields": pitch_fields_with_values,
        "ia_disponible": False,
        "save_url": reverse("etapa4_guardar_pitch"),
        "stage_duration_seconds": sesion.duracion_etapa4_segundos,
        "timeup_url": reverse("api_etapa4_timeup"),
        "global_elapsed_seconds": global_elapsed,
    })


@csrf_exempt
def etapa4_guardar_pitch(request):
    _, team, progress = build_game_context(request)
    project = ensure_project_from_progress(progress)
    if not project:
        return JsonResponse({"ok": False, "msg": "No hay proyecto seleccionado"}, status=400)
    payload = json.loads(request.body.decode("utf-8") or "{}")
    pitch, _ = Pitch.objects.get_or_create(proyecto=project)
    pitch.nombre_producto   = (payload.get("nombre_producto")   or "")[:40]
    pitch.desafio_empatia   = (payload.get("desafio_empatia")   or "")[:220]
    pitch.campo_creatividad = (payload.get("campo_creatividad") or "")[:220]
    pitch.cierre            = (payload.get("cierre")            or "")[:160]
    # Auto-generate guion as concatenation (backward compatibility)
    pitch.guion = "\n\n".join(filter(None, [
        pitch.nombre_producto,
        pitch.desafio_empatia,
        pitch.campo_creatividad,
        pitch.cierre,
    ]))
    pitch.save()
    # Mark completed but do NOT advance stage or compute tokens yet
    progress.etapa4_completed = True
    progress.save(update_fields=["etapa4_completed", "updated_at"])
    return JsonResponse({"ok": True, "redirect_url": reverse("espera_etapa", args=[4])})


def inicio_juego(request):
    return render(request, "etapasJuego/inicio_juego.html", {"sesion": None})


# ---------------------------------------------------------------------------
# Pantalla de espera y cierre sincronizado de etapa
# ---------------------------------------------------------------------------

# Maps etapa_num → stage marker used in GameSession.etapa_actual
_STAGE_CLOSED_MARKER = {
    1: "ETAPA1_CLOSED",
    2: "ETAPA2_CLOSED",
    3: "ETAPA3_CLOSED",
    4: "ETAPA4_CLOSED",
}

# Fields on TeamStageProgress that signal completion of each stage
_STAGE_COMPLETED_FIELD = {
    1: "etapa1_completed",
    2: "etapa2_completed",
    3: "etapa3_completed",
    4: "etapa4_completed",
}

# What stage/route to advance to after each stage closes
_NEXT_STAGE_MAP = {
    1: (TeamStageProgress.STAGE_HISTORIA, "inicioHistoria"),
    2: (TeamStageProgress.STAGE_ETAPA3, "etapa3"),
    3: (TeamStageProgress.STAGE_ETAPA4, "etapa4"),
    4: (TeamStageProgress.STAGE_COEVALUACION, "etapaFinal:negociacion"),
}

# Current stage for each etapa (to know which TeamStageProgress records to advance)
_CURRENT_STAGE_FOR = {
    1: TeamStageProgress.STAGE_ETAPA1,
    2: TeamStageProgress.STAGE_ETAPA2_MAPA,
    3: TeamStageProgress.STAGE_ETAPA3,
    4: TeamStageProgress.STAGE_ETAPA4,
}

# Ranking URL name for each stage
_RANKING_URL_NAME = {
    1: "etapa1_ranking",
    2: "ranking_parcial",
    3: "ranking_parcial",
    4: "ranking_parcial",
}


def espera_etapa(request, etapa_num: int):
    """Waiting screen shown when a team finishes a stage before others."""
    sesion, team, _ = build_game_context(request)
    sopa_session = team.wordsearch_sessions.order_by("-id").first()
    global_elapsed = 0
    if sopa_session and sopa_session.started_at:
        from django.utils import timezone
        global_elapsed = int((timezone.now() - sopa_session.started_at).total_seconds())
    return _render_game(request, "etapasJuego/espera_etapa.html", {
        "sesion": sesion,
        "team": team,
        "etapa_num": etapa_num,
        "global_elapsed_seconds": global_elapsed,
        "poll_url": reverse("api_stage_closed", args=[etapa_num]),
    })


@csrf_exempt
def api_stage_closed(request, etapa_num: int):
    """
    Polled by the waiting screen every 3 seconds.
    Returns {"closed": True, "ranking_url": "..."} once all teams in the session
    have completed the stage (etapaN_completed=True for all).
    On first close: runs update_tokens() for all teams, advances all stages.
    """
    sesion, team, _ = build_game_context(request)
    marker = _STAGE_CLOSED_MARKER.get(etapa_num)
    if not marker:
        return JsonResponse({"closed": False, "error": "unknown stage"})

    # Already closed → respond immediately
    if sesion.etapa_actual == marker:
        ranking_name = _RANKING_URL_NAME.get(etapa_num, "ranking_parcial")
        if etapa_num == 1:
            ranking_url = reverse("etapa1_ranking")
        else:
            ranking_url = reverse("ranking_parcial", args=[etapa_num])
        return JsonResponse({"closed": True, "ranking_url": ranking_url})

    # Check if all teams in session have completed this stage
    completed_field = _STAGE_COMPLETED_FIELD.get(etapa_num)
    all_done = not TeamStageProgress.objects.filter(
        game_session=sesion,
        **{completed_field: False},
    ).exists()

    if not all_done:
        return JsonResponse({"closed": False})

    # All done → compute tokens for every team, advance stages, mark closed
    from django.db import transaction
    with transaction.atomic():
        sesion.refresh_from_db(fields=["etapa_actual"])
        if sesion.etapa_actual == marker:
            # Another tablet beat us here — just return closed
            pass
        else:
            next_stage, next_route = _NEXT_STAGE_MAP[etapa_num]
            current_stage = _CURRENT_STAGE_FOR[etapa_num]

            for equipo in sesion.equipos.prefetch_related(
                "proyecto__mapa_empatia", "proyecto__pitch", "wordsearch_sessions",
                "evaluaciones_recibidas",
            ).all():
                equipo.update_tokens()

            for progress_obj in TeamStageProgress.objects.filter(game_session=sesion):
                if progress_obj.current_stage == current_stage:
                    progress_obj.current_stage = next_stage
                    progress_obj.current_route = next_route
                    progress_obj.save(update_fields=["current_stage", "current_route", "updated_at"])

            sesion.etapa_actual = marker
            sesion.save(update_fields=["etapa_actual"])

    if etapa_num == 1:
        ranking_url = reverse("etapa1_ranking")
    else:
        ranking_url = reverse("ranking_parcial", args=[etapa_num])
    return JsonResponse({"closed": True, "ranking_url": ranking_url})


def api_ranking_overlay(request, etapa_num: int):
    """JSON ranking data consumed by the floating overlay in espera_etapa."""
    sesion, team, _ = build_game_context(request)

    _next_urls = {
        1: reverse("inicioHistoria"),
        2: reverse("etapa3"),
        3: reverse("etapa4"),
        4: reverse("etapaFinal:negociacion"),
    }
    _stage_labels = {
        1: "Sopa de Letras",
        2: "Mapa de Empatía",
        3: "Creación con Lego",
        4: "Pitch",
    }

    if etapa_num == 2:
        order_fields = ("-tokens_empatia", "-tokens_totales", "nombre")
    elif etapa_num in (3, 4):
        order_fields = ("-tokens_creatividad", "-tokens_totales", "nombre")
    else:
        order_fields = ("-tokens_evaluacion", "-tokens_totales", "nombre")

    equipos = list(
        sesion.equipos
        .prefetch_related("wordsearch_sessions")
        .order_by(*order_fields)
    )

    def _latest_sopa(eq):
        """Returns the most recent wordsearch session using the prefetch cache."""
        sessions = sorted(eq.wordsearch_sessions.all(), key=lambda s: s.id, reverse=True)
        return sessions[0] if sessions else None

    # For etapa 1, secondary sort by elapsed time (faster beats ties)
    if etapa_num == 1:
        def _sort_key(eq):
            sopa = _latest_sopa(eq)
            elapsed = sopa.elapsed_seconds if sopa and sopa.elapsed_seconds is not None else 9_999_999
            return (-eq.tokens_evaluacion, elapsed)
        equipos.sort(key=_sort_key)

    entries = []
    for i, equipo in enumerate(equipos):
        if etapa_num == 2:
            score = equipo.tokens_empatia
        elif etapa_num in (3, 4):
            score = equipo.tokens_creatividad
        else:
            score = equipo.tokens_evaluacion

        entry = {
            "position": i + 1,
            "team_id": equipo.id,
            "team_name": equipo.nombre,
            "is_mine": equipo.id == team.id,
            "tokens_totales": equipo.tokens_totales,
            "score": score,
        }

        if etapa_num == 1:
            sopa = _latest_sopa(equipo)
            entry["elapsed_label"] = _format_elapsed(sopa.elapsed_seconds if sopa else None)
            entry["progress_pct"] = round(sopa.progress_pct if sopa else 0)

        entries.append(entry)

    return JsonResponse({
        "ok": True,
        "etapa_num": etapa_num,
        "stage_label": _stage_labels.get(etapa_num, f"Etapa {etapa_num}"),
        "next_url": _next_urls.get(etapa_num, reverse("etapas_index")),
        "team_id": team.id,
        "entries": entries,
    })


def ranking_parcial(request, etapa_num: int):
    """Generic partial ranking shown after each stage closes."""
    sesion, team, _ = build_game_context(request)
    next_urls = {
        1: reverse("inicioHistoria"),
        2: reverse("etapa3"),
        3: reverse("etapa4"),
        4: reverse("etapaFinal:negociacion"),
    }
    if etapa_num == 2:
        order_fields = ("-tokens_empatia", "-tokens_totales", "nombre")
    elif etapa_num in (3, 4):
        order_fields = ("-tokens_creatividad", "-tokens_totales", "nombre")
    else:
        order_fields = ("-tokens_totales", "nombre")
    equipos = list(sesion.equipos.all().order_by(*order_fields))
    return _render_game(request, "etapasJuego/ranking_parcial.html", {
        "sesion": sesion,
        "team": team,
        "etapa_num": etapa_num,
        "equipos": equipos,
        "next_url": next_urls.get(etapa_num, reverse("etapas_index")),
        "auto_advance_seconds": 12,
    })


# ---------------------------------------------------------------------------
# Stage timeup endpoints for etapas 2, 3, 4
# ---------------------------------------------------------------------------

@csrf_exempt
def api_etapa2_timeup(request):
    """Called when stage 2 timer expires. Saves existing map state, marks completed."""
    _, team, progress = build_game_context(request)
    progress.etapa2_completed = True
    progress.save(update_fields=["etapa2_completed", "updated_at"])
    return JsonResponse({"ok": True, "redirect_url": reverse("espera_etapa", args=[2])})


@csrf_exempt
def api_etapa3_timeup(request):
    """Called when stage 3 timer expires. Marks completed with whatever was saved."""
    _, team, progress = build_game_context(request)
    progress.etapa3_completed = True
    progress.save(update_fields=["etapa3_completed", "updated_at"])
    return JsonResponse({"ok": True, "redirect_url": reverse("espera_etapa", args=[3])})


@csrf_exempt
def api_etapa4_timeup(request):
    """Called when stage 4 timer expires. Marks completed with whatever was saved."""
    _, team, progress = build_game_context(request)
    progress.etapa4_completed = True
    progress.save(update_fields=["etapa4_completed", "updated_at"])
    return JsonResponse({"ok": True, "redirect_url": reverse("espera_etapa", args=[4])})


# ---------------------------------------------------------------------------
# APIs mock — wordsearch.js y otros JS los consumen con fetch()
# ---------------------------------------------------------------------------

@csrf_exempt
def api_init(request):
    sesion, team, _ = build_game_context(request)
    stage1_session = TeamGameSession.objects.filter(equipo=team, ended_at__isnull=True).order_by("-id").first()
    if not stage1_session:
        words = list(sesion.palabras_sopa) if sesion.palabras_sopa else DEFAULT_SOPA_WORDS
        soup, positions = generate_board(words, size=12)
        stage1_session = TeamGameSession.objects.create(
            team_id=f"team:{team.id}",
            equipo=team,
            board_size=12,
            words=words,
            soup=soup,
            dict_word_position=positions,
            active_selections={},
            locked_cells=[],
        )
    return JsonResponse({
        "ok": True,
        "success": True,
        "status": stage1_session.status,
        "team_id": stage1_session.team_id,
        "board_size": stage1_session.board_size,
        "soup": stage1_session.soup,
        "words": stage1_session.words,
        "found_words": stage1_session.found_words,
        "progress_pct": stage1_session.progress_pct,
        "ready_at": stage1_session.ready_at.isoformat() if stage1_session.ready_at else None,
        "ready": stage1_session.status == TeamGameSession.STATUS_PLAYING,
        "ended": stage1_session.status in (TeamGameSession.STATUS_FINISHED, TeamGameSession.STATUS_TIME_UP),
    })


@csrf_exempt
def api_stage1_start(request):
    _, team, _ = build_game_context(request)
    stage1_session = TeamGameSession.objects.filter(equipo=team, ended_at__isnull=True).order_by("-id").first()
    if not stage1_session:
        sesion, team, _ = build_game_context(request)
        words = list(sesion.palabras_sopa) if sesion.palabras_sopa else DEFAULT_SOPA_WORDS
        soup, positions = generate_board(words, size=12)
        stage1_session = TeamGameSession.objects.create(
            team_id=f"team:{team.id}",
            equipo=team,
            board_size=12,
            words=words,
            soup=soup,
            dict_word_position=positions,
            active_selections={},
            locked_cells=[],
        )
    stage1_session.mark_started()
    stage1_session.save()
    return JsonResponse({
        "ok": True,
        "status": stage1_session.status,
        "ready_at": stage1_session.ready_at.isoformat() if stage1_session.ready_at else None,
    })


@csrf_exempt
def api_stage1_timeup(request):
    _, team, progress = build_game_context(request)
    stage1_session = TeamGameSession.objects.filter(equipo=team, ended_at__isnull=True).order_by("-id").first()
    if stage1_session:
        stage1_session.mark_time_up()
        stage1_session.save()
    # Mark stage completed but do NOT advance stage or compute tokens yet
    # (synchronized in api_stage_closed after all teams finish)
    progress.etapa1_completed = True
    progress.save(update_fields=["etapa1_completed", "updated_at"])
    return JsonResponse({
        "ok": True,
        "status": "TIME_UP",
        "redirect_url": reverse("espera_etapa", args=[1]),
    })


def api_stage1_ranking(request):
    sesion, _, _ = build_game_context(request)
    sessions = (
        TeamGameSession.objects
        .filter(equipo__sesion=sesion)
        .select_related("equipo")
        .order_by("-progress_pct", "elapsed_seconds", "equipo__nombre")
    )
    entries = _build_ranking_entries(sessions)
    all_finished = all(
        e["status"] in (TeamGameSession.STATUS_FINISHED, TeamGameSession.STATUS_TIME_UP)
        for e in entries
    ) if entries else False
    return JsonResponse({
        "ok": True,
        "success": True,
        "teams": entries,
        "ranking": entries,
        "all_finished": all_finished,
    })


@csrf_exempt
def api_select_start(request):
    _, team, _ = build_game_context(request)
    session = TeamGameSession.objects.filter(equipo=team, ended_at__isnull=True).order_by("-id").first()
    if not session or session.status != TeamGameSession.STATUS_PLAYING:
        return JsonResponse({"ok": False, "error": "session not playing"})

    payload = json.loads(request.body.decode() or "{}")
    start = payload.get("start")  # [r, c]
    color = payload.get("color", "#fb7185")
    if not start or len(start) != 2:
        return JsonResponse({"ok": False, "error": "invalid start"})

    sel_id = secrets.token_hex(4)
    selections = dict(session.active_selections or {})
    selections[sel_id] = {"path": [start], "color": color}
    session.active_selections = selections
    session.locked_cells = _compute_locked(selections)
    session.save(update_fields=["active_selections", "locked_cells"])

    return JsonResponse({
        "ok": True,
        "selection_id": sel_id,
        "active_selections": session.active_selections,
        "locked_cells": session.locked_cells,
    })


@csrf_exempt
def api_select_extend(request):
    _, team, _ = build_game_context(request)
    session = TeamGameSession.objects.filter(equipo=team, ended_at__isnull=True).order_by("-id").first()
    if not session or session.status != TeamGameSession.STATUS_PLAYING:
        return JsonResponse({"ok": False, "error": "session not playing"})

    payload = json.loads(request.body.decode() or "{}")
    sel_id = payload.get("selection_id")
    new_cell = payload.get("cell")  # [r, c]

    selections = dict(session.active_selections or {})
    info = selections.get(sel_id)
    if not info or not new_cell:
        return JsonResponse({"ok": True, "active_selections": selections, "locked_cells": session.locked_cells})

    path = list(info.get("path", []))
    if _is_valid_extension(path, new_cell):
        path.append(new_cell)
        info["path"] = path
        selections[sel_id] = info
        session.active_selections = selections
        session.locked_cells = _compute_locked(selections)
        session.save(update_fields=["active_selections", "locked_cells"])

    return JsonResponse({
        "ok": True,
        "active_selections": session.active_selections,
        "locked_cells": session.locked_cells,
    })


@csrf_exempt
def api_select_commit(request):
    _, team, progress = build_game_context(request)
    session = TeamGameSession.objects.filter(equipo=team, ended_at__isnull=True).order_by("-id").first()
    if not session:
        return JsonResponse({"ok": False, "error": "no session"})

    payload = json.loads(request.body.decode() or "{}")
    sel_id = payload.get("selection_id")

    selections = dict(session.active_selections or {})
    info = selections.pop(sel_id, None)

    result = "not_found"
    found_word = None

    if info and session.status == TeamGameSession.STATUS_PLAYING:
        path = [list(c) for c in info.get("path", [])]
        word_candidate = "".join(
            session.soup[r][c] for r, c in path
            if 0 <= r < len(session.soup) and 0 <= c < len(session.soup[0])
        )
        # Check against stored positions (forward and reversed)
        for word, positions in session.dict_word_position.items():
            if word in (session.found_words or []):
                continue
            if path == positions or path == list(reversed(positions)):
                session.mark_found(word)
                found_word = word
                result = "found"
                break

    session.active_selections = selections
    session.locked_cells = _compute_locked(selections)
    session.save()

    ended = session.status in (TeamGameSession.STATUS_FINISHED, TeamGameSession.STATUS_TIME_UP)
    redirect_url = None

    if ended and result == "found":
        # All words found → mark stage completed and redirect to waiting screen
        progress.etapa1_completed = True
        progress.save(update_fields=["etapa1_completed", "updated_at"])
        redirect_url = reverse("espera_etapa", args=[1])

    return JsonResponse({
        "ok": True,
        "result": result,
        "word": found_word,
        "found_words": list(session.found_words or []),
        "progress_pct": session.progress_pct,
        "status": session.status,
        "ended": ended,
        "redirect_url": redirect_url,
        "active_selections": session.active_selections,
        "locked_cells": session.locked_cells,
    })


@csrf_exempt
def api_reset(request):
    return JsonResponse({"ok": True})


# ---------------------------------------------------------------------------
# Word-search selection helpers
# ---------------------------------------------------------------------------

def _is_valid_extension(path: list, new_cell: list) -> bool:
    """Return True if new_cell continues linearly from path's established direction."""
    new_r, new_c = new_cell[0], new_cell[1]
    if not path:
        return True
    last = path[-1]
    if [new_r, new_c] == last:
        return False  # same cell
    if len(path) == 1:
        return True  # any neighbor establishes direction
    # Direction already established — new cell must continue it
    dr = path[1][0] - path[0][0]
    dc = path[1][1] - path[0][1]
    expected_r = last[0] + dr
    expected_c = last[1] + dc
    return new_r == expected_r and new_c == expected_c


def _compute_locked(selections: dict) -> list:
    """Return list of [r, c] cells currently occupied by any active selection."""
    locked = []
    seen = set()
    for info in selections.values():
        for cell in info.get("path", []):
            key = (cell[0], cell[1])
            if key not in seen:
                seen.add(key)
                locked.append(cell)
    return locked
