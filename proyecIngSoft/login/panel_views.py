import csv

from io import TextIOWrapper
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render

from etapasJuego.models import Challenge, Evaluation, GameSession, Tablet, Team, Topic
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

def _secciones_de_profesor(user):
    return SeccionEstudiantes.objects.filter(sesiones__profesor=user).distinct()


# ===============================
#   Panel ADMIN
# ===============================
@admin_required
def admin_dashboard(request):
    User = get_user_model()
    profesor_count = User.objects.filter(groups__name=PROFESOR_GROUP).distinct().count()
    admin_count = User.objects.filter(groups__name=ADMIN_GROUP).distinct().count()
    equipos_count = Team.objects.count()
    estudiantes_count = Estudiante.objects.count()
    carrera_qs = (
        Estudiante.objects.values("carrera")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    carrera_total = sum(item["total"] for item in carrera_qs) or 1
    colors = ["#fbbf24", "#22d3ee", "#a855f7", "#fb7185", "#2dd4bf", "#f97316"]
    carrera_segments = []
    cursor = 0.0
    for idx, item in enumerate(carrera_qs):
        pct = (item["total"] / carrera_total) * 100.0
        start = cursor
        end = start + pct
        carrera_segments.append(
            {
                "label": item["carrera"] or "Sin carrera",
                "count": item["total"],
                "pct": pct,
                "color": colors[idx % len(colors)],
                "start": start,
                "end": end,
            }
        )
        cursor = end
    carrera_gradient = ", ".join(
        f"{seg['color']} {seg['start']:.2f}% {seg['end']:.2f}%"
        for seg in carrera_segments
    ) or "#fbbf24 0% 100%"
    top_equipos = (
        Team.objects.select_related("sesion", "sesion__profesor")
        .order_by("-tokens_totales", "-id")[:5]
    )
    context = {
        "seccion_count": SeccionEstudiantes.objects.count(),
        "sesion_count": GameSession.objects.count(),
        "topic_count": Topic.objects.count(),
        "challenge_count": Challenge.objects.count(),
        "tablet_count": Tablet.objects.count(),
        "evaluation_count": Evaluation.objects.count(),
        "profesor_count": profesor_count,
        "equipos_count": equipos_count,
        "estudiantes_count": estudiantes_count,
        "admin_count": admin_count,
        "carrera_segments": carrera_segments,
        "carrera_gradient": carrera_gradient,
        "top_equipos": top_equipos,
        "sesiones_recientes": GameSession.objects.select_related("seccion", "profesor").order_by("-id")[
            :5
        ],
    }
    return render(request, "login/admin/dashboard.html", context)


@admin_required
def admin_secciones(request):
    q = request.GET.get("q", "").strip()
    secciones = SeccionEstudiantes.objects.all()
    if q:
        secciones = secciones.filter(
            Q(nombre__icontains=q)
            | Q(carrera__icontains=q)
            | Q(carrera_fk__nombre__icontains=q)
        )
    secciones = secciones.order_by("-fecha_creacion")
    if request.method == "POST":
        form = SeccionEstudiantesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sección creada/actualizada correctamente.")
            return redirect("adminpanel:secciones")
    else:
        form = SeccionEstudiantesForm()

    return render(
        request,
        "login/admin/secciones.html",
        {
            "form": form,
            "secciones": secciones,
            "q": q,
        },
    )


@admin_required
def admin_seccion_editar(request, pk):
    seccion = get_object_or_404(SeccionEstudiantes, pk=pk)
    form = SeccionEstudiantesForm(request.POST or None, instance=seccion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sección actualizada.")
        return redirect("adminpanel:secciones")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar sección", "back_url": "adminpanel:secciones"},
    )


@admin_required
def admin_seccion_eliminar(request, pk):
    seccion = get_object_or_404(SeccionEstudiantes, pk=pk)
    if request.method == "POST":
        seccion.delete()
        messages.success(request, "Sección eliminada.")
        return redirect("adminpanel:secciones")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": seccion, "back_url": "adminpanel:secciones", "title": "Eliminar sección"},
    )


