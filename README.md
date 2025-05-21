# Gestor de Tareas RA 🚀

![Icono de la Aplicación](recursos/ico/app.ico)

## 📝 Descripción

Gestor de Tareas RA es una aplicación de escritorio intuitiva y fácil de usar, desarrollada en Python con Tkinter. Permite administrar eficientemente tareas pendientes y completadas, ideal para entornos educativos donde se necesita hacer un seguimiento de las actividades asignadas a estudiantes.

**Versión:** 1.2.0 (Actualizada con patrones de diseño y MVC)
**Autor:** Rodrigo Angeloni
**Fecha:** Mayo 2025

## ✨ Características Principales

*   **📝 Registro Detallado:** Añade tareas con información completa del estudiante (cédula, nombre, apellido, curso, turno) y la descripción de la acción pendiente.
*   **🔄 Gestión de Estados:** Marca tareas como "completadas" 🟢 o muévelas de nuevo a "pendientes" 🔴.
*   **📑 Organización por Pestañas:** Visualiza claramente las tareas pendientes y las completadas en secciones separadas.
*   **✏️ Edición Fácil:** Modifica la información de cualquier tarea existente con un doble clic o seleccionándola.
*   **🗑️ Eliminación Segura:** Borra tareas con confirmación previa.
*   **🔍 Búsqueda Inteligente:** Filtra rápidamente las tareas por cualquier campo (cédula, nombre, curso, etc.).
*   **💾 Almacenamiento Persistente:** Todas las tareas se guardan en una base de datos SQLite (`database.db`), asegurando que tu información no se pierda.
*   **📊 Migración de Datos:** Si tienes un archivo `alumnos_pendientes.csv` de una versión anterior, la aplicación puede migrar esos datos a la nueva base de datos automáticamente.
*   **🎨 Interfaz Gráfica Moderna:** Diseño amigable y con estilo gracias a `tkinter.ttk`.
*   **🔔 Notificaciones y Estado:** Una barra de estado te mantiene informado sobre las acciones realizadas.
*   **📝 Exportación a CSV:** Exporta las tareas a un archivo CSV para compartir o analizar en otras herramientas.
*   **📊 Generación de Informes:** Visualiza estadísticas sobre las tareas pendientes y completadas.
*   **🔄 Actualización Automática:** Activa la actualización automática para mantener la información siempre al día.
*   **🏗️ Arquitectura MVC:** Organización de código siguiendo el patrón Modelo-Vista-Controlador para mejor mantenibilidad.
*   **🧩 DAO Pattern:** Acceso a datos encapsulado mediante el patrón Data Access Object para mayor flexibilidad con diferentes fuentes de datos.

## 💻 Requisitos del Sistema

*   Windows 7/8/10/11 (Probablemente compatible con otros sistemas operativos que soporten Python y Tkinter).
*   Python 3.x (si se ejecuta desde el código fuente).
*   Dependencias: tkinter (incluido en Python), python-dotenv
*   No requiere instalación adicional si se usa el ejecutable portable.

## 🚀 Instalación y Ejecución

La aplicación está diseñada para ser portable.

1.  **Desde el Ejecutable (Recomendado para usuarios finales):**
    *   Descarga el archivo `GestorTareasRA.exe` (o el nombre que tenga el ejecutable generado).
    *   Colócalo en una carpeta de tu elección.
    *   ¡Haz doble clic para ejecutar!
    *   La base de datos `database.db` se creará automáticamente en la misma carpeta.

2.  **Desde el Código Fuente (Para desarrolladores):**
    *   Clona o descarga el repositorio.
    *   Asegúrate de tener Python 3 instalado.
    *   Instala las dependencias: `pip install python-dotenv`
    *   Abre una terminal en la carpeta del proyecto.
    *   Ejecuta el script: `python main.py`

## 🛠️ Uso de la Aplicación

1.  **➕ Agregar Nueva Tarea:**
    *   Ve a la pestaña "Tareas Pendientes 🔴".
    *   Completa los campos en la sección "Nueva Tarea".
    *   Haz clic en el botón "➕ Agregar".

