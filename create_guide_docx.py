import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_guide():
    doc = docx.Document()

    # Configuración de márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colores temáticos
    COLOR_PRIMARY = RGBColor(27, 54, 93)      # #1B365D Azul marino profundo
    COLOR_SECONDARY = RGBColor(43, 108, 176)  # #2B6CB0 Azul elegante
    COLOR_TEXT = RGBColor(45, 55, 72)         # #2D3748 Gris texto
    COLOR_MUTED = RGBColor(113, 128, 150)     # #718096 Gris secundario
    COLOR_CODE = RGBColor(16, 120, 75)        # Verde código
    HEX_BG_CODE = "F7FAFC"
    HEX_BORDER_CODE = "CBD5E0"
    HEX_BG_HEADER = "2B6CB0"

    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=140, bottom=140, left=200, right=200):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def add_command_box(cmd, title=None):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, HEX_BG_CODE)
        set_cell_margins(cell, top=150, bottom=150, left=250, right=250)

        # Bordes de la celda
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER_CODE}"/>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="2B6CB0"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER_CODE}"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER_CODE}"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15

        if title:
            run_title = p.add_run(f"📌 {title}\n")
            run_title.font.name = "Calibri"
            run_title.font.size = Pt(9.5)
            run_title.font.bold = True
            run_title.font.color.rgb = COLOR_SECONDARY

        run_cmd = p.add_run(cmd)
        run_cmd.font.name = "Consolas"
        run_cmd.font.size = Pt(10)
        run_cmd.font.bold = True
        run_cmd.font.color.rgb = RGBColor(30, 41, 59)

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(6)

    def add_callout(text, icon="ℹ️", title=None):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "EDF2F7")
        set_cell_margins(cell, top=140, bottom=140, left=240, right=240)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
            f'<w:left w:val="single" w:sz="20" w:space="0" w:color="3182CE"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15

        if title:
            r_title = p.add_run(f"{icon} {title}\n")
            r_title.font.name = "Calibri"
            r_title.font.size = Pt(10)
            r_title.font.bold = True
            r_title.font.color.rgb = COLOR_PRIMARY

        r_text = p.add_run(text)
        r_text.font.name = "Calibri"
        r_text.font.size = Pt(9.5)
        r_text.font.color.rgb = COLOR_TEXT

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(6)

    # ==================== PORTADA / ENCABEZADO ====================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(10)
    title_p.paragraph_format.space_after = Pt(4)
    run_t = title_p.add_run("GUÍA DE INSTALACIÓN Y CONFIGURACIÓN")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(16)
    run_sub = sub_p.add_run("Django Moderno + MongoDB Backend Oficial con Django Admin")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = COLOR_SECONDARY

    # Metadata / Tabla info
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Proyecto:", "djangopractica"),
        ("Tecnologías:", "Django 6.1, MongoDB, django-mongodb-backend, PyMongo 4.18"),
        ("Base de Datos:", "MongoDB Local (puerto 27017) -> djangopractica_db"),
        ("Panel Administrativo:", "Habilitado y 100% funcional con ObjectId nativo"),
    ]
    for i, (k, v) in enumerate(meta_data):
        cell_k = meta_table.cell(i, 0)
        cell_v = meta_table.cell(i, 1)
        cell_k.width = Inches(1.8)
        cell_v.width = Inches(4.7)
        set_cell_background(cell_k, "F7FAFC")
        set_cell_background(cell_v, "FFFFFF")
        set_cell_margins(cell_k, top=60, bottom=60, left=100, right=100)
        set_cell_margins(cell_v, top=60, bottom=60, left=100, right=100)
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_before = Pt(2)
        pk.paragraph_format.space_after = Pt(2)
        rk = pk.add_run(k)
        rk.font.name = "Calibri"
        rk.font.size = Pt(9.5)
        rk.font.bold = True
        rk.font.color.rgb = COLOR_PRIMARY

        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_before = Pt(2)
        pv.paragraph_format.space_after = Pt(2)
        rv = pv.add_run(v)
        rv.font.name = "Calibri"
        rv.font.size = Pt(9.5)
        rv.font.color.rgb = COLOR_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Función para encabezados
    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(3)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_SECONDARY
        return h

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix + " ")
            rb.font.name = "Calibri"
            rb.font.size = Pt(10)
            rb.font.bold = True
            rb.font.color.rgb = COLOR_TEXT
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT
        return p

    # ==================== SECCIÓN 1: INTRODUCCIÓN ====================
    add_h1("1. Introducción y Selección de Arquitectura")
    add_p(
        "Tradicionalmente, en tutoriales antiguos de Django y MongoDB se utilizaba la librería 'djongo'. "
        "Sin embargo, 'djongo' quedó abandonada y solo es compatible con versiones obsoletas de Django (hasta la 3.1/3.2). "
        "Al intentar usarla con Django moderno se presentan fallos críticos de sintaxis SQL y migraciones."
    )
    add_p(
        "Por esta razón, MongoDB lanzó el soporte oficial: django-mongodb-backend. "
        "Este paquete fue diseñado específicamente para las versiones modernas de Django (5.x y 6.x) y permite:"
    )
    add_p("• Integrar el ORM estándar de Django con colecciones de MongoDB sin emular SQL defectuoso.")
    add_p("• Usar ObjectIdAutoField nativo de MongoDB en lugar de IDs numéricos relacionales.")
    add_p("• Soporte total para el panel de administración (Django Admin), sistema de usuarios y sesiones.")

    add_callout(
        "Regla de versiones: El paquete django-mongodb-backend sigue la misma numeración que Django. "
        "Por ejemplo, para Django 6.1.x se instala django-mongodb-backend==6.1.*.",
        icon="⭐",
        title="Compatibilidad Garantizada"
    )

    # ==================== SECCIÓN 2: PASO A PASO ====================
    add_h1("2. Paso a Paso Completo con Comandos")

    # Paso 1
    add_h2("Paso 1: Creación del Entorno Virtual (venv)")
    add_p(
        "Para mantener el proyecto aislado y evitar conflictos entre versiones de paquetes globales, "
        "se crea y activa un entorno virtual en la raíz del proyecto."
    )
    add_command_box(
        "# 1. Abrir terminal en la carpeta del proyecto\n"
        "cd \"c:\\Users\\Dell Latitude i7 8th\\Desktop\\djangopractica\"\n\n"
        "# 2. Crear el entorno virtual llamado .venv\n"
        "python -m venv .venv\n\n"
        "# 3. Activar el entorno virtual en PowerShell:\n"
        ".\\.venv\\Scripts\\Activate.ps1\n\n"
        "# (Si usas CMD tradicional, ejecuta: .\\.venv\\Scripts\\activate.bat)",
        title="Creación y activación de entorno virtual"
    )

    # Paso 2
    add_h2("Paso 2: Instalación de Dependencias Necesarias")
    add_p(
        "Instalamos directamente el conector oficial de MongoDB para Django. Pip resuelve e instala automáticamente "
        "la versión compatible de Django (6.1.x), el driver pymongo y utilidades asociadas."
    )
    add_command_box(
        ".\\.venv\\Scripts\\pip install django-mongodb-backend",
        title="Instalación del conector oficial"
    )
    add_p(
        "Las dependencias instaladas quedan registradas en requirements.txt: "
        "django==6.1.1, django-mongodb-backend==6.1.0, pymongo==4.18.2, dnspython, sqlparse, asgiref, tzdata."
    )

    # Paso 3
    add_h2("Paso 3: Creación del Proyecto Django con la Plantilla Oficial")
    add_p(
        "MongoDB Labs proporciona una plantilla oficial para django-admin startproject que viene preconfigurada "
        "con las migraciones adaptadas para MongoDB (carpeta mongo_migrations) y las clases de configuración para Admin y Auth."
    )
    add_command_box(
        ".\\.venv\\Scripts\\django-admin.exe startproject config --template https://github.com/mongodb-labs/django-mongodb-project/archive/refs/heads/6.0.x.zip .",
        title="Generar proyecto con plantilla oficial MongoDB"
    )
    add_p(
        "Nota: El punto final (.) indica que el archivo manage.py y la estructura se creen directamente en la carpeta actual sin anidar carpetas innecesarias."
    )

    # Paso 4
    add_h2("Paso 4: Creación de la Aplicación de Django (miapp)")
    add_p(
        "Creamos la aplicación interna (en este caso llamada miapp) utilizando la plantilla para aplicaciones de MongoDB, "
        "la cual define correctamente el default_auto_field como ObjectIdAutoField."
    )
    add_command_box(
        ".\\.venv\\Scripts\\python.exe manage.py startapp miapp --template https://github.com/mongodb-labs/django-mongodb-app/archive/refs/heads/5.2.x.zip",
        title="Generar la aplicación miapp"
    )

    # Paso 5
    add_h2("Paso 5: Configuración de config/settings.py")
    add_p(
        "En el archivo config/settings.py se realizaron los ajustes clave para MongoDB y Django Admin:"
    )
    
    settings_code = (
        "# 1. Clave primaria global de MongoDB\n"
        "DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'\n\n"
        "# 2. Aplicaciones instaladas con compatibilidad para Admin y Auth\n"
        "INSTALLED_APPS = [\n"
        "    'config.apps.MongoAdminConfig',          # Reemplaza 'django.contrib.admin'\n"
        "    'config.apps.MongoAuthConfig',           # Reemplaza 'django.contrib.auth'\n"
        "    'config.apps.MongoContentTypesConfig',   # Reemplaza 'django.contrib.contenttypes'\n"
        "    'django.contrib.sessions',\n"
        "    'django.contrib.messages',\n"
        "    'django.contrib.staticfiles',\n"
        "    'django_mongodb_backend',                # Backend oficial MongoDB\n"
        "    'miapp.apps.MiappConfig',                # Tu aplicación\n"
        "]\n\n"
        "# 3. Conexión a la base de datos MongoDB\n"
        "DATABASES = {\n"
        "    'default': {\n"
        "        'ENGINE': 'django_mongodb_backend',\n"
        "        'HOST': 'mongodb://localhost:27017/',\n"
        "        'NAME': 'djangopractica_db',\n"
        "    },\n"
        "}\n"
        "DATABASE_ROUTERS = ['django_mongodb_backend.routers.MongoRouter']\n\n"
        "# 4. Módulos de migración compatibles con MongoDB\n"
        "MIGRATION_MODULES = {\n"
        "    'admin': 'mongo_migrations.admin',\n"
        "    'auth': 'mongo_migrations.auth',\n"
        "    'contenttypes': 'mongo_migrations.contenttypes',\n"
        "}\n\n"
        "# 5. Hosts permitidos e Idioma\n"
        "ALLOWED_HOSTS = ['*']\n"
        "LANGUAGE_CODE = 'es-es'\n"
        "TIME_ZONE = 'UTC'"
    )
    add_command_box(settings_code, title="Fragmentos clave en config/settings.py")

    # Paso 6
    add_h2("Paso 6: Definición del Modelo y Registro en el Admin")
    add_p(
        "En miapp/models.py se define el modelo Articulo. Al heredar de models.Model, Django y django-mongodb-backend "
        "gestionarán automáticamente el identificador _id como un ObjectId de MongoDB:"
    )
    model_code = (
        "# miapp/models.py\n"
        "from django.db import models\n\n"
        "class Articulo(models.Model):\n"
        "    titulo = models.CharField(max_length=200, verbose_name='Título')\n"
        "    descripcion = models.TextField(verbose_name='Descripción', blank=True)\n"
        "    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')\n"
        "    activo = models.BooleanField(default=True, verbose_name='Activo')\n\n"
        "    class Meta:\n"
        "        verbose_name = 'Artículo'\n"
        "        verbose_name_plural = 'Artículos'\n\n"
        "    def __str__(self):\n"
        "        return self.titulo"
    )
    add_command_box(model_code, title="miapp/models.py")

    add_p("En miapp/admin.py se registra el modelo para que aparezca en el Django Admin con filtros y búsqueda:")
    admin_code = (
        "# miapp/admin.py\n"
        "from django.contrib import admin\n"
        "from .models import Articulo\n\n"
        "@admin.register(Articulo)\n"
        "class ArticuloAdmin(admin.ModelAdmin):\n"
        "    list_display = ('id', 'titulo', 'activo', 'creado_en')\n"
        "    search_fields = ('titulo', 'descripcion')\n"
        "    list_filter = ('activo', 'creado_en')"
    )
    add_command_box(admin_code, title="miapp/admin.py")

    # Paso 7
    add_h2("Paso 7: Ejecución de Migraciones hacia MongoDB")
    add_p(
        "Django genera los archivos de migración y los aplica directamente en las colecciones de MongoDB:"
    )
    add_command_box(
        "# Crear archivo de migración para miapp\n"
        ".\\.venv\\Scripts\\python.exe manage.py makemigrations\n\n"
        "# Aplicar todas las migraciones a MongoDB (admin, auth, contenttypes, miapp, sessions)\n"
        ".\\.venv\\Scripts\\python.exe manage.py migrate",
        title="Comandos de migración"
    )
    add_p(
        "Al completarse, se crean las colecciones en MongoDB: auth_user, django_session, miapp_articulo, django_admin_log, etc."
    )

    # Paso 8
    add_h2("Paso 8: Creación del Superusuario para el Admin")
    add_p("Para poder ingresar al panel en /admin/ se genera un usuario administrador:")
    add_command_box(
        "# Modo interactivo (te solicita usuario, correo y clave):\n"
        ".\\.venv\\Scripts\\python.exe manage.py createsuperuser\n\n"
        "# O modo rápido mediante shell:\n"
        ".\\.venv\\Scripts\\python.exe manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')\"",
        title="Creación del Administrador"
    )
    add_callout(
        "Credenciales creadas en tu proyecto:\n• Usuario: admin\n• Contraseña: admin1234",
        icon="🔑",
        title="Acceso al Panel Admin"
    )

    # Paso 9
    add_h2("Paso 9: Ejecutar el Servidor de Desarrollo")
    add_p("Para levantar el servicio web local y poder consultar el proyecto en el navegador:")
    add_command_box(
        ".\\.venv\\Scripts\\python.exe manage.py runserver",
        title="Iniciar servidor Django"
    )
    add_p(
        "Enlaces de acceso:\n"
        "• Panel de Administración: http://127.0.0.1:8000/admin/\n"
        "• Página Principal (Lista de artículos): http://127.0.0.1:8000/"
    )

    # ==================== SECCIÓN 3: SOLUCIÓN DE PROBLEMAS ====================
    add_h1("3. Solución de Problemas Frecuentes")

    add_p("A) Error '127.0.0.1 rechazó la conexión (ERR_CONNECTION_REFUSED)':", bold_prefix="Problema 1:")
    add_p(
        "Causa: El comando 'python manage.py runserver' no está ejecutándose en la terminal o la ventana se cerró.\n"
        "Solución: Abre PowerShell, activa el entorno virtual y ejecuta de nuevo 'python manage.py runserver'."
    )

    add_p("B) Error de conexión con MongoDB (ServerSelectionTimeoutError):", bold_prefix="Problema 2:")
    add_p(
        "Causa: El servicio local de MongoDB (mongod) está detenido.\n"
        "Solución: Abre Servicios de Windows (services.msc) e inicia el servicio 'MongoDB Server', o ejecuta 'mongod' en terminal."
    )

    add_p("C) Error de permisos al activar venv en PowerShell ('La ejecución de scripts está deshabilitada'):", bold_prefix="Problema 3:")
    add_p(
        "Solución: Ejecuta en PowerShell como Administrador:\n"
        "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    )

    # ==================== SECCIÓN 4: TABLA RESUMEN ====================
    add_h1("4. Tabla Resumen de Comandos Rápidos")

    summary_table = doc.add_table(rows=7, cols=2)
    summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_content = [
        ("Acción", "Comando"),
        ("1. Activar Entorno Virtual", ".\\.venv\\Scripts\\Activate.ps1"),
        ("2. Instalar Paquetes", "pip install django-mongodb-backend"),
        ("3. Crear Migraciones", "python manage.py makemigrations"),
        ("4. Aplicar Migraciones a MongoDB", "python manage.py migrate"),
        ("5. Crear Superusuario", "python manage.py createsuperuser"),
        ("6. Iniciar Servidor", "python manage.py runserver"),
    ]
    for row_idx, (col0, col1) in enumerate(table_content):
        c0 = summary_table.cell(row_idx, 0)
        c1 = summary_table.cell(row_idx, 1)
        c0.width = Inches(2.5)
        c1.width = Inches(4.0)
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)

        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)

        if row_idx == 0:
            set_cell_background(c0, HEX_BG_HEADER)
            set_cell_background(c1, HEX_BG_HEADER)
            r0 = p0.add_run(col0)
            r1 = p1.add_run(col1)
            r0.font.bold = True
            r1.font.bold = True
            r0.font.color.rgb = RGBColor(255, 255, 255)
            r1.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg_color = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(c0, bg_color)
            set_cell_background(c1, bg_color)
            r0 = p0.add_run(col0)
            r0.font.size = Pt(9.5)
            r0.font.bold = True
            r0.font.color.rgb = COLOR_PRIMARY
            r1 = p1.add_run(col1)
            r1.font.name = "Consolas"
            r1.font.size = Pt(9)
            r1.font.color.rgb = RGBColor(30, 41, 59)

    output_path = r"c:\Users\Dell Latitude i7 8th\Desktop\djangopractica\Guia_Instalacion_Django_MongoDB.docx"
    doc.save(output_path)
    print(f"Documento guardado con éxito en: {output_path}")

if __name__ == "__main__":
    create_guide()
