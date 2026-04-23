from __future__ import annotations

import random
from typing import Iterable


class RouletteEngine:
    """Stateless question catalog used by the rompehielo ruleta."""

    _QUESTIONS = [
        {"id": 1, "emoji": "🚀", "text": "¿Que habilidad tuya crees que el grupo aun no conoce?"},
        {"id": 2, "emoji": "🔥", "text": "¿Que te motiva a estudiar tu carrera hoy?"},
        {"id": 3, "emoji": "🎯", "text": "¿Que desafio te gustaria convertir en oportunidad este año?"},
        {"id": 4, "emoji": "🎧", "text": "¿Que hobby te recarga energia fuera de clases?"},
        {"id": 5, "emoji": "🤝", "text": "¿Que fortaleza aportarias a un equipo emprendedor?"},
        {"id": 6, "emoji": "🧠", "text": "¿Que experiencia te ha enseñado a resolver problemas rapido?"},
        {"id": 7, "emoji": "💡", "text": "¿Que idea de emprendimiento te gustaria explorar algun dia?"},
        {"id": 8, "emoji": "⭐", "text": "¿Que valor no puede faltar en un equipo de trabajo para ti?"},
    ]

    def get_questions(self) -> list[dict[str, object]]:
        return [question.copy() for question in self._QUESTIONS]

    def select_question(self, available_ids: Iterable[int] | None) -> dict[str, object]:
        catalog = self.get_questions()
        valid_ids = {question["id"] for question in catalog}
        requested_ids = {
            question_id
            for question_id in (available_ids or [])
            if isinstance(question_id, int) and question_id in valid_ids
        }

        pool = [question for question in catalog if question["id"] in requested_ids]
        if not pool:
            pool = catalog

        return random.choice(pool).copy()

    def handle_error(self, context: str) -> dict[str, object]:
        return {
            "success": False,
            "message": "No pudimos cargar las preguntas del rompehielo. Intenta nuevamente.",
            "context": context,
        }