@admin_required
def admin_sesiones(request):
    q = request.GET.get("q", "").strip()
    sesiones = GameSession.objects.select_related("profesor", "seccion")
    if q:
        sesiones = sesiones.filter(
            Q(nombre__icontains=q)
            | Q(codigo__icontains=q)
            | Q(profesor__username__icontains=q)
            | Q(profesor__first_name__icontains=q)
            | Q(profesor__last_name__icontains=q)
            | Q(seccion__nombre__icontains=q)
        )
    sesiones = sesiones.order_by("-fecha", "-id")
    form = GameSessionForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sesión guardada.")
        return redirect("adminpanel:sesiones")

    return render(
        request,
        "login/admin/sesiones.html",
        {"sesiones": sesiones, "form": form, "q": q},
    )


@admin_required
def admin_sesion_editar(request, pk):
    sesion = get_object_or_404(GameSession, pk=pk)
    form = GameSessionForm(request.POST or None, instance=sesion, request=request)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sesión actualizada.")
        return redirect("adminpanel:sesiones")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar sesión", "back_url": "adminpanel:sesiones"},
    )


@admin_required
def admin_sesion_eliminar(request, pk):
    sesion = get_object_or_404(GameSession, pk=pk)
    if request.method == "POST":
        sesion.delete()
        messages.success(request, "Sesión eliminada.")
        return redirect("adminpanel:sesiones")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": sesion, "back_url": "adminpanel:sesiones", "title": "Eliminar sesión"},
    )


