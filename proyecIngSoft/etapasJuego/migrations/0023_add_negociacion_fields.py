from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("etapasJuego", "0022_add_palabras_sopa_and_pitch_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamesession",
            name="negociacion_orden",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="gamesession",
            name="negociacion_presentador_idx",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="gamesession",
            name="negociacion_fase",
            field=models.CharField(default="ORDEN", max_length=20),
        ),
        migrations.AddField(
            model_name="gamesession",
            name="negociacion_fase_inicio",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
