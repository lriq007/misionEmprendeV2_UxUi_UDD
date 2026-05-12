"""
Token-computation functions adapted from logicaJuegosCopy.
All functions are pure and idempotent: called multiple times they return the same result.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# ETAPA 1 — Sopa de letras  →  tokens_evaluacion
# Adapted from reglaPuntajeSopaLetras.py
# ---------------------------------------------------------------------------

def compute_sopa_tokens(team) -> int:
    """
    Position-based scoring for word search.
    Reads TeamGameSession data for the team and compares against all sessions
    in the same GameSession to compute relative position.

    5 tokens for 1st place (100%), 4 for 2nd, 3 for 3rd+
    2 tokens for ≥80%, 1 for ≥40%, 0 otherwise.
    """
    from etapasJuego.models import TeamGameSession

    my_session = team.wordsearch_sessions.order_by("-id").first()
    if not my_session or my_session.status == "PENDING":
        return 0

    pct = my_session.progress_pct
    elapsed = my_session.elapsed_seconds

    if pct >= 100 and elapsed is not None:
        faster_count = TeamGameSession.objects.filter(
            equipo__sesion=team.sesion,
            status="FINISHED",
            elapsed_seconds__lt=elapsed,
        ).count()
        position = faster_count + 1
        return 5 if position == 1 else (4 if position == 2 else 3)

    if pct >= 80:
        return 2
    if pct >= 40:
        return 1
    return 0


# ---------------------------------------------------------------------------
# ETAPA 2 — Mapa de empatía  →  tokens_empatia
# Adapted from reglaPuntajeMapaEmpatia.evaluarMapaEmpatia()
# ---------------------------------------------------------------------------

def compute_bubble_tokens(mapa) -> int:
    """
    Quality-based scoring for the empathy map.
    Reads datos_extra (JSON with lists of apéndices per field).
    Falls back to splitting the single-text fields if datos_extra is missing.

    Criteria (faithful to logicaJuegosCopy):
    - completas:   ≥1 valid apéndice (8-100 chars) per question
    - ideales:     all responded apéndices in 40-60 chars range
    - desarrolladas: ≥2 valid apéndices per question
    - superficiales: exactly 1 valid apéndice per question
    - basura:      apéndices of 1-7 chars
    - excesivas:   apéndices >100 chars

    Bonuses/penalties then applied; +1 for finalizing (always True when saved).
    bonusExcelenciaVelocidad is OMITTED (requires cross-team batch calculation).
    """
    if not mapa:
        return 0

    apendices_data = mapa.datos_extra or {}
    campos = ["gustos", "problemas", "miedos", "contexto", "hobbies"]

    # If datos_extra is missing or empty, fall back to splitting text fields
    if not any(apendices_data.get(c) for c in campos):
        apendices_data = _build_apendices_from_fields(mapa, campos)

    completas = desarrolladas = superficiales = ideales = basura = excesivas = 0

    for campo in campos:
        aps = apendices_data.get(campo, [])
        validos = []
        for ap in aps:
            length = len((ap or "").strip())
            if length == 0:
                continue
            if 1 <= length <= 7:
                basura += 1
            elif 8 <= length <= 100:
                validos.append(length)
                if 40 <= length <= 60:
                    ideales += 1
            else:  # > 100
                excesivas += 1
                validos.append(length)

        if validos:
            completas += 1
            if len(validos) == 1:
                superficiales += 1
            if len(validos) >= 2:
                desarrolladas += 1

    bonus_ideal   = 1 if ideales >= 4 else 0
    bonus_solidez = 1 if desarrolladas >= 3 else 0
    pen_superf    = 1 if superficiales >= 3 else 0
    pen_basura    = 1 if basura >= 3 else 0
    pen_exceso    = 1 if excesivas >= 3 else 0

    puntaje = max(
        0,
        completas + bonus_ideal + bonus_solidez
        - pen_superf - pen_basura - pen_exceso,
    )
    # +1 for having finalized (the act of saving counts as finalization)
    return max(0, puntaje + 1)


def _build_apendices_from_fields(mapa, campos: list[str]) -> dict:
    """Fallback: split single text fields by newline into apéndice lists."""
    field_values = {
        "gustos":    mapa.gustos or "",
        "problemas": mapa.problemas or "",
        "miedos":    mapa.miedos or "",
        "contexto":  mapa.contexto or "",
        "hobbies":   mapa.hobbies or "",
    }
    return {
        campo: [line.strip() for line in field_values[campo].split("\n") if line.strip()]
        for campo in campos
    }


# ---------------------------------------------------------------------------
# ETAPA 3 — Lego  →  tokens_creatividad
# Adapted from reglaPuntajeLego.calcularTokensLego()
# ---------------------------------------------------------------------------

def compute_lego_tokens(proyecto) -> int:
    """3 tokens if prototype image was uploaded, 0 otherwise. Faithful to logicaJuegosCopy."""
    if not proyecto:
        return 0
    return 3 if proyecto.foto_prototipo else 0


# ---------------------------------------------------------------------------
# ETAPA 4 — Pitch  →  tokens_creatividad
# Adapted from reglaPuntajePitch.calcularTokensCreacionPitch()
# ---------------------------------------------------------------------------

def compute_pitch_tokens(pitch) -> int:
    """1 token per filled field, max 4. Faithful to logicaJuegosCopy."""
    if not pitch:
        return 0
    fields = [
        pitch.nombre_producto,
        pitch.desafio_empatia,
        pitch.campo_creatividad,
        pitch.cierre,
    ]
    return sum(1 for f in fields if (f or "").strip())


# ---------------------------------------------------------------------------
# ETAPA 5 — Negociación  →  tokens_evaluacion
# Adapted from reglaPuntajeNegociacion.calcularTokensPorPromedio()
# Scale relaxed: 0/5/10/15 instead of 0/2/4/6
# ---------------------------------------------------------------------------

def compute_negociacion_tokens(team) -> int:
    """
    Converts average puntaje_equipo received (excluding self-evaluation) to tokens.
    Scale (relaxed vs logicaJuegosCopy): <2.5→0, 2.5→5, 3.5→10, ≥4.5→15
    """
    puntajes = list(
        team.evaluaciones_recibidas
        .exclude(evaluador=team)
        .values_list("puntaje_equipo", flat=True)
    )
    if not puntajes:
        return 0
    promedio = sum(puntajes) / len(puntajes)
    if promedio < 2.5:
        return 0
    if promedio < 3.5:
        return 5
    if promedio < 4.5:
        return 10
    return 15