2.  **✏️ Editar Tarea Existente:**
    *   Selecciona la tarea que deseas modificar en cualquiera de las listas (pendientes o completadas).
    *   Haz doble clic en la tarea o simplemente carga sus datos en el formulario. Los botones "✏️ Actualizar" y "❌ Cancelar" se activarán.
    *   Realiza los cambios necesarios en el formulario.
    *   Haz clic en "✏️ Actualizar" para guardar los cambios.
    *   Si deseas descartar los cambios, haz clic en "❌ Cancelar".

3.  **✓ Marcar Tarea como Completada:**
    *   En la pestaña "Tareas Pendientes 🔴", selecciona la tarea que ha sido finalizada.
    *   Haz clic en el botón "✓ Marcar como Completado" (ubicado debajo de las listas).

4.  **⟲ Marcar Tarea como Pendiente:**
    *   En la pestaña "Tareas Completadas 🟢", selecciona la tarea que necesitas reabrir.
    *   Haz clic en el botón "⟲ Marcar como Pendiente".

5.  **🔍 Buscar Tareas:**
    *   Utiliza el campo de texto en la sección "Búsqueda" para escribir tu criterio (nombre, cédula, curso, etc.).
    *   Presiona "🔍 Buscar" o simplemente escribe y la lista se filtrará automáticamente.
    *   Para ver todas las tareas de nuevo, haz clic en "🔄 Limpiar".

6.  **🗑️ Eliminar Tarea:**
    *   Selecciona la tarea que deseas eliminar (desde pendientes o completadas).
    *   Haz clic en el botón "🗑️ Eliminar Tarea". Se te pedirá confirmación.
    
7.  **📝 Exportar Datos:**
    *   Ve al menú "Archivo" -> "Exportar a CSV".
    *   Selecciona la ubicación donde deseas guardar el archivo.
    
8.  **📊 Ver Informes:**
    *   Ve al menú "Herramientas" -> "Generar informe".
    *   Se abrirá una ventana con estadísticas de las tareas.
    
9.  **🔄 Activar Actualización Automática:**
    *   Ve al menú "Herramientas" -> "Activar actualización automática".
    *   La aplicación actualizará los datos cada 30 segundos.

## 📁 Estructura de Archivos

```
/GestorTareasRA/
│
├── main.py                    # Punto de entrada principal (ejecutable)
├── database.db                # Base de datos SQLite (creada automáticamente)
├── .env                       # Variables de configuración
├── README.md                  # Este archivo
│
├── /models/                   # Modelos de datos (Patrón MVC)
│   ├── __init__.py
│   └── task.py                # Clase Task para representar tareas
│
├── /dao/                      # Data Access Objects
│   ├── __init__.py
│   └── task_dao.py            # Acceso a base de datos para tareas
│
├── /controllers/              # Controladores (Patrón MVC)
│   ├── __init__.py
│   └── task_controller.py     # Controlador para tareas
│
├── /utils/                    # Funciones de utilidad
│   ├── __init__.py
│   └── util.py                # Funciones de utilidad varias
│
└── /recursos/
    └── /ico/
        └── app.ico            # Icono de la aplicación
```

## 🔧 Desarrollo

El proyecto fue desarrollado utilizando:
*   **Lenguaje:** Python 3.x
*   **Interfaz Gráfica:** Tkinter (`tkinter` y `tkinter.ttk`)
*   **Base de Datos:** SQLite 3
*   **Variables de Entorno:** python-dotenv
*   **Arquitectura:** Modelo-Vista-Controlador (MVC)
*   **Patrones de Diseño:** DAO (Data Access Object)
*   **Empaquetado (Sugerido):** PyInstaller para generar el ejecutable (`.exe`) portable.

**Comando de ejemplo para generar el ejecutable con PyInstaller (desde la terminal):**
```bash
pyinstaller --name GestorTareasRA --onefile --windowed --icon=recursos/ico/app.ico main.py
```
*   `--name GestorTareasRA`: Define el nombre del ejecutable.
*   `--onefile`: Crea un solo archivo ejecutable.
*   `--windowed`: Evita que se abra una consola de comandos al ejecutar la app.
*   `--icon=recursos/ico/app.ico`: Asigna el icono a la aplicación.

## 📜 Licencia

© 2025 Rodrigo Angeloni. Todos los derechos reservados.

---