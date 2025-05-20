"""
DAO (Data Access Object) para la gestión de tareas en SQLite.
Implementa el patrón DAO para encapsular toda la lógica de acceso a datos.
"""

import sqlite3
from datetime import datetime
import os
import csv
from models.task import Task

class TaskDAO:
    """Clase que maneja todas las operaciones de acceso a datos para las tareas."""
    
    def __init__(self, db_name="database.db"):
        """Inicializa el DAO con la conexión a la base de datos."""
        self.db_name = db_name
        self._ensure_db_path_exists() # Asegurar que el directorio de la BD exista
        self.setup_database()
        
    def _ensure_db_path_exists(self):
        """Asegura que el directorio para la base de datos exista."""
        db_dir = os.path.dirname(self.db_name)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
            except OSError as e:
                # Podría ser un problema de permisos o que la ruta no es válida
                raise Exception(f"No se pudo crear el directorio para la base de datos '{db_dir}': {e}")

    def _get_connection(self):
        """Retorna una nueva conexión a la base de datos."""
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            raise Exception(f"Error al conectar con la base de datos '{self.db_name}': {e}")

    def setup_database(self):
        """Configura la base de datos y crea la tabla si no existe."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tareas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cedula TEXT NOT NULL,
                        nombre TEXT NOT NULL,
                        apellido TEXT NOT NULL,
                        curso TEXT NOT NULL,
                        turno TEXT NOT NULL,
                        accion TEXT,
                        fecha_creacion TEXT NOT NULL,
                        fecha_completado TEXT,
                        status TEXT NOT NULL,
                        UNIQUE(cedula)  -- Añadir restricción de unicidad para cédula
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            # Envolver el error de SQLite en una excepción más genérica o específica de la app
            raise Exception(f"Error al configurar la tabla 'tareas': {e}")
    
    def migrate_from_csv(self, csv_file="alumnos_pendientes.csv"):
        """Migra datos desde CSV si existe el archivo y la BD está vacía."""
        if not os.path.exists(csv_file):
            print(f"Archivo CSV '{csv_file}' no encontrado. No se realizará la migración.")
            return False
        
        if self.has_data():
            print("La base de datos ya contiene datos. No se realizará la migración desde CSV.")
            return False
            
        try:
            with self._get_connection() as conn, open(csv_file, newline="", encoding="utf-8") as f:
                cursor = conn.cursor()
                reader = csv.DictReader(f)
                tasks_to_insert = []
                for row in reader:
                    # Validar datos mínimos o usar valores por defecto más robustos
                    task_data = (
                        row.get("cedula") or f"cedula_faltante_{datetime.now().timestamp()}", # Evitar duplicados si falta cédula
                        row.get("nombre") or "Nombre no especificado",
                        row.get("apellido") or "Apellido no especificado",
                        row.get("curso") or "Curso no especificado",
                        row.get("turno") or "Turno no especificado",
                        row.get("accion") or "Acción pendiente no especificada",
                        row.get("fecha_creacion") or datetime.now().strftime("%d/%m/%Y %H:%M"),
                        row.get("fecha_completado") or "",
                        row.get("status") or "pendiente"
                    )
                    tasks_to_insert.append(task_data)
                
                if tasks_to_insert:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO tareas 
                        (cedula, nombre, apellido, curso, turno, accion, 
                         fecha_creacion, fecha_completado, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', tasks_to_insert) # Usar executemany para inserción masiva
                    conn.commit()
                    print(f"Migración desde '{csv_file}' completada. {len(tasks_to_insert)} tareas procesadas.")
                    return True
                else:
                    print(f"No se encontraron datos válidos en '{csv_file}' para migrar.")
                    return False
        except sqlite3.Error as e:
            raise Exception(f"Error de base de datos durante la migración desde CSV: {e}")
        except Exception as e:
            raise Exception(f"Error general durante la migración desde CSV: {e}")
                
    def has_data(self):
        """Verifica si la base de datos ya tiene registros."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tareas")
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            # Considerar logging del error aquí
            print(f"Error al verificar si hay datos: {e}")
            return False # Asumir que no hay datos si hay un error
    
    def insert_task(self, task):
        """Inserta una nueva tarea en la base de datos."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tareas 
                    (cedula, nombre, apellido, curso, turno, accion, 
                     fecha_creacion, fecha_completado, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.cedula,
                    task.nombre,
                    task.apellido,
                    task.curso,
                    task.turno,
                    task.accion,
                    task.fecha_creacion,
                    task.fecha_completado,
                    task.status
                ))
                task.id = cursor.lastrowid
                conn.commit()
                return task
        except sqlite3.IntegrityError as e: # Capturar error de unicidad de cédula
            if "UNIQUE constraint failed: tareas.cedula" in str(e):
                raise Exception(f"Error: La cédula '{task.cedula}' ya existe en la base de datos.")
            else:
                raise Exception(f"Error de integridad al insertar tarea: {e}")
        except sqlite3.Error as e:
            raise Exception(f"Error de base de datos al insertar tarea: {e}")
    
    def update_task(self, task):
        """Actualiza una tarea existente en la base de datos."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tareas SET 
                    cedula = ?, nombre = ?, apellido = ?, curso = ?, 
                    turno = ?, accion = ?, fecha_completado = ?, status = ?
                    WHERE id = ?
                ''', (
                    task.cedula,
                    task.nombre,
                    task.apellido,
                    task.curso,
                    task.turno,
                    task.accion,
                    task.fecha_completado,
                    task.status,
                    task.id
                ))
                conn.commit()
                if cursor.rowcount == 0:
                    # Esto podría significar que el ID no existe, o que los datos eran iguales
                    # Para ser más precisos, se podría verificar si el ID existe antes de actualizar
                    print(f"Advertencia: No se actualizó ninguna fila para la tarea con ID {task.id}. Puede que no exista o los datos sean idénticos.")
                    # Devolver la tarea original si no hubo cambios o no se encontró
                    # Opcionalmente, se podría lanzar una excepción si se espera que siempre exista
                return task # Devolver la tarea actualizada (o la original si no hubo cambios)
        except sqlite3.IntegrityError as e: # Capturar error de unicidad de cédula
            if "UNIQUE constraint failed: tareas.cedula" in str(e):
                raise Exception(f"Error: La cédula '{task.cedula}' ya pertenece a otro registro.")
            else:
                raise Exception(f"Error de integridad al actualizar tarea: {e}")
        except sqlite3.Error as e:
            raise Exception(f"Error de base de datos al actualizar tarea: {e}")
    
    def delete_task(self, task_id):
        """Elimina una tarea por su ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tareas WHERE id = ?", (task_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    # Si no se eliminó ninguna fila, es porque el ID no existía
                    raise Exception(f"No se encontró la tarea con ID {task_id} para eliminar.")
                return True
        except sqlite3.Error as e:
            raise Exception(f"Error de base de datos al eliminar tarea: {e}")
    
    def _map_row_to_task(self, row):
        """Mapea una fila de la base de datos a un objeto Task."""
        if not row: return None
        return Task(
            id=row[0],
            cedula=row[1],
            nombre=row[2],
            apellido=row[3],
            curso=row[4],
            turno=row[5],
            accion=row[6],
            fecha_creacion=row[7],
            fecha_completado=row[8],
            status=row[9]
        )

    def get_all_tasks(self):
        """Obtiene todas las tareas de la base de datos."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, cedula, nombre, apellido, curso, turno, accion, 
                    fecha_creacion, fecha_completado, status FROM tareas ORDER BY id DESC
                ''') # Ordenar por ID descendente para mostrar las más recientes primero
                return [self._map_row_to_task(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener todas las tareas: {e}")
    
    def get_task_by_id(self, task_id):
        """Obtiene una tarea por su ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, cedula, nombre, apellido, curso, turno, accion, 
                    fecha_creacion, fecha_completado, status FROM tareas
                    WHERE id = ?
                ''', (task_id,))
                return self._map_row_to_task(cursor.fetchone())
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener tarea por ID '{task_id}': {e}")
    
    def check_cedula_exists(self, cedula, exclude_id=None):
        """Verifica si ya existe una cédula en la base de datos, opcionalmente excluyendo un ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT COUNT(*) FROM tareas WHERE cedula = ?"
                params = [cedula]
                if exclude_id is not None:
                    query += " AND id != ?"
                    params.append(exclude_id)
                
                cursor.execute(query, tuple(params))
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            # En un entorno de producción, registrar este error
            print(f"Error al verificar existencia de cédula '{cedula}': {e}")
            return False # Asumir que no existe si hay error para evitar bloqueos, aunque podría ser riesgoso
    
    def search_tasks(self, query):
        """Busca tareas por texto en múltiples columnas."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                search_term = f'%{query.lower()}%' # Convertir query a minúsculas para búsqueda case-insensitive
                cursor.execute('''
                    SELECT id, cedula, nombre, apellido, curso, turno, accion, 
                    fecha_creacion, fecha_completado, status FROM tareas
                    WHERE LOWER(cedula) LIKE ? OR LOWER(nombre) LIKE ? OR LOWER(apellido) LIKE ? OR 
                    LOWER(curso) LIKE ? OR LOWER(turno) LIKE ? OR LOWER(accion) LIKE ?
                    ORDER BY id DESC
                ''', (search_term, search_term, search_term, 
                     search_term, search_term, search_term))
                return [self._map_row_to_task(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise Exception(f"Error en búsqueda de tareas con query '{query}': {e}")
