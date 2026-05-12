from django.db import transaction
from django.shortcuts import redirect
from django.utils.cache import add_never_cache_headers

from .models import (
    Challenge,
    Desafio,
    GameSession,
    Project,
    Tablet,
    TabletSessionAssignment,
    Team,
    TeamStageProgress,
)


STAGE_ROUTES = {
    TeamStageProgress.STAGE_ROMPEHIELO: "rompehielo",
    TeamStageProgress.STAGE_ETAPA1: "etapa1",
    TeamStageProgress.STAGE_HISTORIA: "inicioHistoria",
    TeamStageProgress.STAGE_ETAPA2: "etapa2",
    TeamStageProgress.STAGE_ETAPA2_MAPA: "etapa2_1",
    TeamStageProgress.STAGE_ETAPA3: "etapa3",
    TeamStageProgress.STAGE_ETAPA4: "etapa4",
    TeamStageProgress.STAGE_COEVALUACION: "etapaFinal:negociacion",
    TeamStageProgress.STAGE_RESULTADOS: "etapaFinal:cierre_final",
}

STAGE_ORDER = {
    TeamStageProgress.STAGE_ROMPEHIELO: 0,
    TeamStageProgress.STAGE_ETAPA1: 1,
    TeamStageProgress.STAGE_HISTORIA: 2,
    TeamStageProgress.STAGE_ETAPA2: 3,
    TeamStageProgress.STAGE_ETAPA2_MAPA: 4,
    TeamStageProgress.STAGE_ETAPA3: 5,
    TeamStageProgress.STAGE_ETAPA4: 6,
    TeamStageProgress.STAGE_COEVALUACION: 7,
    TeamStageProgress.STAGE_RESULTADOS: 8,
}


def get_current_gamesession_for_tablet(request, tablet=None):
    session_id = request.session.get("game_session_id") or request.GET.get("game_session_id")
    code = request.session.get("game_session_code") or request.GET.get("game_session_code")

    queryset = GameSession.objects.all().order_by("-id")
    if session_id:
        found = queryset.filter(id=session_id).first()
        if found:
            return found
    if code:
        found = queryset.filter(codigo=code).first()
        if found:
            request.session["game_session_id"] = found.id
            return found
    if tablet and tablet.sesion_id:
        request.session["game_session_id"] = tablet.sesion_id
        return tablet.sesion

    # Fallback de desarrollo: el PIN de tablet actual no identifica sesión.
    # En producción, el login debería guardar game_session_id o game_session_code.
    found = queryset.first()
    if found:
        request.session["game_session_id"] = found.id
        return found

    return GameSession.objects.create(nombre="Sesión demo", codigo="DEMO")


def _next_team_code(game_session):
    used = set(Team.objects.filter(sesion=game_session).values_list("codigo_grupo", flat=True))
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if letter not in used:
            return letter
    return "Z"


@transaction.atomic
def get_or_create_team_for_request(request):
    team_id = request.session.get("team_id")
    game_session_id = request.session.get("game_session_id")

    if team_id:
        team = Team.objects.select_related("sesion", "tablet").filter(id=team_id).first()
        if team and (not game_session_id or team.sesion_id == game_session_id):
            request.session["game_session_id"] = team.sesion_id
            return team

    tablet = None
    tablet_id = request.session.get("tablet_id") or request.GET.get("tablet_id")
    if tablet_id:
        tablet = Tablet.objects.filter(id=tablet_id).first()
        if tablet:
            request.session["tablet_id"] = tablet.id

    game_session = get_current_gamesession_for_tablet(request, tablet)

    if tablet:
        assignment = (
            TabletSessionAssignment.objects.select_related("team")
            .filter(tablet=tablet, game_session=game_session, active=True)
            .first()
        )
        if assignment:
            request.session["team_id"] = assignment.team_id
            request.session["game_session_id"] = game_session.id
            return assignment.team

        team = Team.objects.create(
            nombre=f"Equipo {_next_team_code(game_session)}",
            sesion=game_session,
            codigo_grupo=_next_team_code(game_session),
        )
        TabletSessionAssignment.objects.create(tablet=tablet, game_session=game_session, team=team)
        request.session["team_id"] = team.id
        request.session["game_session_id"] = game_session.id
        return team

    team = Team.objects.filter(sesion=game_session).order_by("id").first()
    if not team:
        code = _next_team_code(game_session)
        team = Team.objects.create(nombre=f"Equipo {code}", sesion=game_session, codigo_grupo=code)
    request.session["team_id"] = team.id
    request.session["game_session_id"] = game_session.id
    return team


