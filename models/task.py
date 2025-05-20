"""
Modelo para representar una tarea en el sistema.
Parte del patrón de diseño DAO (Data Access Object).
"""
from datetime import datetime

class Task:
    """Clase que representa una tarea individual en el sistema."""
    
    def __init__(self, id=None, cedula="", nombre="", apellido="", curso="", 
                 turno="", accion="", fecha_creacion=None, fecha_completado=None, 
                 status="pendiente"):
        self.id = id
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.curso = curso
        self.turno = turno
        self.accion = accion
        
        # Si no se proporciona una fecha de creación, usar la fecha actual
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%d/%m/%Y %H:%M")
        self.fecha_completado = fecha_completado or ""
        self.status = status
    
    def to_dict(self):
        """Convierte la tarea a un diccionario."""
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'curso': self.curso,
            'turno': self.turno,
            'accion': self.accion,
            'fecha_creacion': self.fecha_creacion,
            'fecha_completado': self.fecha_completado,
            'status': self.status
        }
    
    def __str__(self):
        """Representación en texto de la tarea."""
        return f"{self.nombre} {self.apellido} - {self.accion} ({self.status})"
    
    def mark_as_completed(self):
        """Marca la tarea como completada."""
        self.status = "completada"
        self.fecha_completado = datetime.now().strftime("%d/%m/%Y %H:%M")
        
    def mark_as_pending(self):
        """Marca la tarea como pendiente."""
        self.status = "pendiente"
        self.fecha_completado = ""
