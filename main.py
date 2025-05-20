"""
Archivo principal de la aplicación. 
Implementa la interfaz de usuario utilizando tkinter y se comunica con el controlador.
"""

import sys
import os  # Ensure os is imported for path manipulation

# --- Start of sys.path modification ---
# Get the absolute path of the directory containing the current script (main.py)
# This is effectively the project root for module resolution.
_project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to sys.path if it's not already there.
# This ensures that Python can find the 'models', 'dao', 'controllers', 'utils' packages.
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
# --- End of sys.path modification ---

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Importar módulos propios
from models.task import Task
from dao.task_dao import TaskDAO
from controllers.task_controller import TaskController
from utils.util import Util

class StudentTaskManager:
    """Clase principal de la aplicación que implementa la interfaz de usuario."""
    
    def __init__(self, root):
        """Inicializa la aplicación."""
        self.root = root
        app_version = os.getenv("APP_VERSION", "1.2.0")
        self.root.title(f"Gestor de Tareas RA v{app_version}")
        self.root.geometry("1200x650")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Variables
        self.current_index = None
        self.db_name = os.getenv("DATABASE_NAME", "database.db")
        self.current_tab = "pendientes"
        self.editing_mode = False
        self.accion_pendiente_entry = None 
        
        # Tema
        self.current_theme = "light" 
        self.style = ttk.Style()
        
        # Aplicar tema personalizado PRIMERO
        self.apply_custom_theme(self.current_theme)
        
        # Barra de estado (debe crearse antes de que el controlador intente usar update_status)
        self.create_status_bar() 

        # Inicializar el controlador
        self.controller = TaskController(self, self.db_name)

        # Crear interfaz (widgets principales como el notebook y las pestañas)
        self.create_widgets()
        
        # Cargar datos existentes en los árboles y actualizar la UI
        # Esto se hace después de que todos los widgets, incluidos los árboles, estén creados.
        if self.controller.load_tasks():
            self.controller.update_trees()

        # Mostrar mensaje inicial
        self.update_status("Aplicación iniciada correctamente. ¡Bienvenido!")
        
        # Configurar acción al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Maneja el evento de cierre de la ventana."""
        # Asegurarse de detener cualquier thread en ejecución
        if hasattr(self.controller, 'auto_refresh_enabled'):
            self.controller.auto_refresh_enabled = False
            
        self.root.destroy()
        
    def apply_custom_theme(self, theme_name="light"):
        """Aplica un tema personalizado a la aplicación"""
        self.current_theme = theme_name

        # Usar un tema base de ttk
        self.style.theme_use('clam')

        # Definir paletas de colores
        if theme_name == "dark":
            bg_color = "#2b2b2b"
            fg_color = "#dcdcdc"  # Color de texto principal
            accent_color = "#007acc" # Azul más vibrante para modo oscuro
            accent_dark = "#005f9e"
            widget_bg_color = "#3c3c3c" # Fondo para widgets como Entry, Treeview
            header_bg_color = "#005f9e" # Fondo para cabeceras de Treeview
            disabled_fg_color = "#7f7f7f"
            notebook_tab_bg = "#3c3c3c"
            notebook_tab_fg = "#dcdcdc"
            notebook_selected_tab_bg = accent_color
            notebook_selected_tab_fg = "#ffffff"
            status_bar_bg = "#3c3c3c"
            status_bar_fg = fg_color
            button_fg_color = "#ffffff" # Color de texto para botones principales
            
            # Colores específicos para botones de acción
            add_btn_bg = "#27ae60" # Verde
            add_btn_active_bg = "#229954"
            update_btn_bg = "#f39c12" # Naranja
            update_btn_active_bg = "#d68910"
            delete_btn_bg = "#e74c3c" # Rojo
            delete_btn_active_bg = "#cb4335"
            cancel_btn_bg = "#7f8c8d" # Gris
            cancel_btn_active_bg = "#707b7c"

        else: # Tema claro (light)
            bg_color = "#f5f5f5"
            fg_color = "#2c3e50"
            accent_color = "#3498db"
            accent_dark = "#2980b9"
            widget_bg_color = "white"
            header_bg_color = accent_color
            disabled_fg_color = "#95a5a6"
            notebook_tab_bg = '#d6eaf8'
            notebook_tab_fg = fg_color
            notebook_selected_tab_bg = accent_color
            notebook_selected_tab_fg = 'white'
            status_bar_bg = '#d6eaf8'
            status_bar_fg = fg_color
            button_fg_color = "white"

            add_btn_bg = '#1e8449'
            add_btn_active_bg = '#196f3d'
            update_btn_bg = '#b9770e'
            update_btn_active_bg = '#9c640c'
            delete_btn_bg = '#b03a2e'
            delete_btn_active_bg = '#96281b'
            cancel_btn_bg = '#5d6d7e'
            cancel_btn_active_bg = '#4a5864'

        # Configurar colores de la ventana principal
        self.root.configure(bg=bg_color)
        
        # Estilo para botones
        self.style.configure('TButton', 
                        font=('Segoe UI', 9),
                        background=accent_color,
                        foreground=button_fg_color)
        self.style.map('TButton', 
                  background=[('active', accent_dark), ('pressed', '#1f618d')], # Pressed color can be generic or themed
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        
        # Estilo para etiquetas
        self.style.configure('TLabel', 
                        font=('Segoe UI', 10),
                        background=bg_color,
                        foreground=fg_color)
        
        # Estilo para entradas
        self.style.configure('TEntry', 
                        font=('Segoe UI', 10),
                        fieldbackground=widget_bg_color,
                        foreground=fg_color,
                        insertcolor=fg_color) # Color del cursor
        
        # Estilo para combobox
        self.style.configure('TCombobox', 
                        font=('Segoe UI', 10),
                        fieldbackground=widget_bg_color,
                        foreground=fg_color)
        self.style.map('TCombobox',
                 fieldbackground=[('readonly', widget_bg_color)],
                 selectbackground=[('readonly', widget_bg_color)],
                 selectforeground=[('readonly', fg_color)],
                 background=[('readonly', widget_bg_color)])


        # Estilo para notebook (pestañas)
        self.style.configure('TNotebook', background=bg_color)
        self.style.configure('TNotebook.Tab', 
                        font=('Segoe UI', 10, 'bold'),
                        padding=[10, 4],
                        background=notebook_tab_bg,
                        foreground=notebook_tab_fg)
        self.style.map('TNotebook.Tab', 
                  background=[('selected', notebook_selected_tab_bg)],
                  foreground=[('selected', notebook_selected_tab_fg)],
                  expand=[('selected', [1, 1, 1, 0])])
        
        # Estilo para frames
        self.style.configure('TFrame', background=bg_color)
        
        # Estilo para LabelFrame
        self.style.configure('TLabelframe', 
                        font=('Segoe UI', 10, 'bold'),
                        background=bg_color,
                        foreground=fg_color,
                        bordercolor=accent_color if theme_name == 'dark' else '#c0c0c0')
        self.style.configure('TLabelframe.Label', 
                        font=('Segoe UI', 10, 'bold'),
                        background=bg_color, # Match TLabelframe background
                        foreground=fg_color)
        
        # Estilo para el Treeview (tablas)
        self.style.configure('Treeview', 
                        font=('Segoe UI', 9),
                        background=widget_bg_color,
                        foreground=fg_color,
                        fieldbackground=widget_bg_color,
                        rowheight=25)
        self.style.configure('Treeview.Heading', 
                        font=('Segoe UI', 10, 'bold'),
                        background=header_bg_color,
                        foreground=button_fg_color) # Usar button_fg_color para contraste
        self.style.map('Treeview', 
                  background=[('selected', accent_color)],
                  foreground=[('selected', button_fg_color)])
        
        # Botones especiales
        self.style.configure('Add.TButton', font=('Segoe UI', 9, 'bold'), background=add_btn_bg, foreground=button_fg_color)
        self.style.map('Add.TButton', background=[('active', add_btn_active_bg), ('pressed', add_btn_active_bg)], foreground=[('!disabled', button_fg_color)])
        
        self.style.configure('Update.TButton', font=('Segoe UI', 9, 'bold'), background=update_btn_bg, foreground=button_fg_color)
        self.style.map('Update.TButton', background=[('active', update_btn_active_bg), ('pressed', update_btn_active_bg)], foreground=[('!disabled', button_fg_color)])
        
        self.style.configure('Delete.TButton', font=('Segoe UI', 9, 'bold'), background=delete_btn_bg, foreground=button_fg_color)
        self.style.map('Delete.TButton', background=[('active', delete_btn_active_bg), ('pressed', delete_btn_active_bg)], foreground=[('!disabled', button_fg_color)])
                  
        self.style.configure('Cancel.TButton', font=('Segoe UI', 9, 'bold'), background=cancel_btn_bg, foreground=button_fg_color)
        self.style.map('Cancel.TButton', background=[('active', cancel_btn_active_bg), ('pressed', cancel_btn_active_bg)], foreground=[('!disabled', button_fg_color)])
                  
        # Estilo para barra de estado
        self.style.configure('Status.TLabel', font=('Segoe UI', 9), background=status_bar_bg, foreground=status_bar_fg)

        # Forzar actualización de widgets existentes si es necesario (a veces ttk es caprichoso)
        # Esto puede ser más complejo y requerir iterar sobre widgets y reconfigurarlos.
        # Por ahora, confiamos en que la reconfiguración del estilo global sea suficiente.
        # Si no, se podría necesitar algo como:
        # for widget in self.root.winfo_children():
        #     widget.update() # o reconfigurar su estilo específico si es un ttk widget

    def toggle_theme(self):
        """Cambia entre el tema claro y oscuro."""
        if self.current_theme == "light":
            self.apply_custom_theme("dark")
            self.update_status("Tema oscuro activado.")
        else:
            self.apply_custom_theme("light")
            self.update_status("Tema claro activado.")

    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Frame para tareas pendientes
        self.pendientes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pendientes_frame, text="Tareas Pendientes 🔴")
        
        # Frame para tareas completadas
        self.completadas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.completadas_frame, text="Tareas Completadas 🟢")
        
        # Configurar pesos para expansión
        self.pendientes_frame.columnconfigure(0, weight=1)
        self.pendientes_frame.rowconfigure(1, weight=1)
        self.completadas_frame.columnconfigure(0, weight=1)
        self.completadas_frame.rowconfigure(0, weight=1)
        
        # Crear widgets para ambas pestañas
        self.create_pendientes_tab()
        self.create_completadas_tab()
        self.create_controls()
        
        # Detectar cambios de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)
        
    def create_status_bar(self):
        """Crea una barra de estado en la parte inferior de la ventana"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=2, column=0, sticky="ew")
        
        self.status_label = ttk.Label(self.status_frame, style='Status.TLabel', 
                                     text="Listo", relief="sunken", anchor="w")
        self.status_label.pack(fill="x")
        
    def update_status(self, message):
        """Actualiza el mensaje de la barra de estado"""
        self.status_label.config(text=message)
        
    def tab_changed(self, event):
        """Maneja el cambio entre pestañas"""
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        if "Pendientes" in tab_name:
            self.current_tab = "pendientes"
            self.update_status("Visualizando tareas pendientes")
        else:
            self.current_tab = "completadas"
            self.update_status("Visualizando tareas completadas")
        
    def create_pendientes_tab(self):
        """Crea la pestaña de tareas pendientes."""
        # Frame de entrada de datos
        input_frame = ttk.LabelFrame(self.pendientes_frame, text="Nueva Tarea")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Campos del formulario - Divididos en dos columnas para mejor organización
        left_frame = ttk.Frame(input_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        
        right_frame = ttk.Frame(input_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nw")
        
        # Columna izquierda
        ttk.Label(left_frame, text="Cédula:").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.cédula = ttk.Entry(left_frame, width=20)
        self.cédula.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        
        ttk.Label(left_frame, text="Nombre:").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.nombre = ttk.Entry(left_frame, width=20)
        self.nombre.grid(row=1, column=1, sticky="w", padx=5, pady=8)
        
        ttk.Label(left_frame, text="Apellido:").grid(row=2, column=0, sticky="e", padx=5, pady=8)
        self.apellido = ttk.Entry(left_frame, width=20)
        self.apellido.grid(row=2, column=1, sticky="w", padx=5, pady=8)
        
        # Columna derecha
        ttk.Label(right_frame, text="Curso/Grado:").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.curso_grado = ttk.Combobox(right_frame, values=[
            "Pre Escolar", "1° Grado", "2° Grado", "3° Grado",
            "4° Grado", "5° Grado", "6° Grado", "7° Grado",
            "8° Grado", "9no Grado", "1° Curso", "2° Curso", "3° Curso"
        ], width=17)
        self.curso_grado.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        
        ttk.Label(right_frame, text="Turno:").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.turno = ttk.Combobox(right_frame, values=["Mañana", "Tarde"], width=17)
        self.turno.grid(row=1, column=1, sticky="w", padx=5, pady=8)
        
        ttk.Label(right_frame, text="Acción Pendiente:").grid(row=2, column=0, sticky="e", padx=5, pady=8)
        self.accion_pendiente_entry = ttk.Entry(right_frame, width=30) # Renombrado
        self.accion_pendiente_entry.grid(row=2, column=1, sticky="w", padx=5, pady=8)
        
        # Frame para botones
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Botones para agregar/editar con estilos mejorados
        self.add_btn = ttk.Button(btn_frame, text="➕ Agregar", 
                                style="Add.TButton", command=self.controller.add_task)
        self.add_btn.grid(row=0, column=0, padx=8)
        
        self.update_btn = ttk.Button(btn_frame, text="✏️ Actualizar", 
                                   style="Update.TButton", command=self.controller.update_task, 
                                   state="disabled")
        self.update_btn.grid(row=0, column=1, padx=8)
        
        self.cancel_btn = ttk.Button(btn_frame, text="❌ Cancelar", 
                                   style="Cancel.TButton", command=self.cancel_edit, 
                                   state="disabled")
        self.cancel_btn.grid(row=0, column=2, padx=8)
        
        # Lista de estudiantes pendientes con scrollbar
        tree_frame = ttk.Frame(self.pendientes_frame)
        tree_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        self.tree_pendientes = self.create_tree(tree_frame)
        
    def create_completadas_tab(self):
        """Crea la pestaña de tareas completadas."""
        # Lista de estudiantes completados con scrollbar
        tree_frame = ttk.Frame(self.completadas_frame)
        tree_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tree_completadas = self.create_tree(tree_frame)
        
    def create_controls(self):
        """Crea los controles y la barra de búsqueda."""
        # Barra de búsqueda y botones
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, pady=8, sticky="ew")
        
        # Frame para búsqueda
        search_frame = ttk.LabelFrame(control_frame, text="Búsqueda")
        search_frame.pack(side="left", padx=10, fill="x", expand=True)
        
        ttk.Label(search_frame, text="Filtrar por:").grid(row=0, column=0, padx=5, pady=8)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5, pady=8)
        self.search_entry.bind("<KeyRelease>", self.controller.search_tasks)
        
        ttk.Button(search_frame, text="🔍 Buscar", 
                 command=self.controller.search_tasks).grid(row=0, column=2, padx=5)
        
        ttk.Button(search_frame, text="🔄 Limpiar", 
                 command=self.controller.clear_search).grid(row=0, column=3, padx=5)
        
        # Frame para acciones
        btn_frame = ttk.LabelFrame(control_frame, text="Acciones")
        btn_frame.pack(side="right", padx=10)
        
        ttk.Button(btn_frame, text="✓ Marcar como Completado", 
                 command=lambda: self.controller.toggle_task_status("completada")).grid(row=0, column=0, padx=5, pady=8)
        ttk.Button(btn_frame, text="⟲ Marcar como Pendiente", 
                 command=lambda: self.controller.toggle_task_status("pendiente")).grid(row=0, column=1, padx=5, pady=8)
        ttk.Button(btn_frame, text="🗑️ Eliminar Tarea", 
                 style="Delete.TButton", command=self.controller.delete_task).grid(row=0, column=2, padx=5, pady=8)
        
        # Menú Archivo
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a CSV", command=self.controller.export_tasks_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Generar informe", command=self.controller.generate_and_show_report)
        tools_menu.add_command(label="Activar actualización automática", 
                              command=lambda: self.controller.toggle_auto_refresh(30))
        tools_menu.add_command(label="Cambiar Tema", command=self.toggle_theme) # Nueva opción de menú
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
    def show_about(self):
        """Muestra información sobre la aplicación."""
        author = os.getenv("AUTHOR_NAME", "Rodrigo Angeloni")
        app_version = os.getenv("APP_VERSION", "1.1.0")
        contact = os.getenv("CONTACT_EMAIL", "correo@ejemplo.com")
        
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de Gestor de Tareas RA")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        # Centrar en pantalla
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        frame = ttk.Frame(about_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Gestor de Tareas RA", 
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))
        
        ttk.Label(frame, text=f"Versión {app_version}", 
                 font=("Segoe UI", 12)).pack(pady=(0, 20))
        
        ttk.Label(frame, text=f"Desarrollado por: {author}", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        
        ttk.Label(frame, text=f"Contacto: {contact}", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        
        ttk.Label(frame, text=f"Fecha: {datetime.now().strftime('%B %Y')}", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        
        ttk.Label(frame, text="\nEsta aplicación permite gestionar tareas pendientes y completadas,\n"
                             "ideal para entornos educativos.", 
                 font=("Segoe UI", 9), justify="center").pack(pady=10)
        
        ttk.Button(frame, text="Cerrar", command=about_window.destroy).pack(pady=10)
        
    def create_tree(self, parent):
        """Crea un treeview con scrollbars."""
        # Frame para contener el treeview y scrollbars
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")
        
        # Configuración del treeview
        columns = ("ID", "Cédula", "Nombre", "Apellido", "Curso", "Turno", "Acción", "Creado", "Completado")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse",
                           yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configurar scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Posicionar elementos
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
        
        # Configurar columnas
        tree.heading("ID", text="ID")
        tree.column("ID", width=50, anchor="center")
        
        for col in columns[1:]:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        tree.column("Acción", width=200)
        tree.column("Creado", width=150)
        tree.column("Completado", width=150)
        
        # Eventos
        tree.bind("<<TreeviewSelect>>", self.load_selected)
        tree.bind("<Double-1>", self.on_item_double_click)
        
        return tree
        
    def load_selected(self, event):
        """Carga los datos de una tarea seleccionada en los campos."""
        widget = event.widget
        selected_item = widget.selection()
        
        if selected_item:
            values = widget.item(selected_item)['values']
            
            # Limpiar campos primero
            self.clear_fields()
            
            # Cargar valores
            self.cédula.insert(0, values[1])  # Cédula está en el índice 1 ahora
            self.nombre.insert(0, values[2])
            self.apellido.insert(0, values[3])
            self.curso_grado.set(values[4])
            self.turno.set(values[5])
            self.accion_pendiente_entry.insert(0, values[6]) # Renombrado
            
            # Guardar el ID de la tarea seleccionada
            self.current_index = values[0]
            
            # Actualizar barra de estado
            self.update_status(f"Registro seleccionado: {values[2]} {values[3]}")
            
    def on_item_double_click(self, event):
        """Activa el modo de edición al hacer doble clic."""
        self.toggle_edit_mode(True)
    
    def toggle_edit_mode(self, enable=True):
        """Activa o desactiva el modo de edición."""
        self.editing_mode = enable
        if enable:
            self.add_btn.config(state="disabled")
            self.update_btn.config(state="normal")
            self.cancel_btn.config(state="normal")
            self.update_status("Modo edición activado")
        else:
            self.add_btn.config(state="normal")
            self.update_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled") # Ensure cancel button is disabled when not in edit mode
            self.current_index = None
            self.update_status("Modo edición cancelado")
    
    def cancel_edit(self):
        """Cancela la edición actual."""
        self.clear_fields()
        self.toggle_edit_mode(False)
            
    def validate_fields(self):
        """Valida los campos del formulario."""
        # Validar Cédula
        is_valid_cedula, cedula_message = Util.validate_cedula(self.cédula.get())
        if not is_valid_cedula:
            messagebox.showerror("Error de Validación", cedula_message)
            self.cédula.focus_set()
            return False
            
        # Validar Nombre
        is_valid_nombre, nombre_message = Util.validate_name(self.nombre.get(), field_name="Nombre")
        if not is_valid_nombre:
            messagebox.showerror("Error de Validación", nombre_message)
            self.nombre.focus_set()
            return False

        # Validar Apellido
        is_valid_apellido, apellido_message = Util.validate_name(self.apellido.get(), field_name="Apellido")
        if not is_valid_apellido:
            messagebox.showerror("Error de Validación", apellido_message)
            self.apellido.focus_set()
            return False
            
        # Validar otros campos requeridos (Curso, Turno, Acción)
        other_required_fields = {
            "Curso/Grado": (self.curso_grado.get(), self.curso_grado),
            "Turno": (self.turno.get(), self.turno),
            "Acción Pendiente": (self.accion_pendiente_entry.get(), self.accion_pendiente_entry)
        }
        
        for field_name, (field_value, widget_ref) in other_required_fields.items():
            if not field_value or not field_value.strip(): # Check if empty or only whitespace
                messagebox.showerror("Error de Validación", f"El campo '{field_name}' no puede estar vacío.")
                # For Combobox, focus might not be as direct as Entry, but attempt it.
                # For Entry widgets, focus_set() is appropriate.
                if hasattr(widget_ref, 'focus_set'):
                    widget_ref.focus_set()
                return False
        
        return True
        
    def clear_fields(self):
        """Limpia los campos del formulario."""
        self.cédula.delete(0, tk.END)
        self.nombre.delete(0, tk.END)
        self.apellido.delete(0, tk.END)
        self.curso_grado.set('')
        self.turno.set('')
        self.accion_pendiente_entry.delete(0, tk.END) # Renombrado
        self.current_index = None # Asegurar que no hay índice seleccionado


def configurar_icono(root_window):
    """Configura el icono de la aplicación."""
    try:
        # Obtener la ruta del script actual para construir la ruta al icono
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "recursos", "ico", "app.ico")
        
        if os.path.exists(icon_path):
            root_window.iconbitmap(icon_path)
        else:
            print(f"Advertencia: No se encontró el archivo de icono en {icon_path}")
            # Optionally, update status bar if app instance is available and it's safe to do so
            # For example, if this function were a method of StudentTaskManager:
            # self.update_status("Advertencia: Icono no encontrado.")
    except tk.TclError as e:
        # This error can occur on some systems/configurations if icon setting fails
        print(f"Error de Tcl al configurar el icono (puede ser normal en algunos entornos): {e}")
    except Exception as e:
        print(f"Error inesperado al configurar el icono: {e}")
        # Optionally, update status bar
        # if hasattr(app_instance, 'update_status'): # Check if app_instance is defined and has update_status
        #     app_instance.update_status(f"Error al configurar icono: {e}")

# Punto de entrada de la aplicación
if __name__ == "__main__":
    # load_dotenv() is already called at the top-level module scope,
    # so environment variables should be loaded by now.

    main_root = tk.Tk()  # Create the main Tkinter window
    app_instance = StudentTaskManager(main_root)  # Create an instance of the application
    configurar_icono(main_root)  # Configure the application icon
    main_root.mainloop()  # Start the Tkinter event loop
