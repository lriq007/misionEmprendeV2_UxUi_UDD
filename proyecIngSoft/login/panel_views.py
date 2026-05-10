from django.shortcuts import render, redirect


# ===============================
#   Panel ADMIN — páginas estáticas
# ===============================

def admin_dashboard(request):
    return render(request, "login/admin/dashboard.html", {
        "seccion_count": 0, "sesion_count": 0, "topic_count": 0,
        "challenge_count": 0, "tablet_count": 0, "evaluation_count": 0,
        "profesor_count": 0, "equipos_count": 0, "estudiantes_count": 0,
        "admin_count": 0, "carrera_segments": [], "carrera_gradient": "#fbbf24 0% 100%",
        "top_equipos": [], "sesiones_recientes": [],
    })


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


def admin_sesiones(request):
    if request.method == "POST":
        return redirect("adminpanel:sesiones")
    return render(request, "login/admin/sesiones.html", {"sesiones": [], "q": ""})


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
    if request.method == "POST":
        return redirect("adminpanel:topics")
    return render(request, "login/admin/topics.html", {"topics": [], "q": ""})


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


def admin_challenges(request):
    if request.method == "POST":
        return redirect("adminpanel:challenges")
    return render(request, "login/admin/challenges.html", {"challenges": [], "q": ""})


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


# ===============================
#   Panel PROFESOR — páginas estáticas
# ===============================

def profesor_dashboard(request):
    return render(request, "login/profesor/dashboard.html", {
        "sesiones": [], "secciones": [], "sesion_count": 0,
        "seccion_count": 0, "equipos_count": 0, "estudiantes_count": 0,
        "top_equipos": [], "ranking": [], "q": "",
    })


def profesor_sesiones(request):
    if request.method == "POST":
        return redirect("profesorpanel:sesiones")
    return render(request, "login/profesor/sesiones.html", {"sesiones": []})


def profesor_sesion_editar(request, pk):
    if request.method == "POST":
        return redirect("profesorpanel:sesiones")
    return render(request, "login/admin/form.html", {
        "title": "Editar sesión", "back_url": "profesorpanel:sesiones",
    })


def profesor_sesion_eliminar(request, pk):
    if request.method == "POST":
        return redirect("profesorpanel:sesiones")
    return render(request, "login/admin/confirm_delete.html", {
        "back_url": "profesorpanel:sesiones", "title": "Eliminar sesión",
    })


def profesor_alumnos(request):
    if request.method == "POST":
        return redirect("profesorpanel:alumnos")
    return render(request, "login/profesor/alumnos.html", {"estudiantes": []})


def profesor_equipos(request):
    if request.method == "POST":
        return redirect("profesorpanel:equipos")
    return render(request, "login/profesor/equipos.html", {"equipos": []})


def profesor_secciones(request):
    if request.method == "POST":
        return redirect("profesorpanel:secciones")
    return render(request, "login/profesor/secciones.html", {"secciones": []})
