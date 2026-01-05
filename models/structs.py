# models/structs.py
# ============================================================================
# ESTRUCTURAS Y ENUMS
# ============================================================================

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class TipoMUFA(str, Enum):
    """Tipo de MUFA: Existente o Proyectada"""
    EXISTENTE = "Mufa existente"
    PROYECTADA = "Mufa proyectada"


class TipoTrabajo(str, Enum):
    """Tipo de trabajo: Avería o Implementación"""
    AVERIA = "Avería"
    IMPLEMENTACION = "Implementación"


class EstadoMUFA(str, Enum):
    """Estado de una MUFA"""
    BUEN_ESTADO = "BUEN ESTADO"
    SATURADA = "SATURADA"
    CRITICA = "CRÍTICA"


class PasoFlujo(str, Enum):
    """Pasos del flujo de registro"""
    TIPO_MUFA = "tipo_mufa"
    ROTULO_MUFA = "rotulo_mufa"
    PATCH_PANEL = "patch_panel"
    TIPO_TRABAJO = "tipo_trabajo"
    PROYECTO_EDIFICIO = "proyecto_edificio"
    SUPERVISOR = "supervisor"
    NODO = "nodo"
    ESTADO = "estado"
    CONFIRMACION = "confirmacion"
    COMPLETADO = "completado"


@dataclass
class RegistroMUFA:
    """Registro completo de intervención MUFA"""
    user_id: int
    tipo_mufa: str  # "Mufa existente" o "Mufa proyectada"
    rotulo_mufa: str
    patch_panel: str
    tipo_trabajo: str  # "Avería" o "Implementación"
    proyecto_edificio: Optional[str] = None
    supervisor: Optional[str] = None
    nodo: Optional[str] = None
    estado: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def generar_plantilla(self) -> str:
        """
        Genera la plantilla formateada lista para copiar/pegar.
        
        Returns:
            str: Plantilla formateada
        """
        # Determinar saludo según hora
        hora = self.timestamp.hour
        if 6 <= hora < 12:
            saludo = "Buenos días"
        elif 12 <= hora < 18:
            saludo = "Buenas tardes"
        else:
            saludo = "Buenas noches"
        
        plantilla = f"""{saludo}, permiso para realizar trabajos.

MUFA: {self.rotulo_mufa}
NODO: {self.nodo}
PATCH PANEL: {self.patch_panel}
PROYECTO/EDIFICIO: {self.proyecto_edificio or 'N/A'}
ESTADO: {self.estado or 'Mufa nueva' if self.tipo_mufa == TipoMUFA.PROYECTADA.value else self.estado}
SUPERVISOR A CARGO: {self.supervisor}
TIPO DE TRABAJO: {self.tipo_trabajo}"""
        
        return plantilla
    
    def a_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "tipo_mufa": self.tipo_mufa,
            "rotulo_mufa": self.rotulo_mufa,
            "patch_panel": self.patch_panel,
            "tipo_trabajo": self.tipo_trabajo,
            "proyecto_edificio": self.proyecto_edificio,
            "supervisor": self.supervisor,
            "nodo": self.nodo,
            "estado": self.estado,
            "timestamp": self.timestamp.isoformat()
        }