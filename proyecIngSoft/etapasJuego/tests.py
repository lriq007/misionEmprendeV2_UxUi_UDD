import json

from django.test import TestCase
from django.urls import reverse

from .models import GameSession, Team, Tablet, TeamGameSession
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


class Stage1RankingTests(TestCase):
    def setUp(self):
        self.game_session = GameSession.objects.create(nombre="Sesion Test", codigo="TEST01")
        self.tablet = Tablet.objects.create(codigo="Tablet A", sesion=self.game_session)
        self.team = Team.objects.create(
            nombre="Equipo A",
            sesion=self.game_session,
            codigo_grupo="A",
            tablet=self.tablet,
        )
        session = self.client.session
        session["tablet_id"] = self.tablet.id
        session["team_id"] = self.team.id
        session.save()

    def test_stage1_start_marks_session_as_playing(self):
        self.client.post(
            reverse("api_init"),
            data=json.dumps({}),
            content_type="application/json",
        )

        response = self.client.post(reverse("api_stage1_start"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], TeamGameSession.STATUS_PLAYING)
        tgs = TeamGameSession.objects.get(equipo=self.team, ended_at__isnull=True)
        self.assertIsNotNone(tgs.ready_at)
        self.assertEqual(tgs.status, TeamGameSession.STATUS_PLAYING)

    def test_stage1_ranking_includes_connected_team(self):
        TeamGameSession.objects.create(
            team_id=f"team:{self.team.id}",
            equipo=self.team,
            words=["A"],
            soup=[["A"]],
            dict_word_position={"A": [[0, 0]]},
            progress_pct=100.0,
            status=TeamGameSession.STATUS_FINISHED,
            elapsed_seconds=120,
        )

        response = self.client.get(reverse("api_stage1_ranking"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["success"], True)
        self.assertEqual(len(payload["teams"]), 1)
        self.assertEqual(payload["teams"][0]["team_name"], "Equipo A")
        self.assertEqual(payload["teams"][0]["status"], TeamGameSession.STATUS_FINISHED)
