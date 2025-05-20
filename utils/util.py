"""
Este archivo contiene una clase con funciones de utilidad para la aplicación.
Proporciona funcionalidades reutilizables como validación, formateo de datos, etc.
"""

import re
from datetime import datetime

class Util:
    """Clase que proporciona funciones de utilidad para la aplicación."""
    
    @staticmethod
    def validate_cedula(cedula):
        """Valida que una cédula sea numérica y tenga una longitud apropiada (6-10 dígitos)."""
        if not cedula:
            return False, "La cédula no puede estar vacía."
        if not cedula.isdigit():
            return False, "La cédula debe contener solo números."
        if not (6 <= len(cedula) <= 10):
            return False, f"La cédula debe tener entre 6 y 10 dígitos (actual: {len(cedula)})."
        return True, ""
    
    @staticmethod
    def format_date(date_str):
        """Formatea una fecha si es necesario. Devuelve string vacío si la entrada es vacía."""
        if not date_str or not str(date_str).strip():
            return "" # Devuelve vacío si la entrada es None, vacía o solo espacios
        
        # Si ya tiene el formato deseado, devolverlo tal cual
        if isinstance(date_str, str) and re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', date_str):
            return date_str
        
        # Intentar convertir varios formatos de fecha
        # Formatos comunes a intentar (del más específico al más general)
        common_formats = [
            "%Y-%m-%d %H:%M:%S.%f", # ISO con microsegundos
            "%Y-%m-%d %H:%M:%S",    # ISO sin microsegundos
            "%Y-%m-%dT%H:%M:%S",   # ISO con T
            "%Y-%m-%d",             # Solo fecha ISO
            "%d/%m/%Y %H:%M",      # Formato deseado (por si acaso)
            "%d/%m/%Y"             # Solo fecha con barras
        ]
        
        parsed_date = None
        if isinstance(date_str, datetime): # Si ya es un objeto datetime
            parsed_date = date_str
        elif isinstance(date_str, str):
            for fmt in common_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break # Salir del bucle si se parsea correctamente
                except ValueError:
                    continue # Probar el siguiente formato
        
        if parsed_date:
            return parsed_date.strftime("%d/%m/%Y %H:%M")
        else:
            # Si no se pudo parsear y no es el formato deseado, registrar o advertir
            # print(f"Advertencia: No se pudo formatear la fecha '{date_str}'. Se usará la fecha actual.")
            # Considerar si devolver la fecha actual es el comportamiento deseado o un string vacío/error
            return datetime.now().strftime("%d/%m/%Y %H:%M") # Opcional: devolver fecha actual como fallback
    
    @staticmethod
    def validate_name(name, field_name="Nombre"):
        """Valida que un nombre/apellido no esté vacío y contenga caracteres válidos."""
        if not name or not name.strip():
            return False, f"{field_name} no puede estar vacío."
        
        # Permitir letras (incluyendo acentuadas y ñ), espacios, apóstrofes y guiones.
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\'\-]+$'
        if not re.match(pattern, name.strip()):
            return False, f"{field_name} contiene caracteres no válidos. Solo se permiten letras, espacios, apóstrofes y guiones."
        
        if len(name.strip()) < 2:
             return False, f"{field_name} debe tener al menos 2 caracteres."

        return True, ""
    
    @staticmethod
    def export_to_csv(tasks, filename):
        """Exporta una lista de tareas a un archivo CSV."""
        import csv # Mover import aquí para que solo se cargue si se usa la función
        
        if not tasks:
            print("No hay tareas para exportar.")
            return False, "No hay datos para exportar."

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile: # utf-8-sig para mejor compatibilidad con Excel
                fieldnames = ['id', 'cedula', 'nombre', 'apellido', 'curso', 
                             'turno', 'accion', 'fecha_creacion', 'fecha_completado', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore') # Ignorar campos extra en el dict
                
                writer.writeheader()
                for task in tasks:
                    # Asegurarse de que to_dict() devuelve todos los fieldnames esperados
                    task_dict = task.to_dict()
                    # Formatear fechas para el CSV si es necesario, aunque to_dict debería manejarlo
                    task_dict['fecha_creacion'] = Util.format_date(task_dict.get('fecha_creacion'))
                    task_dict['fecha_completado'] = Util.format_date(task_dict.get('fecha_completado'))
                    writer.writerow(task_dict)
                    
            return True, f"Datos exportados correctamente a {filename}"
        except IOError as e: # Más específico para errores de archivo
            error_msg = f"Error de E/S al exportar a CSV '{filename}': {e}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado al exportar a CSV: {e}"
            print(error_msg)
            return False, error_msg
    
    @staticmethod
    def generate_report(tasks):
        """Genera un informe resumido basado en la lista de tareas."""
        if not tasks:
            return {
                "total": 0,
                "pendientes": 0,
                "completadas": 0,
                "por_curso": {},
                "por_turno": {},
                "message": "No hay tareas para generar el informe."
            }

        report = {
            "total": len(tasks),
            "pendientes": 0,
            "completadas": 0,
            "por_curso": {},
            "por_turno": {}
        }
        
        for task in tasks:
            if not isinstance(task, object) or not hasattr(task, 'status'): # Chequeo básico de validez del objeto task
                continue

            # Contar por estado
            if task.status == "pendiente":
                report["pendientes"] += 1
            elif task.status == "completada": # Ser explícito con el estado
                report["completadas"] += 1
                
            # Contar por curso
            curso = getattr(task, 'curso', 'Desconocido') # Usar getattr para seguridad
            report["por_curso"][curso] = report["por_curso"].get(curso, 0) + 1
            
            # Contar por turno
            turno = getattr(task, 'turno', 'Desconocido') # Usar getattr para seguridad
            report["por_turno"][turno] = report["por_turno"].get(turno, 0) + 1
        
        return report
