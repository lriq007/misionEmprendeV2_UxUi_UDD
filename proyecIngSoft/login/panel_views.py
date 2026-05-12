import csv

from io import TextIOWrapper
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render

from etapasJuego.models import Challenge, Evaluation, GameSession, Tablet, Team, Topic, Pitch, TeamStageProgress, TeamGameSession
from .forms import (
    AdminUserForm,
    AdminUserEditForm,
    ChallengeForm,
    EvaluationForm,
    GameSessionForm,
    SeccionEstudiantesForm,
    TabletForm,
    TopicForm,
    EstudianteAdminForm,
    TeamAdminForm,
    CSVUploadForm,
)
from .models import Estudiante, SeccionEstudiantes
from .permissions import ADMIN_GROUP, PROFESOR_GROUP, admin_required, is_admin, profesor_required
import math
from .forms import ProfesorPerfilForm

def _secciones_de_profesor(user):
    return SeccionEstudiantes.objects.filter(sesiones__profesor=user).distinct()

from django.contrib.auth import get_user_model
from django.db.models import Count
User = get_user_model()
# ===============================
#   Panel ADMIN — páginas estáticas
# ===============================

#Nueva funcion 12/5
@admin_required
def admin_dashboard(request):

    from login.models import (
        Estudiante,
        SeccionEstudiantes,
    )

    sesiones = GameSession.objects.all()

    equipos = Team.objects.all()

    estudiantes = Estudiante.objects.all()

    tablets = Tablet.objects.all()

    # KPIs
    sesion_count = sesiones.count()

    seccion_count = SeccionEstudiantes.objects.count()

    profesor_count = User.objects.filter(
        groups__name="PROFESOR"
    ).distinct().count()

    estudiantes_count = estudiantes.count()

    equipos_count = equipos.count()

    tablet_count = tablets.count()

    # Profesor más activo
    top_profesor = User.objects.annotate(
        total_sesiones=Count(
            "sesiones_juego"
        )
    ).order_by(
        "-total_sesiones"
    ).first()

    # Top equipos
    top_equipos = Team.objects.order_by(
        "-tokens_totales"
    )[:5]

    # Sesiones recientes
    sesiones_recientes = sesiones.order_by(
        "-id"
    )[:5]

    # Carreras
    carreras = estudiantes.values(
        "carrera"
    ).annotate(
        total=Count("id")
    ).order_by(
        "-total"
    )

    colors = [
        "#2563eb",
        "#7c3aed",
        "#0f766e",
        "#ea580c",
        "#dc2626",
        "#0891b2",
    ]

    carrera_segments = []

    total_estudiantes = max(
        estudiantes_count,
        1
    )

    start = 0

    for idx, carrera in enumerate(carreras):

        pct = (
            carrera["total"]
            / total_estudiantes
        ) * 100

        end = start + pct

        carrera_segments.append({
            "label": carrera["carrera"] or "Sin carrera",
            "count": carrera["total"],
            "pct": pct,
            "color": colors[idx % len(colors)],
            "start": start,
            "end": end,
        })

        start = end

    carrera_gradient = ", ".join([
        f"{seg['color']} {seg['start']}% {seg['end']}%"
        for seg in carrera_segments
    ])

    if not carrera_gradient:

        carrera_gradient = "#2563eb 0% 100%"

    return render(
        request,
        "login/admin/dashboard.html",
        {
            "sesion_count": sesion_count,
            "seccion_count": seccion_count,
            "profesor_count": profesor_count,
            "equipos_count": equipos_count,
            "estudiantes_count": estudiantes_count,
            "tablet_count": tablet_count,

            "top_profesor": top_profesor,

            "top_equipos": top_equipos,

            "sesiones_recientes": sesiones_recientes,

            "carrera_segments": carrera_segments,
            "carrera_gradient": carrera_gradient,
        },
    )


#Nueva funcion retroalimentacion 12/5
@admin_required
def admin_retroalimentacion(request):

    mejores_pitches = Pitch.objects.exclude(
        score_ai__isnull=True
    ).order_by(
        "-score_ai"
    )[:10]

    mejores_equipos = Team.objects.order_by(
        "-tokens_totales"
    )[:10]

    evaluaciones = Evaluation.objects.all().order_by(
        "-id"
    )[:20]

    return render(
        request,
        "login/admin/retroalimentacion.html",
        {
            "mejores_pitches": mejores_pitches,
            "mejores_equipos": mejores_equipos,
            "evaluaciones": evaluaciones,
        },
    )

