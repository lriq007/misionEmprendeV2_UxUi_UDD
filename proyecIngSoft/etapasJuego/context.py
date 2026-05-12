from .models import GameSession, Team
from .progress import get_or_create_team_for_request as resolve_team


def get_current_gamesession() -> GameSession | None:
    return GameSession.objects.order_by("-id").first()


def get_or_create_team_for_request(request) -> tuple[GameSession, Team]:
    """
    Fachada legacy para vistas existentes.

    La identidad nueva se resuelve en progress.resolve_team usando
    TabletSessionAssignment como fuente persistente. request.session queda solo
    como cache de tablet_id/team_id/game_session_id.
    """
    team = resolve_team(request)
    return team.sesion, team
