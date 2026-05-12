from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from etapasJuego.models import Evaluation, GameSession, Project, TeamGameSession, TeamStageProgress


class Command(BaseCommand):
    help = "Reinicia el progreso de juego de todos los equipos de una sesion."

    def add_arguments(self, parser):
        parser.add_argument(
            "codigo_sesion",
            help="Codigo de la sesion de juego que se quiere reiniciar.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra que se reiniciaria sin modificar la base de datos.",
        )

    def handle(self, *args, **options):
        codigo_sesion = options["codigo_sesion"]
        dry_run = options["dry_run"]

        try:
            sesion = GameSession.objects.get(codigo=codigo_sesion)
        except GameSession.DoesNotExist as exc:
            raise CommandError(f"No existe una sesion con codigo '{codigo_sesion}'.") from exc

        teams = list(sesion.equipos.order_by("id"))
        if not teams:
            self.stdout.write(self.style.WARNING("La sesion no tiene equipos para reiniciar."))
            return

        if dry_run:
            self.stdout.write(f"Sesion: {sesion.nombre} ({sesion.codigo})")
            self.stdout.write(f"Equipos a reiniciar: {len(teams)}")
            self.stdout.write("No se modifico la base de datos porque se uso --dry-run.")
            return

        with transaction.atomic():
            # Reset GameSession state so negociacion starts fresh
            sesion.etapa_actual = "ETAPA1"
            sesion.negociacion_orden = []
            sesion.negociacion_presentador_idx = 0
            sesion.negociacion_fase = "ORDEN"
            sesion.negociacion_fase_inicio = None
            sesion.save(update_fields=[
                "etapa_actual",
                "negociacion_orden",
                "negociacion_presentador_idx",
                "negociacion_fase",
                "negociacion_fase_inicio",
            ])

            reset_count = 0
            for team in teams:
                TeamGameSession.objects.filter(equipo=team).delete()
                Evaluation.objects.filter(evaluador=team).delete()
                Evaluation.objects.filter(evaluado=team).delete()
                Project.objects.filter(equipo=team).delete()

                team.tokens_empatia = 0
                team.tokens_creatividad = 0
                team.tokens_evaluacion = 0
                team.tokens_totales = 0
                team.save(
                    update_fields=[
                        "tokens_empatia",
                        "tokens_creatividad",
                        "tokens_evaluacion",
                        "tokens_totales",
                    ]
                )

                progress, _ = TeamStageProgress.objects.get_or_create(
                    team=team,
                    defaults={"game_session": sesion},
                )
                progress.game_session = sesion
                progress.current_stage = TeamStageProgress.STAGE_ROMPEHIELO
                progress.current_route = "rompehielo"
                progress.selected_topic = None
                progress.selected_challenge = None
                progress.selected_desafio = None
                progress.project = None
                progress.etapa1_completed = False
                progress.etapa2_completed = False
                progress.etapa3_completed = False
                progress.etapa4_completed = False
                progress.coevaluacion_completed = False
                progress.save()
                reset_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sesion '{sesion.codigo}' reiniciada. Equipos reiniciados: {reset_count}."
            )
        )
