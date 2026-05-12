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
    
    #Nuevo generar equipos automaticos 9/5
    path(
        "equipos/generar/",
        views.generar_equipos_automaticos,
        name="generar_equipos",
    ),

    #Nuevo eliminar alumnos 9/5
    path(
        "alumnos/<int:pk>/eliminar/",
        views.eliminar_alumno,
        name="eliminar_alumno",
    ),

    #Fin nuevo 9/5

    #Nuevo url mover alumno 10/5
    path(
        "alumnos/<int:pk>/mover/",
        views.mover_alumno,
        name="mover_alumno",
    ),
    #Fin nuevo url mover alumno 10/5

    #Nuevo modificar cantidad equipos 10/5
    path(
        "equipos/agregar/",
        views.agregar_equipo,
        name="agregar_equipo",
    ),

    path(
        "equipos/eliminar/",
        views.eliminar_equipo,
        name="eliminar_equipo",
    ),
    #Fin nuevo modificar cantidad equipos 10/5

    #Nuevo url mi perfil 11/5
    path(
        "perfil/",
        views.profesor_mi_perfil,
        name="mi_perfil",
    ),

    #Nuevo url ver progreso 11/5
    path(
        "progreso/",
        views.progreso_juego,
        name="progreso_juego",
    ),

    #Nuevo evaluacion 12/5
    path(
        "evaluacion/",
        views.profesor_evaluacion,
        name="profesor_evaluacion",
    ),
    #Fin nuevo url ver progreso 11/5
]