def admin_secciones(request):
    if request.method == "POST":
        return redirect("adminpanel:secciones")
    return render(request, "login/admin/secciones.html", {"secciones": [], "q": ""})


def admin_seccion_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:secciones")
    return render(request, "login/admin/form.html", {
        "title": "Editar sección", "back_url": "adminpanel:secciones",
    })


def admin_seccion_eliminar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:secciones")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "adminpanel:secciones", "title": "Eliminar sección",
    })

#Nuevo Cambio de la funcion 12/5
@admin_required
def admin_sesiones(request):

    q = request.GET.get(
        "q",
        ""
    ).strip()

    sesiones = GameSession.objects.select_related(
        "profesor"
    ).order_by(
        "-id"
    )

    if q:

        sesiones = sesiones.filter(
            Q(nombre__icontains=q)
            | Q(codigo__icontains=q)
            | Q(profesor__username__icontains=q)
            | Q(profesor__email__icontains=q)
        )

    form = GameSessionForm(
        request.POST or None,
        request=request
    )

    if request.method == "POST" and form.is_valid():

        form.save()

        messages.success(
            request,
            "Sesión creada correctamente."
        )

        return redirect(
            "adminpanel:sesiones"
        )

    return render(
        request,
        "login/admin/sesiones.html",
        {
            "sesiones": sesiones,
            "form": form,
            "q": q,
        },
    )
#Fin nuevo cambio de la funcion 12/5


def admin_sesion_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:sesiones")
    return render(request, "login/admin/form.html", {
        "title": "Editar sesión", "back_url": "adminpanel:sesiones",
    })


def admin_sesion_eliminar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:sesiones")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "adminpanel:sesiones", "title": "Eliminar sesión",
    })


def admin_topics(request):
    q = request.GET.get("q", "").strip()
    topics = Topic.objects.all()
    if q:
        topics = topics.filter(Q(nombre__icontains=q) | Q(slug__icontains=q))
    topics = topics.order_by("nombre")
    form = TopicForm(request.POST or None, request=request, files=request.FILES or None)
    #Nuevo cambiar slugs que se generen automaticamente 11/5
    if request.method == "POST" and form.is_valid():
        topic =form.save(commit=False)

        from django.utils.text import slugify
        topic.slug = slugify(topic.nombre)
        
        if not topic.color_hex:
            topic.color_hex = "#2563eb"
        topic.save()

        messages.success(request, "Tema guardado.")
        return redirect("adminpanel:topics")
    #Nuevo cambio 12/5
    return render(
        request,
        "login/admin/topics.html",
        {
            "topics": topics,
            "form": form,
            "q": q,
        },
    )
#Fin nuevo cambio 12/5


def admin_topic_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:topics")
    return render(request, "login/admin/form.html", {
        "title": "Editar tema", "back_url": "adminpanel:topics",
    })


def admin_topic_eliminar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:topics")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "adminpanel:topics", "title": "Eliminar tema",
    })

#Nuevo cambio de la funcion 12/5
@admin_required
def admin_challenges(request):

    q = request.GET.get(
        "q",
        ""
    ).strip()

    challenges = Challenge.objects.select_related(
        "topic"
    ).order_by(
        "topic__nombre",
        "orden"
    )

    if q:

        challenges = challenges.filter(
            Q(titulo__icontains=q)
            | Q(topic__nombre__icontains=q)
        )

    form = ChallengeForm(
        request.POST or None,
        request=request,
        files=request.FILES or None
    )

    if request.method == "POST" and form.is_valid():

        form.save()

        messages.success(
            request,
            "Desafío guardado."
        )

        return redirect(
            "adminpanel:challenges"
        )

    return render(
        request,
        "login/admin/challenges.html",
        {
            "challenges": challenges,
            "form": form,
            "q": q,
        },
    )
#Fin nuevo cambio de la funcion 12/5


def admin_challenge_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:challenges")
    return render(request, "login/admin/form.html", {
        "title": "Editar desafío", "back_url": "adminpanel:challenges",
    })


def admin_challenge_eliminar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:challenges")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "adminpanel:challenges", "title": "Eliminar desafío",
    })


def admin_tablets(request):
    if request.method == "POST":
        return redirect("adminpanel:tablets")
    return render(request, "login/admin/tablets.html", {"tablets": [], "q": ""})


def admin_tablet_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:tablets")
    return render(request, "login/admin/form.html", {
        "title": "Editar tablet", "back_url": "adminpanel:tablets",
    })


def admin_tablet_eliminar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:tablets")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "adminpanel:tablets", "title": "Eliminar tablet",
    })