@admin_required
def admin_topics(request):
    q = request.GET.get("q", "").strip()
    topics = Topic.objects.all()
    if q:
        topics = topics.filter(Q(nombre__icontains=q) | Q(slug__icontains=q))
    topics = topics.order_by("nombre")
    form = TopicForm(request.POST or None, request=request, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tema guardado.")
        return redirect("adminpanel:topics")
    return render(
        request,
        "login/admin/topics.html",
        {"topics": topics, "form": form, "q": q},
    )


@admin_required
def admin_topic_editar(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    form = TopicForm(request.POST or None, request=request, instance=topic, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tema actualizado.")
        return redirect("adminpanel:topics")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar tema", "back_url": "adminpanel:topics"},
    )


@admin_required
def admin_topic_eliminar(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == "POST":
        topic.delete()
        messages.success(request, "Tema eliminado.")
        return redirect("adminpanel:topics")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": topic, "back_url": "adminpanel:topics", "title": "Eliminar tema"},
    )


@admin_required
def admin_challenges(request):
    q = request.GET.get("q", "").strip()
    challenges = Challenge.objects.select_related("topic").all()
    if q:
        challenges = challenges.filter(
            Q(titulo__icontains=q) | Q(topic__nombre__icontains=q)
        )
    challenges = challenges.order_by("topic__nombre", "orden")
    form = ChallengeForm(request.POST or None, request=request, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Desafío guardado.")
        return redirect("adminpanel:challenges")
    return render(
        request,
        "login/admin/challenges.html",
        {"challenges": challenges, "form": form, "q": q},
    )


@admin_required
def admin_challenge_editar(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    form = ChallengeForm(request.POST or None, request=request, instance=challenge, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Desafío actualizado.")
        return redirect("adminpanel:challenges")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar desafío", "back_url": "adminpanel:challenges"},
    )


@admin_required
def admin_challenge_eliminar(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk)
    if request.method == "POST":
        challenge.delete()
        messages.success(request, "Desafío eliminado.")
        return redirect("adminpanel:challenges")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": challenge, "back_url": "adminpanel:challenges", "title": "Eliminar desafío"},
    )


@admin_required
def admin_tablets(request):
    q = request.GET.get("q", "").strip()
    tablets = Tablet.objects.select_related("sesion", "team").all()
    if q:
        tablets = tablets.filter(
            Q(codigo__icontains=q)
            | Q(codigo_acceso__icontains=q)
            | Q(sesion__nombre__icontains=q)
        )
    tablets = tablets.order_by("sesion__nombre", "codigo")
    form = TabletForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tablet guardada.")
        return redirect("adminpanel:tablets")
    return render(
        request,
        "login/admin/tablets.html",
        {"tablets": tablets, "form": form, "q": q},
    )


@admin_required
def admin_tablet_editar(request, pk):
    tablet = get_object_or_404(Tablet, pk=pk)
    form = TabletForm(request.POST or None, request=request, instance=tablet)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tablet actualizada.")
        return redirect("adminpanel:tablets")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar tablet", "back_url": "adminpanel:tablets"},
    )


@admin_required
def admin_tablet_eliminar(request, pk):
    tablet = get_object_or_404(Tablet, pk=pk)
    if request.method == "POST":
        tablet.delete()
        messages.success(request, "Tablet eliminada.")
        return redirect("adminpanel:tablets")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": tablet, "back_url": "adminpanel:tablets", "title": "Eliminar tablet"},
    )


@admin_required
def admin_evaluaciones(request):
    q = request.GET.get("q", "").strip()
    evaluaciones = Evaluation.objects.select_related("sesion", "evaluador", "evaluado").all()
    if q:
        evaluaciones = evaluaciones.filter(
            Q(sesion__nombre__icontains=q)
            | Q(sesion__codigo__icontains=q)
            | Q(evaluador__nombre__icontains=q)
            | Q(evaluador__codigo_grupo__icontains=q)
            | Q(evaluado__nombre__icontains=q)
            | Q(evaluado__codigo_grupo__icontains=q)
        )
    evaluaciones = evaluaciones.order_by("-sesion__fecha", "evaluador__codigo_grupo")
    form = EvaluationForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Evaluación guardada.")
        return redirect("adminpanel:evaluaciones")
    return render(
        request,
        "login/admin/evaluaciones.html",
        {"evaluaciones": evaluaciones, "form": form, "q": q},
    )


@admin_required
def admin_evaluacion_editar(request, pk):
    evaluacion = get_object_or_404(Evaluation, pk=pk)
    form = EvaluationForm(request.POST or None, request=request, instance=evaluacion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Evaluación actualizada.")
        return redirect("adminpanel:evaluaciones")
    return render(
        request,
        "login/admin/form.html",
        {"form": form, "title": "Editar evaluación", "back_url": "adminpanel:evaluaciones"},
    )


@admin_required
def admin_evaluacion_eliminar(request, pk):
    evaluacion = get_object_or_404(Evaluation, pk=pk)
    if request.method == "POST":
        evaluacion.delete()
        messages.success(request, "Evaluación eliminada.")
        return redirect("adminpanel:evaluaciones")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": evaluacion, "back_url": "adminpanel:evaluaciones", "title": "Eliminar evaluación"},
    )


@admin_required
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


# ===============================
#   Panel PROFESOR
# ===============================
@profesor_required
def profesor_dashboard(request):
    q = request.GET.get("q", "").strip()
    sesiones = GameSession.objects.select_related("seccion").filter(profesor=request.user).order_by("-id")
    secciones = _secciones_de_profesor(request.user)
    equipos = Team.objects.select_related("sesion").filter(sesion__profesor=request.user)
    estudiantes_count = Estudiante.objects.filter(team__sesion__profesor=request.user).count()
    if q:
        equipos = equipos.filter(Q(nombre__icontains=q) | Q(sesion__nombre__icontains=q))
    top_equipos = equipos.order_by("-tokens_totales", "-id")[:5]
    context = {
        "sesiones": sesiones,
        "secciones": secciones,
        "sesion_count": sesiones.count(),
        "seccion_count": secciones.count(),
        "equipos_count": equipos.count(),
        "estudiantes_count": estudiantes_count,
        "top_equipos": top_equipos,
        "ranking": equipos.order_by("-tokens_totales", "nombre")[:10],
        "q": q,
    }
    return render(request, "login/profesor/dashboard.html", context)


@profesor_required
def profesor_sesiones(request):
    sesiones = GameSession.objects.select_related("seccion").filter(profesor=request.user).order_by("-id")
    secciones_disponibles = SeccionEstudiantes.objects.filter(
        Q(sesiones__profesor=request.user) | Q(sesiones__isnull=True)
    ).distinct()
    form = GameSessionForm(
        request.POST or None,
        request=request,
        allowed_secciones=secciones_disponibles,
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
        allowed_secciones=secciones_disponibles,
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
        sesion.delete()
        messages.success(request, "Sesión eliminada.")
        return redirect("profesorpanel:sesiones")
    return render(
        request,
        "login/admin/confirm_delete.html",
        {"object": sesion, "back_url": "profesorpanel:sesiones", "title": "Eliminar sesión"},
    )



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
    sesiones = GameSession.objects.filter(profesor=request.user)
    secciones = SeccionEstudiantes.objects.filter(sesiones__in=sesiones).distinct().order_by("-fecha_creacion")

    form = SeccionEstudiantesForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sección creada/actualizada correctamente.")
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
#Fin nuevo modificar cantidad equipos 10/5