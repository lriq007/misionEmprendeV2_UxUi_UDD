from typing import Optional

from django.conf import settings
from openai import AuthenticationError, OpenAI, OpenAIError

from etapasJuego.models import Challenge, Desafio, EmpathyMap, Pitch, Topic


_PLACEHOLDER_KEYS = {"", "tu_api_key_aqui", "your_api_key_here"}


def _safe(val):
    return val or ""


def _api_key_configured() -> bool:
    api_key = (getattr(settings, "OPENAI_API_KEY", "") or "").strip()
    return api_key not in _PLACEHOLDER_KEYS


client = OpenAI(api_key=settings.OPENAI_API_KEY) if _api_key_configured() else None


def ia_pitch_disponible() -> bool:
    return client is not None


def generar_sugerencias_pitch(
    topic: Optional[Topic],
    challenge: Optional[Challenge],
    desafio: Optional[Desafio],
    mapa: Optional[EmpathyMap],
) -> str:
    """
    Genera tres puntos de apoyo para el pitch usando OpenAI.
    Si la integracion no esta disponible, devuelve string vacio.
    """
    if client is None:
        return ""

    tema_nombre = _safe(getattr(topic, "nombre", ""))
    tema_desc = _safe(getattr(topic, "descripcion", ""))

    challenge_titulo = _safe(getattr(challenge, "titulo", ""))
    challenge_desc = _safe(getattr(challenge, "descripcion", ""))

    personaje = _safe(getattr(desafio, "personaje", ""))
    historia = _safe(getattr(desafio, "historia", ""))

    gustos = _safe(getattr(mapa, "gustos", ""))
    problemas = _safe(getattr(mapa, "problemas", ""))
    miedos = _safe(getattr(mapa, "miedos", ""))
    contexto = _safe(getattr(mapa, "contexto", ""))
    hobbies = _safe(getattr(mapa, "hobbies", ""))

    prompt = f"""
Eres un asistente experto en pitch y storytelling para estudiantes hispanohablantes. Ayuda a sintetizar un pitch breve basado en el mapa de empatia y el contexto del desafio.

Contexto del tema:
- Nombre del tema: {tema_nombre}
- Descripcion del tema: {tema_desc}

Contexto del desafio:
- Titulo del desafio: {challenge_titulo}
- Descripcion del desafio: {challenge_desc}

Personaje/usuario:
- Nombre/personaje: {personaje}
- Historia / descripcion breve: {historia}

Mapa de empatia (insumos clave):
- Gustos: {gustos}
- Problemas: {problemas}
- Miedos: {miedos}
- Contexto: {contexto}
- Hobbies: {hobbies}

Con esta informacion, devuelve exactamente 3 ideas de apoyo al pitch en este formato, una por linea y sin texto adicional:
Punto 1: ...
Punto 2: ...
Punto 3: ...
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en pitch y storytelling. Responde en espanol claro para estudiantes y entrega solo los puntos solicitados.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=350,
        )
    except (AuthenticationError, OpenAIError):
        return ""

    texto = (response.choices[0].message.content or "").strip()

    import re

    texto = re.sub(r"^Punto\s*\d+\s*:\s*", "", texto, flags=re.MULTILINE)
    return texto


def evaluar_pitch_con_ia(texto: str) -> Optional[int]:
    """
    Evalua el texto de un pitch y retorna un puntaje entero 1-5.
    Devuelve None si no hay IA disponible o si no se obtiene un valor valido.
    """
    if client is None or not texto or len(texto.strip()) < 30:
        return None

    prompt = (
        "Eres un experto en escritura, gramatica y narrativa de pitch de emprendimiento, "
        "con estandares MIT, Oxford e Imperial College. Evalua SOLO la estructura, claridad, "
        "coherencia y calidad de redaccion del siguiente pitch. Devuelve SOLO un numero entero "
        "del 1 al 5, sin ningun otro texto, palabra, explicacion ni simbolo."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": texto},
            ],
            temperature=0,
            max_tokens=5,
        )
    except (AuthenticationError, OpenAIError):
        return None

    raw = (response.choices[0].message.content or "").strip()
    try:
        value = int(raw)
    except (ValueError, TypeError):
        return None

    return value if 1 <= value <= 5 else None


def actualizar_score_ai(pitch: Pitch) -> None:
    """
    Evalua pitch.guion con IA y actualiza pitch.score_ai si se obtiene un valor valido.
    Si la IA no esta disponible, deja el score en None sin romper el flujo.
    """
    if not pitch.guion:
        pitch.score_ai = None
        return

    score = evaluar_pitch_con_ia(pitch.guion)
    if score is not None:
        pitch.score_ai = score
        pitch.save(update_fields=["score_ai"])
    else:
        pitch.score_ai = None
        pitch.save(update_fields=["score_ai"])
