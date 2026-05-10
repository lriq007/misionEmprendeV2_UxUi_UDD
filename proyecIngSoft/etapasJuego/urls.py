from django.urls import path
from . import views

urlpatterns = [
    path("", views.etapas_index, name="etapas_index"),  # /etapasJuego/
    path("tablet/seleccion-modalidad/", views.seleccion_modalidad, name="seleccion_modalidad"),
    path("tablet/rompehielo/", views.rompehielo, name="rompehielo"),
    path("etapa/0/", views.etapa2_tema),
    path("etapa2/tema/", views.etapa2_tema, name="etapa2_tema"),
    path("etapa/1/", views.etapa1, name="etapa1"),
    path("etapa/1/ranking/", views.etapa1_ranking, name="etapa1_ranking"),
    path("api/init/", views.api_init, name="api_init"),
    path("api/start/", views.api_stage1_start, name="api_stage1_start"),
    path("api/timeup/", views.api_stage1_timeup, name="api_stage1_timeup"),
    path("api/ranking/", views.api_stage1_ranking, name="api_stage1_ranking"),
    path("api/select/start/", views.api_select_start, name="api_select_start"),
    path("api/select/extend/", views.api_select_extend, name="api_select_extend"),
    path("api/select/commit/", views.api_select_commit, name="api_select_commit"),
    path("api/reset/", views.api_reset, name="api_reset"),

    # Waiting screen and synchronized stage closure
    path("etapa/<int:etapa_num>/espera/", views.espera_etapa, name="espera_etapa"),
    path("api/etapa/<int:etapa_num>/cerrada/", views.api_stage_closed, name="api_stage_closed"),
    path("etapa/<int:etapa_num>/ranking/", views.ranking_parcial, name="ranking_parcial"),
    path("api/etapa/<int:etapa_num>/ranking-overlay/", views.api_ranking_overlay, name="api_ranking_overlay"),

    path("inicio-historia/", views.inicioHistoria, name="inicioHistoria"),
    path("etapa/2/", views.etapa2, name="etapa2"),
    path("etapa/2/seleccionar/", views.etapa2_seleccionar, name="etapa2_select"),
    path("etapa/2/seleccion/", views.etapa2_1, name="etapa2_1"),
    path("etapa/2/mapa/guardar/", views.etapa2_guardar_mapa, name="etapa2_guardar_mapa"),
    path("etapa/2/timeup/", views.api_etapa2_timeup, name="api_etapa2_timeup"),
    path("etapa/3/", views.etapa3, name="etapa3"),
    path("etapa/3/guardar-foto/", views.etapa3_guardar_foto, name="etapa3_guardar_foto"),
    path("api/foto-equipo/", views.api_guardar_foto_equipo, name="api_guardar_foto_equipo"),
    path("etapa/3/timeup/", views.api_etapa3_timeup, name="api_etapa3_timeup"),
    path("etapa/4/", views.etapa4, name="etapa4"),
    path("etapa/4/guardar-pitch/", views.etapa4_guardar_pitch, name="etapa4_guardar_pitch"),
    path("etapa/4/timeup/", views.api_etapa4_timeup, name="api_etapa4_timeup"),
    path("inicio_juego/", views.inicio_juego, name="inicio_juego"),
]
