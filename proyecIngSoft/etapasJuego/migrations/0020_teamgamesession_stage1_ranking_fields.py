from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("etapasJuego", "0019_gamesession_qr_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="teamgamesession",
            name="elapsed_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teamgamesession",
            name="ready_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teamgamesession",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pendiente"),
                    ("PLAYING", "Jugando"),
                    ("FINISHED", "Terminado"),
                    ("TIME_UP", "No completo"),
                ],
                default="PENDING",
                max_length=16,
            ),
        ),
    ]
