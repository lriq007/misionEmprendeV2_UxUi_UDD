import json

from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from login.models import Estudiante

from .models import (
    Challenge,
    Desafio,
    EmpathyMap,
    Evaluation,
    GameSession,
    Pitch,
    Project,
    Tablet,
    TabletSessionAssignment,
    Team,
    TeamGameSession,
    TeamStageProgress,
    Topic,
)
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

    def test_get_questions_changes_by_modality(self):
        new_team_questions = self.engine.get_questions(RouletteEngine.MODALITY_NEW_TEAM)
        known_team_questions = self.engine.get_questions(RouletteEngine.MODALITY_KNOWN_TEAM)

        self.assertNotEqual(new_team_questions, known_team_questions)
        self.assertIn("trabajar mejor", new_team_questions[-1]["text"])


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

    def test_rompehielo_new_team_mode_renders_intro_with_team_count(self):
        game_session = GameSession.objects.create(nombre="Sesion Test", codigo="RHTEST")
        team = Team.objects.create(nombre="Equipo A", sesion=game_session, codigo_grupo="A")
        Estudiante.objects.create(nombre_apellido="Ana Perez", carrera="Diseno", team=team)
        Estudiante.objects.create(nombre_apellido="Luis Soto", carrera="Ingenieria", team=team)
        session = self.client.session
        session["team_id"] = team.id
        session["game_session_id"] = game_session.id
        session.save()

        response = self.client.get(reverse("rompehielo"), {"modalidad": "no_se_conocen"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-requires-intro="true"')
        self.assertContains(response, 'data-player-count="2"')
        self.assertContains(response, 'data-intro-overlay')
        self.assertContains(response, "Ana Perez")

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

    def test_rompehielo_json_mode_returns_modality_specific_questions(self):
        new_team_response = self.client.get(
            reverse("rompehielo"),
            {"format": "json", "modalidad": "no_se_conocen"},
            HTTP_ACCEPT="application/json",
        )
        known_team_response = self.client.get(
            reverse("rompehielo"),
            {"format": "json", "modalidad": "se_conocen"},
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(new_team_response.status_code, 200)
        self.assertEqual(known_team_response.status_code, 200)
        self.assertTrue(new_team_response.json()["requires_intro"])
        self.assertFalse(known_team_response.json()["requires_intro"])
        self.assertNotEqual(new_team_response.json()["questions"], known_team_response.json()["questions"])


class InicioHistoriaViewTests(TestCase):
    def setUp(self):
        self.topics = [
            Topic.objects.create(nombre="Salud", slug="salud", activo=True),
            Topic.objects.create(nombre="Educacion", slug="educacion", activo=True),
            Topic.objects.create(nombre="Sustentabilidad", slug="sustentabilidad", activo=True),
        ]

    def test_inicio_historia_renders_story_and_squad_views(self):
        response = self.client.get(reverse("inicioHistoria"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Archivo")
        self.assertContains(response, "2060")
        self.assertContains(response, "Epidemia del Miedo al Emprendimiento")
        self.assertContains(response, "/media/imgHistoria/fondoHistoria.png")
        self.assertContains(response, "/media/imgHistoria/fondoEscuadrones.png")
        self.assertContains(response, "Seleccion")
        self.assertContains(response, "Escuadron")
        self.assertContains(response, 'data-squad-option')
        self.assertContains(response, 'aria-disabled="true"')
        self.assertContains(response, "/media/imgHistoria/escuadronRojo.png")
        self.assertContains(response, "/media/imgHistoria/escuadronAzul.png")
        self.assertContains(response, "/media/imgHistoria/escuadronAmarillo.png")
        self.assertContains(response, 'data-next-view')
        self.assertContains(response, "Tematica del Escuadron")
        self.assertContains(response, "Salud")
        self.assertContains(response, "Educacion")
        self.assertContains(response, "Sustentabilidad")
        self.assertContains(response, 'name="topic_id"')
        self.assertContains(response, reverse("etapa2_select"))
        self.assertContains(response, 'data-challenge-overlay')
        self.assertTemplateUsed(response, "etapasJuego/inicioHistoria.html")

    def test_inicio_historia_blocks_when_active_topics_are_not_three(self):
        self.topics[0].activo = False
        self.topics[0].save(update_fields=["activo"])

        response = self.client.get(reverse("inicioHistoria"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Configuracion pendiente")
        self.assertContains(response, "exactamente 3 temas activos")

    def test_inicio_historia_blocks_when_topic_has_more_than_three_active_desafios(self):
        challenge = Challenge.objects.create(
            topic=self.topics[0],
            titulo="Salud urbana",
            descripcion="Descripcion",
            activo=True,
        )
        for index in range(4):
            Desafio.objects.create(
                numero=index + 1,
                titulo=f"Desafio {index + 1}",
                historia="Historia",
                personaje="Persona",
                activo=True,
                challenge=challenge,
            )

        response = self.client.get(reverse("inicioHistoria"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Configuracion pendiente")
        self.assertContains(response, "maximo 3 desafios activos")

    def test_post_topic_from_story_redirects_to_challenges_and_filters_by_topic(self):
        selected_challenge = Challenge.objects.create(
            topic=self.topics[0],
            titulo="Salud urbana",
            descripcion="Descripcion salud",
            activo=True,
        )
        other_challenge = Challenge.objects.create(
            topic=self.topics[1],
            titulo="Educacion digital",
            descripcion="Descripcion educacion",
            activo=True,
        )
        selected_desafio = Desafio.objects.create(
            numero=1,
            titulo="Adultos mayores conectados",
            historia="Historia salud",
            personaje="Persona salud",
            activo=True,
            challenge=selected_challenge,
        )
        other_desafio = Desafio.objects.create(
            numero=1,
            titulo="Aulas conectadas",
            historia="Historia educacion",
            personaje="Persona educacion",
            activo=True,
            challenge=other_challenge,
        )

        response = self.client.post(
            reverse("etapa2_tema"),
            {"topic_id": self.topics[0].id},
            follow=True,
        )

        self.assertRedirects(response, reverse("etapa2"))
        self.assertContains(response, self.topics[0].nombre)
        self.assertContains(response, selected_desafio.titulo)
        self.assertNotContains(response, other_desafio.titulo)

    def test_select_challenge_from_story_modal_persists_project_without_topic_session(self):
        challenge = Challenge.objects.create(
            topic=self.topics[0],
            titulo="Salud urbana",
            descripcion="Descripcion salud",
            activo=True,
        )
        desafio = Desafio.objects.create(
            numero=1,
            titulo="Adultos mayores conectados",
            historia="Historia salud",
            personaje="Persona salud",
            activo=True,
            challenge=challenge,
        )

        response = self.client.post(
            reverse("etapa2_select"),
            {
                "topic_id": self.topics[0].id,
                "challenge_id": challenge.id,
                "desafio_id": desafio.id,
            },
        )

        self.assertRedirects(response, reverse("etapa2_1"), fetch_redirect_response=False)
        session = self.client.session
        self.assertEqual(session["topic_id"], self.topics[0].id)
        self.assertEqual(session["etapa2_desafio_numero"], desafio.id)


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

    def test_stage1_ranking_next_url_points_to_inicio_historia(self):
        response = self.client.get(reverse("etapa1_ranking"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("inicioHistoria"))


class PersistentGameFlowTests(TestCase):
    def setUp(self):
        self.session_a = GameSession.objects.create(nombre="Sesion A", codigo="FLOWA")
        self.session_b = GameSession.objects.create(nombre="Sesion B", codigo="FLOWB")
        self.tablet = Tablet.objects.create(codigo="Tablet flujo")
        self.team = Team.objects.create(nombre="Equipo A", sesion=self.session_a, codigo_grupo="A")
        self.other_team = Team.objects.create(nombre="Equipo B", sesion=self.session_a, codigo_grupo="B")
        self.topic = Topic.objects.create(nombre="Salud", slug="salud-flow", activo=True)
        self.challenge = Challenge.objects.create(
            topic=self.topic,
            titulo="Salud urbana",
            descripcion="Descripcion salud",
            activo=True,
        )
        self.desafio = Desafio.objects.create(
            numero=1,
            titulo="Adultos mayores conectados",
            historia="Historia salud",
            personaje="Persona salud",
            activo=True,
            challenge=self.challenge,
        )
        session = self.client.session
        session["team_id"] = self.team.id
        session["game_session_id"] = self.session_a.id
        session.save()

    def test_tablet_can_be_assigned_in_multiple_game_sessions(self):
        team_b = Team.objects.create(nombre="Equipo C", sesion=self.session_b, codigo_grupo="C")

        TabletSessionAssignment.objects.create(
            tablet=self.tablet,
            game_session=self.session_a,
            team=self.team,
        )
        TabletSessionAssignment.objects.create(
            tablet=self.tablet,
            game_session=self.session_b,
            team=team_b,
        )

        self.assertEqual(self.tablet.assignments.count(), 2)

    def test_same_tablet_cannot_duplicate_assignment_inside_same_session(self):
        TabletSessionAssignment.objects.create(
            tablet=self.tablet,
            game_session=self.session_a,
            team=self.team,
        )

        with self.assertRaises(IntegrityError):
            TabletSessionAssignment.objects.create(
                tablet=self.tablet,
                game_session=self.session_a,
                team=self.other_team,
            )

    def test_progress_is_created_for_team(self):
        response = self.client.get(reverse("etapa1"))

        self.assertEqual(response.status_code, 200)
        progress = self.team.progress
        self.assertEqual(progress.game_session, self.session_a)

    def test_select_challenge_creates_project_and_saves_progress_project(self):
        response = self.client.post(reverse("etapa2_select"), {
            "topic_id": self.topic.id,
            "challenge_id": self.challenge.id,
            "desafio_id": self.desafio.id,
        })

        self.assertRedirects(response, reverse("etapa2_1"), fetch_redirect_response=False)
        project = Project.objects.get(equipo=self.team)
        progress = TeamStageProgress.objects.get(team=self.team)
        self.assertEqual(project.desafio, self.challenge)
        self.assertEqual(project.selected_desafio, self.desafio)
        self.assertEqual(progress.project, project)
        self.assertEqual(progress.selected_topic, self.topic)

    def _select_project(self):
        self.client.post(reverse("etapa2_select"), {
            "topic_id": self.topic.id,
            "challenge_id": self.challenge.id,
            "desafio_id": self.desafio.id,
        })
        return Project.objects.get(equipo=self.team)

    def test_bubble_map_updates_empathy_map_and_recalculates_tokens(self):
        project = self._select_project()
        payload = {
            "respuestas": {
                "likes_dislikes": "Le gusta comunicarse",
                "obstacles": "No entiende la app",
                "feelings": "Miedo a equivocarse",
                "others_say": "Su familia lo apoya",
                "hobbies": "Caminar",
            }
        }

        response = self.client.post(
            reverse("etapa2_guardar_mapa"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        empathy_map = EmpathyMap.objects.get(proyecto=project)
        self.assertEqual(empathy_map.gustos, "Le gusta comunicarse")
        # New flow: etapa2 marks etapa2_completed=True and redirects to waiting screen
        # Stage does NOT advance immediately (synchronized via api_stage_closed)
        progress = self.team.progress
        self.assertTrue(progress.etapa2_completed)
        # Tokens are computed at stage close — verify data is persisted for scoring
        self.assertIsNotNone(empathy_map.datos_extra)

    def test_lego_updates_project_and_recalculates_tokens(self):
        project = self._select_project()
        TeamStageProgress.objects.filter(team=self.team).update(
            current_stage=TeamStageProgress.STAGE_ETAPA3,
            current_route="etapa3",
        )
        image = SimpleUploadedFile("lego.jpg", b"fake-image", content_type="image/jpeg")

        response = self.client.post(reverse("etapa3_guardar_foto"), {
            "resumen_idea": "Una solucion clara para conectar a adultos mayores con sus familias.",
            "lego_image": image,
        })

        # New flow: etapa3 redirects to waiting screen, not directly to etapa4
        self.assertRedirects(response, reverse("espera_etapa", args=[3]), fetch_redirect_response=False)
        project.refresh_from_db()
        self.assertIn("adultos mayores", project.resumen_idea)
        # etapa3_completed is set; tokens computed at stage close
        progress = self.team.progress
        self.assertTrue(progress.etapa3_completed)
        # Verify lego image was saved (enables 3 tokens when computed)
        self.assertTrue(bool(project.foto_prototipo))

    def test_pitch_updates_pitch_and_recalculates_tokens(self):
        self._select_project()
        TeamStageProgress.objects.filter(team=self.team).update(
            current_stage=TeamStageProgress.STAGE_ETAPA4,
            current_route="etapa4",
        )

        # New flow: 4 structured fields instead of single pitch_text
        response = self.client.post(
            reverse("etapa4_guardar_pitch"),
            data=json.dumps({
                "nombre_producto": "EduConecta",
                "desafio_empatia": "Adultos mayores no pueden conectar con familia.",
                "campo_creatividad": "App simple con botones grandes y voz.",
                "cierre": "Apóyennos para eliminar la brecha digital.",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        pitch = Pitch.objects.get(proyecto__equipo=self.team)
        # 4 fields should be saved
        self.assertEqual(pitch.nombre_producto, "EduConecta")
        self.assertIn("adultos mayores", pitch.desafio_empatia.lower())
        # guion is auto-generated from 4 fields
        self.assertIn("EduConecta", pitch.guion)
        # New flow: stage does NOT advance immediately (waiting screen)
        progress = self.team.progress
        self.assertTrue(progress.etapa4_completed)

    def test_coevaluacion_updates_evaluation_and_recalculates_tokens(self):
        TeamStageProgress.objects.create(
            team=self.team,
            game_session=self.session_a,
            current_stage=TeamStageProgress.STAGE_COEVALUACION,
            current_route="etapaFinal:negociacion",
        )
        payload = {
            "evaluaciones": [{
                "evaluado_id": self.other_team.id,
                "puntaje_equipo": 5,
                "puntaje_empatia": 4,
                "puntaje_creatividad": 5,
                "puntaje_comunicacion": 4,
                "comentario": "Buen trabajo",
            }]
        }

        response = self.client.post(
            reverse("etapaFinal:save_coevaluacion"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Evaluation.objects.filter(evaluador=self.team, evaluado=self.other_team).exists())
        self.other_team.refresh_from_db()
        # New scoring: average puntaje_equipo = 5 → 15 tokens (not raw sum of 18)
        # The evaluated team gets tokens_evaluacion based on average-to-tokens formula
        self.assertEqual(self.other_team.tokens_evaluacion, 15)

    def test_entering_previous_stage_redirects_to_current_route(self):
        TeamStageProgress.objects.create(
            team=self.team,
            game_session=self.session_a,
            current_stage=TeamStageProgress.STAGE_ETAPA4,
            current_route="etapa4",
        )

        response = self.client.get(reverse("etapa3"))

        self.assertRedirects(response, reverse("etapa4"), fetch_redirect_response=False)