def admin_evaluaciones(request):
    if request.method == "POST":
        return redirect("adminpanel:evaluaciones")
    return render(request, "login/admin/evaluaciones.html", {"evaluaciones": [], "q": ""})


def admin_evaluacion_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:evaluaciones")
    return render(request, "login/admin/form.html", {
        "title": "Editar evaluación", "back_url": "adminpanel:evaluaciones",
    })


def admin_evaluacion_eliminar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:evaluaciones")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "adminpanel:evaluaciones", "title": "Eliminar evaluación",
    })


def admin_usuarios(request):
    User = get_user_model()
    usuarios_admin = User.objects.filter(groups__name=ADMIN_GROUP).distinct()
    usuarios_prof = User.objects.filter(groups__name=PROFESOR_GROUP).distinct()
    form = AdminUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Usuario creado y rol asignado.")
        return redirect("adminpanel:usuarios")
    return render(
        request,
        "login/admin/usuarios.html",
        {
            "form": form,
            "usuarios_admin": usuarios_admin,
            "usuarios_prof": usuarios_prof,
        },
    )


@admin_required
def admin_usuario_editar(request, pk):
    User = get_user_model()
    usuario = get_object_or_404(User, pk=pk, groups__name=PROFESOR_GROUP)
    form = AdminUserEditForm(request.POST or None, instance=usuario)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil de profesor actualizado.")
        return redirect("adminpanel:usuarios")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar profesor", "back_url": "adminpanel:usuarios"},
    )


@admin_required
def admin_equipos(request):
    q = request.GET.get("q", "").strip()
    equipos = (
        Team.objects.select_related("sesion", "sesion__profesor", "tablet")
        .prefetch_related("estudiantes")
        .order_by("-tokens_totales", "sesion__nombre", "codigo_grupo")
    )
    if q:
        equipos = equipos.filter(
            Q(nombre__icontains=q)
            | Q(codigo_grupo__icontains=q)
            | Q(sesion__nombre__icontains=q)
            | Q(tablet__codigo__icontains=q)
        )
    form = TeamAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Equipo creado correctamente.")
        return redirect("adminpanel:equipos")
    return render(
        request,
        "login/admin/equipos.html",
        {"equipos": equipos, "form": form, "q": q},
    )


@admin_required
def admin_estudiantes(request):
    q = request.GET.get("q", "").strip()
    estudiantes = (
        Estudiante.objects.select_related("seccion", "team", "team__sesion")
        .order_by("nombre_apellido")
    )
    if q:
        estudiantes = estudiantes.filter(
            Q(nombre_apellido__icontains=q)
            | Q(carrera__icontains=q)
            | Q(seccion__nombre__icontains=q)
            | Q(team__nombre__icontains=q)
        )
    form = EstudianteAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Estudiante creado correctamente.")
        return redirect("adminpanel:estudiantes")
    return render(
        request,
        "login/admin/estudiantes.html",
        {"estudiantes": estudiantes, "form": form},
    )


@admin_required
def admin_equipo_editar(request, pk):
    equipo = get_object_or_404(Team, pk=pk)
    form = TeamAdminForm(request.POST or None, instance=equipo)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Equipo actualizado.")
        return redirect("adminpanel:equipos")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar equipo", "back_url": "adminpanel:equipos"},
    )


@admin_required
def admin_estudiante_editar(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    form = EstudianteAdminForm(request.POST or None, instance=estudiante)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Estudiante actualizado.")
        return redirect("adminpanel:estudiantes")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar estudiante", "back_url": "adminpanel:estudiantes"},
    )

#Nuevo boton "Mi perfil" 11/5
@admin_required
def admin_mi_perfil(request):

    form = ProfesorPerfilForm(
        request.POST or None,
        instance=request.user
    )

    if request.method == "POST" and form.is_valid():

        user = form.save(commit=False)

        nueva_password = form.cleaned_data.get(
            "nueva_password"
        )

        if nueva_password:

            user.set_password(
                nueva_password
            )

        user.save()

        messages.success(
            request,
            "Perfil actualizado correctamente."
        )

        return redirect(
            "login:login"
        )

    return render(
        request,
        "login/admin/mi_perfil.html",
        {
            "form": form,
        },
    )