def get_progress_for_team(team):
    progress, _ = TeamStageProgress.objects.get_or_create(
        team=team,
        defaults={
            "game_session": team.sesion,
            "current_stage": TeamStageProgress.STAGE_ROMPEHIELO,
            "current_route": STAGE_ROUTES[TeamStageProgress.STAGE_ROMPEHIELO],
        },
    )
    if progress.game_session_id != team.sesion_id:
        progress.game_session = team.sesion
        progress.save(update_fields=["game_session", "updated_at"])
    return progress


def set_current_stage(team, stage, route=None):
    progress = get_progress_for_team(team)
    progress.current_stage = stage
    progress.current_route = route or STAGE_ROUTES[stage]
    progress.save(update_fields=["current_stage", "current_route", "updated_at"])
    return progress


def advance_to_stage(team, stage, route=None, completed_field=None):
    progress = get_progress_for_team(team)
    if completed_field:
        setattr(progress, completed_field, True)
    progress.current_stage = stage
    progress.current_route = route or STAGE_ROUTES[stage]
    fields = ["current_stage", "current_route", "updated_at"]
    if completed_field:
        fields.append(completed_field)
    progress.save(update_fields=fields)
    return progress


def get_redirect_for_progress(progress):
    return redirect(progress.current_route)


def ensure_project_from_progress(progress):
    if progress.project:
        return progress.project
    if hasattr(progress.team, "proyecto"):
        progress.project = progress.team.proyecto
        progress.save(update_fields=["project", "updated_at"])
        return progress.project
    if not progress.selected_challenge:
        return None
    project, _ = Project.objects.get_or_create(
        equipo=progress.team,
        defaults={
            "desafio": progress.selected_challenge,
            "selected_desafio": progress.selected_desafio,
        },
    )
    changed = False
    if project.desafio_id != progress.selected_challenge_id:
        project.desafio = progress.selected_challenge
        changed = True
    if progress.selected_desafio_id and project.selected_desafio_id != progress.selected_desafio_id:
        project.selected_desafio = progress.selected_desafio
        changed = True
    if changed:
        project.save()
    progress.project = project
    progress.save(update_fields=["project", "updated_at"])
    return project


def build_game_context(request):
    team = get_or_create_team_for_request(request)
    progress = get_progress_for_team(team)
    return team.sesion, team, progress


def require_stage(request, expected_stage):
    if request.method != "GET":
        return None
    _, team, progress = build_game_context(request)
    if progress.current_stage != expected_stage:
        return get_redirect_for_progress(progress)
    return None


def redirect_if_stage_is_past(request, page_stage):
    if request.method != "GET":
        return None
    _, _, progress = build_game_context(request)
    if STAGE_ORDER.get(progress.current_stage, 0) > STAGE_ORDER.get(page_stage, 0):
        return get_redirect_for_progress(progress)
    return None


def never_cache(response):
    add_never_cache_headers(response)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


def parse_selected_challenge(topic_id, challenge_id, desafio_id):
    challenge = Challenge.objects.select_related("topic").get(id=challenge_id, topic_id=topic_id, activo=True)
    desafio = Desafio.objects.get(id=desafio_id, challenge=challenge, activo=True)
    return challenge.topic, challenge, desafio
