"""
Clase para manejar la lógica de la interfaz de usuario y conectar el DAO con la UI.
Implementa el patrón Controller en una arquitectura MVC simplificada.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import threading
import time

from dao.task_dao import TaskDAO
from models.task import Task
from utils.util import Util

class TaskController:
    """Controlador para manejar la lógica entre la UI y el DAO."""
    
    def __init__(self, app, db_name="database.db"):
        """Inicializa el controlador con referencia a la app y el DAO."""
        self.app = app
        self.task_dao = TaskDAO(db_name)
        self.pending_tasks = []
        self.completed_tasks = []
        self.last_search_query = ""
        self.auto_refresh_enabled = False
        self.auto_refresh_thread = None
        # Las tareas se cargarán explícitamente desde StudentTaskManager después de crear los widgets
    
    def load_tasks(self, query=None):
        """Carga tareas desde la base de datos, opcionalmente filtradas por una query."""
        try:
            if query:
                tasks = self.task_dao.search_tasks(query)
                self.app.update_status(f"Mostrando resultados para: '{query}'")
            else:
                tasks = self.task_dao.get_all_tasks()
                self.app.update_status(f"Tareas cargadas. Total: {len(tasks)}")
            
            self.pending_tasks = [task for task in tasks if task.status == "pendiente"]
            self.completed_tasks = [task for task in tasks if task.status == "completada"]
            
            return True
        except Exception as e:
            error_msg = f"Error al cargar tareas: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de Carga", error_msg)
            return False
    
    def update_trees(self):
        """Actualiza los árboles de tareas en la interfaz con las listas locales."""
        try:
            # Limpiar los trees
            for tree in [self.app.tree_pendientes, self.app.tree_completadas]:
                for item in tree.get_children():
                    tree.delete(item)
            
            # Insertar tareas pendientes
            for task in self.pending_tasks:
                values = (
                    task.id,
                    task.cedula,
                    task.nombre,
                    task.apellido,
                    task.curso,
                    task.turno,
                    task.accion,
                    task.fecha_creacion,
                    task.fecha_completado
                )
                self.app.tree_pendientes.insert("", "end", values=values, tags=("pendiente",))
            
            # Insertar tareas completadas
            for task in self.completed_tasks:
                values = (
                    task.id,
                    task.cedula,
                    task.nombre,
                    task.apellido,
                    task.curso,
                    task.turno,
                    task.accion,
                    task.fecha_creacion,
                    task.fecha_completado
                )
                self.app.tree_completadas.insert("", "end", values=values, tags=("completada",))
            
            # Configurar colores de las filas según el estado
            self.app.tree_pendientes.tag_configure("pendiente", foreground="#e74c3c") # Considerar usar colores del tema
            self.app.tree_completadas.tag_configure("completada", foreground="#27ae60") # Considerar usar colores del tema
            
            # Actualizar contadores en la barra de estado
            self.app.update_status(f"Pendientes: {len(self.pending_tasks)}, Completadas: {len(self.completed_tasks)}")
            
            return True
        except Exception as e:
            error_msg = f"Error al actualizar árboles: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de UI", error_msg)
            return False
    
    def add_task(self):
        """Añade una nueva tarea a la base de datos."""
        try:
            # Validar los campos
            if not self.app.validate_fields():
                return False
                
            cedula = self.app.cédula.get()
            
            # Verificar si la cédula ya existe
            if self.task_dao.check_cedula_exists(cedula):
                messagebox.showerror("Error de Duplicado", "Ya existe un estudiante con esa cédula")
                return False
                
            # Crear nueva tarea
            task = Task(
                cedula=cedula,
                nombre=self.app.nombre.get(),
                apellido=self.app.apellido.get(),
                curso=self.app.curso_grado.get(),
                turno=self.app.turno.get(),
                accion=self.app.accion_pendiente_entry.get()
            )
            
            # Insertar la tarea
            self.task_dao.insert_task(task)
            
            # Recargar tareas y actualizar la interfaz
            self.load_tasks() # Recargar todas las tareas
            self.update_trees()
            self.app.clear_fields()
            self.app.update_status(f"Tarea agregada: {task.nombre} {task.apellido}")
            messagebox.showinfo("Éxito", "Tarea agregada correctamente")
            
            return True
        except Exception as e:
            error_msg = f"Error al agregar tarea: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de Adición", error_msg)
            return False
    
    def update_task(self):
        """Actualiza una tarea existente."""
        try:
            # Validar los campos
            if not self.app.validate_fields():
                return False
            
            if self.app.current_index is None:
                messagebox.showerror("Error de Selección", "No hay tarea seleccionada para actualizar")
                return False
                
            if not self.app.editing_mode:
                # Esto no debería ocurrir si la UI está bien gestionada
                messagebox.showwarning("Modo incorrecto", "Debe estar en modo edición para actualizar.")
                return False
            
            # Buscar la tarea actual (usar DAO para asegurar datos frescos)
            task = self.task_dao.get_task_by_id(self.app.current_index)
            if not task:
                messagebox.showerror("Error", f"No se encontró la tarea con ID {self.app.current_index} para actualizar.")
                return False
            
            # Verificar si la cédula ya existe (pero no es la misma tarea)
            cedula = self.app.cédula.get()
            if cedula != task.cedula and self.task_dao.check_cedula_exists(cedula, task.id):
                messagebox.showerror("Error de Duplicado", "Ya existe otro estudiante con esa cédula")
                return False
                
            # Actualizar los datos del objeto task
            task.cedula = cedula
            task.nombre = self.app.nombre.get()
            task.apellido = self.app.apellido.get()
            task.curso = self.app.curso_grado.get()
            task.turno = self.app.turno.get()
            task.accion = self.app.accion_pendiente_entry.get()
            
            # Actualizar la tarea en la BD
            self.task_dao.update_task(task)
            
            # Recargar tareas y actualizar la interfaz
            self.load_tasks() # Recargar todas las tareas
            self.update_trees()
            self.app.clear_fields()
            self.app.toggle_edit_mode(False)
            self.app.update_status(f"Tarea actualizada: {task.nombre} {task.apellido}")
            messagebox.showinfo("Éxito", "Tarea actualizada correctamente")
            
            return True
        except Exception as e:
            error_msg = f"Error al actualizar tarea: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de Actualización", error_msg)
            return False
    
    def toggle_task_status(self, new_status):
        """Cambia el estado de una tarea entre pendiente y completada."""
        try:
            # Selecciona el tree correcto según la acción
            if new_status == "completada":
                selected_tree = self.app.tree_pendientes
                status_msg_user = "completada"
            else:
                selected_tree = self.app.tree_completadas
                status_msg_user = "pendiente"
            
            selected_item = selected_tree.selection()
            
            if not selected_item:
                messagebox.showwarning("Advertencia", "Seleccione un registro primero para cambiar su estado.")
                return False
                
            # Confirmación
            confirmacion = messagebox.askyesno(
                "Confirmar Cambio de Estado", 
                f"¿Está seguro que desea marcar esta tarea como {status_msg_user}?"
            )
            if not confirmacion:
                return False
                
            item_values = selected_tree.item(selected_item)['values']
            task_id = item_values[0]
            
            # Obtener la tarea
            task = self.task_dao.get_task_by_id(task_id)
            if not task:
                messagebox.showerror("Error", f"No se encontró la tarea con ID {task_id} para cambiar estado.")
                return False
                
            # Actualizar estado
            if new_status == "completada":
                task.mark_as_completed()
            else:
                task.mark_as_pending()
                
            # Guardar cambios
            self.task_dao.update_task(task)
            
            # Recargar y actualizar interfaz
            self.load_tasks()
            self.update_trees()
            self.app.update_status(f"Tarea marcada como {status_msg_user} correctamente")
            messagebox.showinfo("Estado Actualizado", f"Estado de la tarea actualizado a {new_status.capitalize()}.")
            
            return True
        except Exception as e:
            error_msg = f"Error al cambiar estado: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de Estado", error_msg)
            return False
    
    def delete_task(self):
        """Elimina una tarea seleccionada."""
        try:
            # Determinar pestaña activa para saber qué tree usar
            if self.app.current_tab == "pendientes":
                selected_tree = self.app.tree_pendientes
            else:
                selected_tree = self.app.tree_completadas
                
            selected_item = selected_tree.selection()
            
            if not selected_item:
                messagebox.showwarning("Advertencia", "Seleccione un registro primero para eliminar.")
                return False
                
            # Confirmación
            confirmacion = messagebox.askyesno(
                "Confirmar Eliminación", 
                "¿Está seguro que desea eliminar esta tarea? Esta acción no se puede deshacer."
            )
            if not confirmacion:
                return False
                
            item_values = selected_tree.item(selected_item)['values']
            task_id = item_values[0]
            student_name = f"{item_values[2]} {item_values[3]}"
            
            # Eliminar la tarea
            self.task_dao.delete_task(task_id)
            
            # Recargar y actualizar interfaz
            self.load_tasks()
            self.update_trees()
            self.app.clear_fields()
            self.app.toggle_edit_mode(False)
            self.app.update_status(f"Tarea para {student_name} eliminada.")
            messagebox.showinfo("Eliminado", f"Tarea para {student_name} eliminada correctamente.")
            
            return True
        except Exception as e:
            error_msg = f"Error al eliminar tarea: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de Eliminación", error_msg)
            return False
    
    def search_tasks(self, query=None):
        """Busca tareas y actualiza la vista. Si la query es None o vacía, carga todas las tareas."""
        try:
            if query is None: # Si se llama desde el botón de búsqueda
                query = self.app.search_entry.get().strip().lower()
            
            self.last_search_query = query # Guardar para posible re-búsqueda o refresh
            
            if not query: # Si la query está vacía, cargar todo
                self.load_tasks() # Carga todas las tareas
            else:
                self.load_tasks(query=query) # Carga tareas filtradas
            
            self.update_trees() # Actualiza los árboles con las tareas cargadas (filtradas o todas)
            
            if query:
                self.app.update_status(f"Mostrando {len(self.pending_tasks) + len(self.completed_tasks)} resultados para: '{query}'")
            else:
                self.app.update_status(f"Mostrando todas las tareas. Pendientes: {len(self.pending_tasks)}, Completadas: {len(self.completed_tasks)}")
            return True
        except Exception as e:
            error_msg = f"Error durante la búsqueda: {e}"
            self.app.update_status(error_msg)
            messagebox.showerror("Error de Búsqueda", error_msg)
            # En caso de error de búsqueda, intentar cargar todas las tareas como fallback
            self.load_tasks()
            self.update_trees()
            return False
    
    def clear_search(self):
        """Limpia el campo de búsqueda y muestra todos los registros."""
        self.last_search_query = ""
        self.app.search_entry.delete(0, tk.END)
        self.update_trees()
        self.app.update_status("Búsqueda limpiada. Mostrando todos los registros.")
        return True
        
    def export_tasks_to_csv(self):
        """Exporta las tareas a un archivo CSV."""
        try:
            # Preguntar dónde guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar como CSV"
            )
            
            if not filename:
                return False  # Usuario canceló
                
            # Cargar todas las tareas
            tasks = self.task_dao.get_all_tasks()
            
            # Exportar a CSV
            if Util.export_to_csv(tasks, filename):
                self.app.update_status(f"Datos exportados correctamente a {filename}")
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a {filename}")
                return True
            else:
                raise Exception("Error al exportar datos")
                
        except Exception as e:
            self.app.update_status(f"Error al exportar: {e}")
            messagebox.showerror("Error", f"Error al exportar datos: {e}")
            return False
            
    def generate_and_show_report(self):
        """Genera y muestra un informe de tareas."""
        try:
            tasks = self.task_dao.get_all_tasks()
            report = Util.generate_report(tasks)
            
            # Crear ventana para mostrar el informe
            report_window = tk.Toplevel(self.app.root)
            report_window.title("Informe de Tareas")
            report_window.geometry("500x400")
            
            # Agregar contenido
            ttk.Label(report_window, text="INFORME DE TAREAS", 
                     font=("Segoe UI", 16, "bold")).pack(pady=10)
            
            frame = ttk.Frame(report_window)
            frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Datos generales
            ttk.Label(frame, text=f"Total de tareas: {report['total']}", 
                     font=("Segoe UI", 12)).pack(anchor="w", pady=5)
            ttk.Label(frame, text=f"Tareas pendientes: {report['pendientes']} ({int(report['pendientes']*100/report['total'] if report['total'] else 0)}%)", 
                     font=("Segoe UI", 12)).pack(anchor="w", pady=5)
            ttk.Label(frame, text=f"Tareas completadas: {report['completadas']} ({int(report['completadas']*100/report['total'] if report['total'] else 0)}%)", 
                     font=("Segoe UI", 12)).pack(anchor="w", pady=5)
            
            # Divider
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
            
            # Distribución por curso
            ttk.Label(frame, text="Distribución por curso:", 
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
            
            for curso, cantidad in report["por_curso"].items():
                ttk.Label(frame, text=f"- {curso}: {cantidad} tareas", 
                         font=("Segoe UI", 10)).pack(anchor="w", padx=20)
            
            # Divider
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
            
            # Distribución por turno
            ttk.Label(frame, text="Distribución por turno:", 
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
            
            for turno, cantidad in report["por_turno"].items():
                ttk.Label(frame, text=f"- {turno}: {cantidad} tareas", 
                         font=("Segoe UI", 10)).pack(anchor="w", padx=20)
            
            # Botón para cerrar
            ttk.Button(report_window, text="Cerrar", command=report_window.destroy).pack(pady=10)
            
            return True
        except Exception as e:
            self.app.update_status(f"Error al generar informe: {e}")
            messagebox.showerror("Error", f"Error al generar informe: {e}")
            return False
            
    def toggle_auto_refresh(self, interval=30):
        """Activa o desactiva la actualización automática."""
        if self.auto_refresh_enabled:
            self.auto_refresh_enabled = False
            if self.auto_refresh_thread and self.auto_refresh_thread.is_alive():
                # No podemos detener directamente un thread, pero la bandera
                # hará que salga del bucle
                self.app.update_status("Actualización automática desactivada")
                return False
        else:
            self.auto_refresh_enabled = True
            self.auto_refresh_thread = threading.Thread(
                target=self._auto_refresh_worker,
                args=(interval,),
                daemon=True
            )
            self.auto_refresh_thread.start()
            self.app.update_status(f"Actualización automática activada (cada {interval} segundos)")
            return True
            
    def _auto_refresh_worker(self, interval):
        """Método worker para el thread de actualización automática."""
        while self.auto_refresh_enabled:
            time.sleep(interval)
            if not self.auto_refresh_enabled:
                break
                
            # Actualizar en el thread principal
            if self.app.root and self.app.root.winfo_exists():
                self.app.root.after(0, self._safe_update)
    
    def _safe_update(self):
        """Realiza una actualización segura para llamarse desde el thread principal."""
        try:
            if self.last_search_query:
                # Si hay una búsqueda activa, actualizarla
                self.search_tasks(self.last_search_query)
            else:
                # Si no, actualizar normalmente
                self.update_trees()
        except Exception as e:
            print(f"Error en actualización automática: {e}")
