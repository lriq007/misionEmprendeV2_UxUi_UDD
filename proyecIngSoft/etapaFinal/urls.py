from django.urls import path
from . import views

app_name = "etapaFinal"

urlpatterns = [
    path("", views.coevaluacion_home, name="home"),
    path("save/", views.save_coevaluacion, name="save_coevaluacion"),
    path("final/", views.final_resultados, name="final_resultados"),
    path("cierre/", views.cierre_final, name="cierre_final"),
    path("foto-grupal/", views.upload_foto_grupal, name="upload_foto_grupal"),
    # Negociación secuencial
    path("negociacion/", views.negociacion_view, name="negociacion"),
    path("api/negociacion/estado/", views.api_negociacion_estado, name="api_negociacion_estado"),
    path("api/negociacion/iniciar-pitch/", views.api_negociacion_iniciar_pitch, name="api_negociacion_iniciar_pitch"),
    path("api/negociacion/timeup-pitch/", views.api_negociacion_timeup_pitch, name="api_negociacion_timeup_pitch"),
    path("api/negociacion/guardar-evaluacion/", views.api_negociacion_guardar_evaluacion, name="api_negociacion_guardar_evaluacion"),
    path("api/negociacion/timeup-evaluacion/", views.api_negociacion_timeup_evaluacion, name="api_negociacion_timeup_evaluacion"),
]