# ===============================
#   Panel PROFESOR
# ===============================
#Cambio funcion 12/5
@profesor_required
def profesor_dashboard(request):

    q = request.GET.get(
        "q",
        ""
    ).strip()

    sesiones = GameSession.objects.select_related(
        "seccion"
    ).filter(
        profesor=request.user
    ).order_by(
        "-id"
    )

    secciones = _secciones_de_profesor(
        request.user
    )

    equipos = Team.objects.select_related(
        "sesion"
    ).filter(
        sesion__profesor=request.user
    )

    pitches = Pitch.objects.filter(
        proyecto__equipo__sesion__profesor=request.user
    )

    evaluaciones = Evaluation.objects.filter(
        sesion__profesor=request.user
    )

    estudiantes = Estudiante.objects.filter(
        team__sesion__profesor=request.user
    ).distinct()

    if q:

        equipos = equipos.filter(
            Q(nombre__icontains=q)
            | Q(sesion__nombre__icontains=q)
        )

    top_equipos = equipos.order_by(
        "-tokens_totales",
        "-id"
    )[:5]

    mejor_equipo = equipos.order_by(
        "-tokens_totales"
    ).first()

    mejor_pitch = pitches.exclude(
        score_ai__isnull=True
    ).order_by(
        "-score_ai"
    ).first()

    sesiones_recientes = sesiones[:5]

    context = {

        "sesiones": sesiones,

        "secciones": secciones,

        "sesion_count": sesiones.count(),

        "seccion_count": secciones.count(),

        "equipos_count": equipos.count(),

        "estudiantes_count": estudiantes.count(),

        "pitch_count": pitches.count(),

        "evaluacion_count": evaluaciones.count(),

        "top_equipos": top_equipos,

        "ranking": equipos.order_by(
            "-tokens_totales",
            "nombre"
        )[:10],

        "mejor_equipo": mejor_equipo,

        "mejor_pitch": mejor_pitch,

        "sesiones_recientes": sesiones_recientes,

        "q": q,
    }

    return render(
        request,
        "login/profesor/dashboard.html",
        context
    )


