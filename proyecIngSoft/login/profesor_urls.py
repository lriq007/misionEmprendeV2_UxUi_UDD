from django.urls import path

from . import panel_views as views

app_name = "profesorpanel"

urlpatterns = [
    path("", views.profesor_dashboard, name="dashboard"),
    path("sesiones/", views.profesor_sesiones, name="sesiones"),
    path("sesiones/<int:pk>/editar/", views.profesor_sesion_editar, name="sesion_editar"),
    path("sesiones/<int:pk>/eliminar/", views.profesor_sesion_eliminar, name="sesion_eliminar"),
    path("alumnos/", views.profesor_alumnos, name="alumnos"),
    path("equipos/", views.profesor_equipos, name="equipos"),
    path("secciones/", views.profesor_secciones, name="secciones"),

    #Nuevo agregar urls nuevas 9/5
    path(
        "sesiones/<int:pk>/iniciar/",
        views.profesor_iniciar_sesion,
        name="iniciar_sesion",
    ),

    path(
        "sesiones/<int:pk>/finalizar/",
        views.profesor_finalizar_sesion,
    name="finalizar_sesion",
    ),

    #Nuevo url subir csv 9/5
    path(
        "alumnos/importar-csv/",
        views.importar_estudiantes_csv,
        name="importar_csv",
    ),
    #Fin nuevo
]
