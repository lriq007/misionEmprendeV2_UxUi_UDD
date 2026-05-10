import random


class RouletteEngine:
    MODALITY_NEW_TEAM = "no_se_conocen"
    MODALITY_KNOWN_TEAM = "se_conocen"

    NEW_TEAM_QUESTIONS = [
        {"id": 1, "text": "¿Qué habilidad tuya puede ayudar al equipo?", "emoji": "🤝"},
        {"id": 2, "text": "¿Qué tema te entusiasma aprender en esta misión?", "emoji": "🎯"},
        {"id": 3, "text": "¿Qué forma de trabajar te acomoda más?", "emoji": "🧭"},
        {"id": 4, "text": "¿Qué experiencia personal puede sumar al desafío?", "emoji": "✨"},
        {"id": 5, "text": "¿Qué rol te gustaría probar hoy?", "emoji": "🧩"},
        {"id": 6, "text": "¿Qué te ayuda a confiar en un equipo nuevo?", "emoji": "🌱"},
        {"id": 7, "text": "¿Qué fortaleza tuya suele aparecer bajo presión?", "emoji": "⚡"},
        {"id": 8, "text": "¿Qué esperas que tus compañeros sepan de ti para trabajar mejor?", "emoji": "💬"},
    ]

    KNOWN_TEAM_QUESTIONS = [
        {"id": 1, "text": "¿Qué problema de tu comunidad te gustaría resolver?", "emoji": "💡"},
        {"id": 2, "text": "¿Qué habilidad del equipo deberíamos aprovechar más?", "emoji": "🤝"},
        {"id": 3, "text": "Si crearas una startup hoy, ¿qué vendería?", "emoji": "🚀"},
        {"id": 4, "text": "¿Qué producto cotidiano mejorarías?", "emoji": "🛠️"},
        {"id": 5, "text": "¿Qué te motiva a emprender?", "emoji": "🔥"},
        {"id": 6, "text": "¿Qué usuario te interesa entender mejor?", "emoji": "👀"},
        {"id": 7, "text": "¿Qué tecnología usarías para crear impacto?", "emoji": "⚙️"},
        {"id": 8, "text": "¿Qué aprendizaje quieres llevarte de esta misión?", "emoji": "🎯"},
    ]
    QUESTIONS = KNOWN_TEAM_QUESTIONS

    def normalize_modality(self, modality):
        if modality == self.MODALITY_NEW_TEAM:
            return self.MODALITY_NEW_TEAM
        return self.MODALITY_KNOWN_TEAM

    def get_questions(self, modality=None):
        normalized = self.normalize_modality(modality)
        if normalized == self.MODALITY_NEW_TEAM:
            return list(self.NEW_TEAM_QUESTIONS)
        return list(self.KNOWN_TEAM_QUESTIONS)

    def select_question(self, available_ids, modality=None):
        questions = self.get_questions(modality)
        ids = set(available_ids or [])
        pool = [question for question in questions if question["id"] in ids] or questions
        return random.choice(pool)

    def handle_error(self, context):
        return {
            "success": False,
            "context": context,
            "message": "Intenta nuevamente en unos segundos.",
        }
