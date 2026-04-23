from django.test import TestCase
from django.urls import reverse

from .services import RouletteEngine


class RouletteEngineTests(TestCase):
    def setUp(self):
        self.engine = RouletteEngine()

    def test_get_questions_returns_catalog(self):
        questions = self.engine.get_questions()

        self.assertGreaterEqual(len(questions), 8)
        self.assertTrue(all("id" in question and "text" in question and "emoji" in question for question in questions))

    def test_select_question_with_empty_ids_reuses_full_catalog(self):
        selection = self.engine.select_question([])
        available_ids = {question["id"] for question in self.engine.get_questions()}

        self.assertIn(selection["id"], available_ids)

    def test_handle_error_returns_actionable_payload(self):
        payload = self.engine.handle_error("test")

        self.assertEqual(payload["success"], False)
        self.assertEqual(payload["context"], "test")
        self.assertIn("Intenta nuevamente", payload["message"])


class RompehieloViewTests(TestCase):
    def test_rompehielo_html_mode_renders_shell(self):
        response = self.client.get(reverse("rompehielo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-rompehielo-app')
        self.assertContains(response, 'data-bootstrap-url')
        self.assertContains(response, 'data-turn-button')
        self.assertContains(response, 'data-current-question')
        self.assertContains(response, 'data-question-overlay')
        self.assertContains(response, 'data-pass-button')
        self.assertTemplateUsed(response, "etapasJuego/rompehielo.html")

    def test_rompehielo_json_mode_returns_questions(self):
        response = self.client.get(
            reverse("rompehielo"),
            {"format": "json"},
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        payload = response.json()
        self.assertEqual(payload["success"], True)
        self.assertGreaterEqual(len(payload["questions"]), 8)
        self.assertTrue(all("id" in question and "text" in question and "emoji" in question for question in payload["questions"]))