@profesor_required
def profesor_sesiones(request):
    sesiones = GameSession.objects.select_related("seccion").filter(profesor=request.user).order_by("-id")
    secciones_disponibles = SeccionEstudiantes.objects.filter(
        Q(sesiones__profesor=request.user) | Q(sesiones__isnull=True)
    ).distinct()
    form = GameSessionForm(
        request.POST or None,
        request=request,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sesión guardada.")
        return redirect("profesorpanel:sesiones")
    return render(
        request,
        "login/profesor/sesiones.html",
        {"sesiones": sesiones, "form": form},
    )


@profesor_required
def profesor_sesion_editar(request, pk):
    sesion = get_object_or_404(GameSession, pk=pk, profesor=request.user)
    secciones_disponibles = SeccionEstudiantes.objects.filter(
        Q(sesiones__profesor=request.user) | Q(sesiones__isnull=True)
    ).distinct()
    form = GameSessionForm(
        request.POST or None,
        request=request,
        instance=sesion,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sesión actualizada.")
        return redirect("profesorpanel:sesiones")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar sesión", "back_url": "profesorpanel:sesiones"},
    )


@profesor_required
def profesor_sesion_eliminar(request, pk):
    sesion = get_object_or_404(GameSession, pk=pk, profesor=request.user)
    if request.method == "POST":
        return redirect("adminpanel:usuarios")
    return render(request, "login/admin/usuarios.html", {
        "usuarios_admin": [], "usuarios_prof": [],
    })


def admin_usuario_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:usuarios")
    return render(request, "login/admin/form.html", {
        "title": "Editar profesor", "back_url": "adminpanel:usuarios",
    })


def admin_equipos(request):
    if request.method == "POST":
        return redirect("adminpanel:equipos")
    return render(request, "login/admin/equipos.html", {"equipos": [], "q": ""})


def admin_equipo_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:equipos")
    return render(request, "login/admin/form.html", {
        "title": "Editar equipo", "back_url": "adminpanel:equipos",
    })


def admin_estudiantes(request):
    if request.method == "POST":
        return redirect("adminpanel:estudiantes")
    return render(request, "login/admin/estudiantes.html", {"estudiantes": []})


def admin_estudiante_editar(request, pk):
    if request.method == "POST":
        return redirect("adminpanel:estudiantes")
    return render(request, "login/admin/form.html", {
        "title": "Editar estudiante", "back_url": "adminpanel:estudiantes",
    })


#Eliminar funciones Lucas de profesor 12/5

#Nuevo cambio profesor_alumnos 9/5
@profesor_required
def profesor_alumnos(request):

    sesiones = GameSession.objects.filter(
        profesor=request.user
    )

    equipos = Team.objects.filter(
        sesion__in=sesiones
    )

    secciones = SeccionEstudiantes.objects.filter(
        sesiones__in=sesiones
    ).distinct()

    sesion_id = request.GET.get("sesion")

    estudiantes = Estudiante.objects.select_related(
        "seccion",
        "team",
        "team__sesion",
        "team__tablet",
    ).filter(
        team__sesion__in=sesiones
    )

    if sesion_id:

        estudiantes = estudiantes.filter(
            team__sesion_id=sesion_id
        )

    estudiantes = estudiantes.order_by(
        "team__tablet__codigo",
        "team__codigo_grupo",
        "nombre_apellido"
    )

    form = EstudianteAdminForm(
        request.POST or None
    )

    form.fields["team"].queryset = equipos

    form.fields["seccion"].queryset = secciones

    if request.method == "POST" and form.is_valid():

        form.save()

        messages.success(
            request,
            "Estudiante creado correctamente."
        )

        return redirect(
            "profesorpanel:alumnos"
        )

    return render(
        request,
        "login/profesor/alumnos.html",
        {
            "estudiantes": estudiantes,
            "form": form,
            "sesiones": sesiones,
        },
    )
#Fin nuevo cambio profesor_alumnos 9/5

#Nuevo arreglo cambio profesor_equipos 10/5
@profesor_required
def profesor_equipos(request):

    sesiones = GameSession.objects.filter(
        profesor=request.user
    )

    sesion_activa = GameSession.objects.filter(
        profesor=request.user,
        estado__in=[
            "PREPARACION",
            "ACTIVA",
        ]
    ).first()

    equipos = Team.objects.none()

    if sesion_activa:

        equipos = Team.objects.filter(
            sesion=sesion_activa
        ).prefetch_related(
            "estudiantes",
            "tablet",
        ).order_by(
            "tablet__codigo"
        )

    form = TeamAdminForm(
        request.POST or None
    )

    form.fields["sesion"].queryset = sesiones

    if request.method == "POST" and form.is_valid():

        cantidad_equipos = Team.objects.filter(
            sesion=form.cleaned_data["sesion"]
        ).count()

        if cantidad_equipos >= 8:

            messages.error(
                request,
                "Máximo 8 equipos por sesión."
            )

            return redirect(
                "profesorpanel:equipos"
            )

        equipo = form.save()

        tablet_disponible = Tablet.objects.filter(
            sesion=equipo.sesion,
            team__isnull=True
        ).first()

        if tablet_disponible:

            tablet_disponible.sesion = equipo.sesion

            tablet_disponible.save(
                update_fields=["sesion"]
            )

            equipo.tablet = tablet_disponible

            equipo.save(
                update_fields=["tablet"]
            )

        messages.success(
            request,
            "Equipo creado correctamente."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    return render(
        request,
        "login/profesor/equipos.html",
        {
            "equipos": equipos,
            "form": form,
            "sesiones": sesiones,
        },
    )
#Fin arreglo cambio profesor_equipos 10/5

#Validar si el profesor deberia poder crear secciones o si solo el admin las crea 9/5
@profesor_required
def profesor_secciones(request):
    if request.method == "POST":
        return redirect("profesorpanel:secciones")

    return render(
        request,
        "login/profesor/secciones.html",
        {"secciones": secciones, "form": form},
    )


#Nuevo funcion INICIAR JUEGO 9/5
@profesor_required
def profesor_iniciar_sesion(request, pk):

    sesion = get_object_or_404(
        GameSession,
        pk=pk,
        profesor=request.user
    )

    equipos = Team.objects.filter(sesion=sesion)

    if equipos.count() < 3:
        messages.error(
            request,
            "La sesión necesita mínimo 3 equipos."
        )
        return redirect("profesorpanel:equipos")

    equipos_invalidos = [
        e for e in equipos
        if not e.meets_minimum()
    ]

    if equipos_invalidos:
        messages.error(
            request,
            "Todos los equipos deben tener mínimo 2 integrantes."
        )
        return redirect("profesorpanel:equipos")

    sesion.estado = "ACTIVA"

    sesion.save(update_fields=["estado"])

    messages.success(
        request,
        "Juego iniciado correctamente."
    )

    return redirect("profesorpanel:equipos")

#Nuevo arreglar funcion FINALIZAR JUEGO 10/5
@profesor_required
def profesor_finalizar_sesion(request, pk):

    sesion = get_object_or_404(
        GameSession,
        pk=pk,
        profesor=request.user
    )

    # Eliminar equipos
    Team.objects.filter(
        sesion=sesion
    ).delete()

    # Liberar tablets
    Tablet.objects.filter(
        sesion=sesion
    ).update(
        sesion=None
    )

    sesion.estado = "FINALIZADA"

    sesion.save(
        update_fields=["estado"]
    )

    messages.success(
        request,
        "Juego finalizado."
    )

    return redirect(
        "profesorpanel:sesiones"
    )
#Fin arreglo funcion FINALIZAR JUEGO 10/5

#Nuevo arreglo importar CSV 10/5
@profesor_required
def importar_estudiantes_csv(request):

    if request.method != "POST":

        return redirect(
            "profesorpanel:alumnos"
        )

    archivo = request.FILES.get("archivo")

    sesion_id = request.POST.get("sesion")

    sesion = get_object_or_404(
        GameSession,
        id=sesion_id,
        profesor=request.user
    )

    if not archivo:

        messages.error(
            request,
            "Debes seleccionar un archivo CSV."
        )

        return redirect(
            "profesorpanel:alumnos"
        )

    archivo = TextIOWrapper(
        archivo.file,
        encoding="utf-8"
    )

    reader = csv.DictReader(archivo)

    estudiantes_creados = []

    for row in reader:

        nombre = row.get(
            "nombre_apellido",
            ""
        ).strip()

        if not nombre:
            continue

        estudiante = Estudiante.objects.create(
            nombre_apellido=nombre,
            carrera=row.get("carrera", "").strip(),
            seccion=sesion.seccion,
        )

        estudiantes_creados.append(estudiante)

    # CREAR EQUIPOS AUTOMÁTICAMENTE
    equipos = list(
        Team.objects.filter(
            sesion=sesion
        )
    )

    if not equipos:

        cantidad_estudiantes = len(
            estudiantes_creados
        )

        cantidad_equipos = max(
            3,
            min(
                8,
                math.ceil(
                    cantidad_estudiantes / 6
                )
            )
        )

        tablets_ocupadas = Team.objects.values_list(
            "tablet_id",
            flat=True
        )

        tablets = list(
            Tablet.objects.exclude(
                id__in=tablets_ocupadas
            )[:cantidad_equipos]
        )

        if len(tablets) < cantidad_equipos:

            messages.error(
                request,
                f"No hay suficientes tablets disponibles "
                f"({len(tablets)}/{cantidad_equipos})."
            )

            return redirect(
                "profesorpanel:alumnos"
            )

        equipos = []

        for i in range(cantidad_equipos):

            tablet = tablets[i]

            tablet.sesion = sesion

            tablet.save(
                update_fields=["sesion"]
            )

            equipo = Team.objects.create(
                nombre=f"Equipo {i+1}",
                codigo_grupo=str(i+1),
                sesion=sesion,
                tablet=tablet,
            )

            equipos.append(equipo)

    # DISTRIBUIR ESTUDIANTES
    idx = 0

    for estudiante in estudiantes_creados:

        assigned = False

        attempts = 0

        while not assigned and attempts < len(equipos):

            equipo = equipos[idx % len(equipos)]

            if equipo.has_cupo():

                estudiante.team = equipo

                estudiante.save(
                    update_fields=["team"]
                )

                assigned = True

            idx += 1
            attempts += 1

    messages.success(
        request,
        f"{len(estudiantes_creados)} estudiantes importados y asignados."
    )

    return redirect(
        "profesorpanel:alumnos"
    )
#Nuevo arreglo generar equipos automaticos v2 10/5
@profesor_required
def generar_equipos_automaticos(request):

    sesion = GameSession.objects.filter(
        profesor=request.user,
        estado="PREPARACION"
    ).first()

    if not sesion:

        messages.error(
            request,
            "No tienes una sesión en preparación."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    equipos = list(
        Team.objects.filter(
            sesion=sesion
        ).order_by("id")
    )

    if not equipos:

        messages.error(
            request,
            "La sesión no tiene equipos."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    # SINCRONIZAR TABLETS CON SESIÓN
    for equipo in equipos:

        if equipo.tablet:

            equipo.tablet.sesion = sesion

            equipo.tablet.save(
                update_fields=["sesion"]
            )

    estudiantes = list(
        Estudiante.objects.filter(
            Q(team__sesion=sesion)
            |
            Q(
                seccion=sesion.seccion,
                team__isnull=True
            )
        ).distinct()
    )

    import random

    random.shuffle(estudiantes)

    idx = 0

    for estudiante in estudiantes:

        assigned = False

        attempts = 0

        while not assigned and attempts < len(equipos):

            equipo = equipos[idx % len(equipos)]

            if equipo.has_cupo():

                estudiante.team = equipo

                estudiante.save(
                    update_fields=["team"]
                )

                assigned = True

            idx += 1
            attempts += 1

    messages.success(
        request,
        "Equipos mezclados correctamente."
    )

    return redirect(
        "profesorpanel:equipos"
    )
#Fin nuevo arreglo generar equipos 10/5 

#Nuevo eliminar alumnos 9/5
@profesor_required
def eliminar_alumno(request):

    sesion = GameSession.objects.filter(
        profesor=request.user,
        estado="PREPARACION"
    ).first()

    if not sesion:

        messages.error(
            request,
            "No hay sesión disponible."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    equipos = Team.objects.filter(
        sesion=sesion
    ).order_by("-id")

    if equipos.count() <= 3:

        messages.error(
            request,
            "Debe existir mínimo 3 equipos."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    equipo_eliminar = equipos.first()

    otros_equipos = list(
        Team.objects.filter(
            sesion=sesion
        ).exclude(
            id=equipo_eliminar.id
        )
    )

    estudiantes = list(
        Estudiante.objects.filter(
            team=equipo_eliminar
        )
    )

    idx = 0

    for estudiante in estudiantes:

        assigned = False

        attempts = 0

        while not assigned and attempts < len(otros_equipos):

            destino = otros_equipos[
                idx % len(otros_equipos)
            ]

            if destino.has_cupo():

                estudiante.team = destino

                estudiante.save(
                    update_fields=["team"]
                )

                assigned = True

            idx += 1
            attempts += 1

    tablet = equipo_eliminar.tablet

    equipo_eliminar.delete()

    if tablet:

        tablet.sesion = None

        tablet.save(
            update_fields=["sesion"]
        )

    messages.success(
        request,
        "Tablet/equipo eliminado correctamente."
    )

    return redirect(
        "profesorpanel:equipos"
    )

#Fin nuevo 9/5

#Nuevo mover alumno 10/5
@profesor_required
def mover_alumno(request, pk):

    alumno = get_object_or_404(
        Estudiante,
        pk=pk,
        team__sesion__profesor=request.user
    )

    #Nuevo bloque de mover alumnos en sesiones activas 11/5
    if alumno.team.sesion.estado == "ACTIVA":

        messages.error(
            request,
            "No puedes mover alumnos durante el juego."
        )

        return redirect(
            "profesorpanel:equipos"
        )
    #Fin nuevo bloque de mover alumnos en sesiones activas 11/5    

    nuevo_team = get_object_or_404(
        Team,
        pk=request.POST.get("team"),
        sesion__profesor=request.user
    )

    if not nuevo_team.has_cupo():

        messages.error(
            request,
            "El equipo ya está completo."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    alumno.team = nuevo_team

    alumno.save(update_fields=["team"])

    messages.success(
        request,
        "Alumno movido correctamente."
    )

    return redirect(
        "profesorpanel:equipos"
    )
#Fin nuevo mover alumno 10/5 

#Nuevo modificar cantidad equipos 10/5
@profesor_required
def agregar_equipo(request):

    sesion = GameSession.objects.filter(
        profesor=request.user,
        estado="PREPARACION"
    ).first()

    if not sesion:

        messages.error(
            request,
            "No hay una sesión en preparación."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    cantidad = Team.objects.filter(
        sesion=sesion
    ).count()

    if cantidad >= 8:

        messages.error(
            request,
            "Máximo 8 tablets/equipos."
        )

        return redirect(
            "profesorpanel:equipos"
        )
    #Nuevo cambio tablets disponibles 10/5
    tablets_ocupadas = Team.objects.values_list(
        "tablet_id",
        flat=True
    )

    tablet_disponible = Tablet.objects.exclude(
        id__in=tablets_ocupadas
    ).first()

    tablet_disponible.sesion = sesion

    tablet_disponible.save(
        update_fields=["sesion"]
    )
    #Fin nuevo cambio tablets disponibles 10/5

    if not tablet_disponible:

        messages.error(
            request,
            "No hay tablets disponibles."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    tablet_disponible.sesion = sesion

    tablet_disponible.save(
        update_fields=["sesion"]
    )

    ultimo = Team.objects.filter(
        sesion=sesion
    ).order_by("-id").first()

    nuevo_numero = 1

    if ultimo:

        try:
            nuevo_numero = int(
                ultimo.codigo_grupo
            ) + 1

        except:
            nuevo_numero = cantidad + 1

    codigo = f"Equipo {nuevo_numero}"

    Team.objects.create(
        nombre=codigo,
        codigo_grupo=str(nuevo_numero),
        sesion=sesion,
        tablet=tablet_disponible,
    )

    messages.success(
        request,
        "Tablet/equipo agregado."
    )

    return redirect(
        "profesorpanel:equipos"
    )

@profesor_required
def eliminar_equipo(request):

    sesion = GameSession.objects.filter(
        profesor=request.user,
        estado="PREPARACION"
    ).first()

    if not sesion:

        messages.error(
            request,
            "No hay sesión activa."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    equipos = Team.objects.filter(
        sesion=sesion
    ).order_by("-id")

    if equipos.count() <= 3:

        messages.error(
            request,
            "Debe existir mínimo 3 equipos."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    equipo = equipos.first()

    estudiantes = list(
        equipo.estudiantes.all()
    )

    otros = Team.objects.filter(
        sesion=sesion
    ).exclude(
        id=equipo.id
    )

    idx = 0

    for estudiante in estudiantes:

        for _ in range(len(otros)):

            destino = otros[idx % len(otros)]

            idx += 1

            if destino.has_cupo():

                estudiante.team = destino

                estudiante.save(
                    update_fields=["team"]
                )

                break

    tablet = equipo.tablet

    equipo.delete()

    if tablet:

        tablet.sesion = None

        tablet.save(
            update_fields=["sesion"]
        )

    messages.success(
        request,
        "Tablet/equipo eliminado."
    )

    return redirect(
        "profesorpanel:equipos"
    )

#Nuevo boton "Mi perfil" 11/5
@profesor_required
def profesor_mi_perfil(request):

    form = ProfesorPerfilForm(
        request.POST or None,
        instance=request.user
    )

    if request.method == "POST" and form.is_valid():

        user = form.save(commit=False)

        nueva_password = form.cleaned_data.get(
            "nueva_password"
        )

        if nueva_password:

            user.set_password(nueva_password)

        user.save()

        messages.success(
            request,
            "Perfil actualizado correctamente."
        )

        return redirect(
            "login:login"
        )


    return render(
        request,
        "login/profesor/mi_perfil.html",
        {
            "form": form,
        },
    )
#Fin nuevo modificar cantidad equipos 10/5

#Nuevo progreso juego 12/5
@profesor_required
def progreso_juego(request):

    sesion = GameSession.objects.filter(
        profesor=request.user,
        estado="ACTIVA"
    ).first()

    if not sesion:

        messages.error(
            request,
            "No hay un juego activo."
        )

        return redirect(
            "profesorpanel:equipos"
        )

    equipos = Team.objects.filter(
        sesion=sesion
    ).prefetch_related(
        "estudiantes"
    ).order_by(
        "-tokens_totales"
    )

    progreso = TeamStageProgress.objects.select_related(
        "team",
        "selected_topic",
        "selected_challenge",
    ).filter(
        game_session=sesion
    )

    for equipo in equipos:

        equipo.progreso = progreso.filter(
            team=equipo
        ).first()

        equipo.game_session = TeamGameSession.objects.filter(
            equipo=equipo
        ).order_by(
            "-id"
        ).first()

    return render(
        request,
        "login/profesor/progreso.html",
        {
            "sesion": sesion,
            "equipos": equipos,
        },
    )
#Fin progreso juego 12/5
#Nuevo evaluacion 12/5
@profesor_required
def profesor_evaluacion(request):

    sesiones = GameSession.objects.filter(
        profesor=request.user
    ).order_by(
        "-id"
    )

    sesion_id = request.GET.get(
        "sesion"
    )

    equipos = Team.objects.none()

    pitches = Pitch.objects.none()

    evaluaciones = Evaluation.objects.none()

    if sesion_id:

        equipos = Team.objects.filter(
            sesion_id=sesion_id
        ).order_by(
            "-tokens_totales"
        )

        pitches = Pitch.objects.filter(
            proyecto__equipo__sesion_id=sesion_id
        ).select_related(
            "proyecto",
            "proyecto__equipo",
        )

        evaluaciones = Evaluation.objects.filter(
            sesion_id=sesion_id
        )

    return render(
        request,
        "login/profesor/evaluacion.html",
        {
            "sesiones": sesiones,
            "equipos": equipos,
            "pitches": pitches,
            "evaluaciones": evaluaciones,
            "sesion_id": sesion_id,
        },
    )