# services/session_service.py
# ============================================================================
# RESPONSABILIDAD: Gestionar sesiones de usuario en memoria
# ============================================================================

import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class SessionService:
    """Gestiona sesiones de usuario en memoria"""
    
    def __init__(self):
        """Inicializa diccionario de sesiones"""
        self.sesiones: Dict[int, Dict[str, Any]] = {}
    
    def crear_sesion(self, user_id: int) -> bool:
        """
        Crea nueva sesión de usuario.
        
        Args:
            user_id (int): ID del usuario Telegram
            
        Returns:
            bool: True si se crea
        """
        if user_id in self.sesiones:
            logger.warning(f"⚠️ Usuario {user_id} ya tiene sesión abierta")
            return False
        
        # Nueva sesión: empieza en paso "tipo_mufa"
        self.sesiones[user_id] = {
            "paso_actual": "tipo_mufa",
            "datos": {
                "tipo_mufa": None,              # Mufa existente / Mufa proyectada
                "rotulo_mufa": None,           # Rótulo de MUFA
                "patch_panel": None,           # Patch panel
                "tipo_trabajo": None,          # Avería / Implementación
                "proyecto_edificio": None,     # Solo si es Implementación
                "supervisor": None,            # Supervisor
                "nodo": None,                  # Nodo
                "estado": None,                # Estado (solo si es Existente)
            }
        }
        
        logger.info(f"✅ Sesión creada para usuario {user_id}")
        return True
    
    def obtener_sesion(self, user_id: int) -> Optional[Dict]:
        """Obtiene sesión actual del usuario"""
        return self.sesiones.get(user_id)
    
    def obtener_paso_actual(self, user_id: int) -> Optional[str]:
        """Obtiene el paso actual del usuario"""
        sesion = self.sesiones.get(user_id)
        return sesion["paso_actual"] if sesion else None
    
    def guardar_dato(self, user_id: int, clave: str, valor: str) -> bool:
        """
        Guarda un dato en la sesión del usuario.
        
        Args:
            user_id (int): ID del usuario
            clave (str): Campo a guardar
            valor (str): Valor a guardar
            
        Returns:
            bool: True si se guarda
        """
        sesion = self.sesiones.get(user_id)
        
        if not sesion:
            #logger.error(f"❌ Usuario {user_id} no tiene sesión")
            return False
        
        if clave not in sesion["datos"]:
            #logger.error(f"❌ Campo '{clave}' no existe en sesión")
            return False
        
        sesion["datos"][clave] = valor
        #logger.debug(f"💾 Guardado {clave}={valor} para usuario {user_id}")
        return True
    
    def obtener_datos(self, user_id: int) -> Optional[Dict]:
        """Obtiene todos los datos temporales del usuario"""
        sesion = self.sesiones.get(user_id)
        return sesion["datos"] if sesion else None
    
    def avanzar_paso(self, user_id: int) -> bool:
        """
        Avanza el usuario al siguiente paso.
        
        Pasos: tipo_mufa → rotulo_mufa → patch_panel → tipo_trabajo → 
               proyecto_edificio → supervisor → nodo → estado → confirmacion
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            bool: True si avanza exitosamente
        """
        pasos_orden = [
            "tipo_mufa",
            "rotulo_mufa",
            "patch_panel",
            "tipo_trabajo",
            "proyecto_edificio",
            "supervisor",
            "nodo",
            "estado",
            "confirmacion"
        ]
        
        sesion = self.sesiones.get(user_id)
        if not sesion:
            logger.error(f"❌ Usuario {user_id} no tiene sesión")
            return False
        
        paso_actual = sesion["paso_actual"]
        
        if paso_actual not in pasos_orden:
            #logger.error(f"❌ Paso '{paso_actual}' no válido")
            return False
        
        idx_actual = pasos_orden.index(paso_actual)
        
        if idx_actual >= len(pasos_orden) - 1:
            #logger.warning(f"⚠️ Ya estamos en último paso")
            return False
        
        proximo_paso = pasos_orden[idx_actual + 1]
        sesion["paso_actual"] = proximo_paso
        
        #logger.info(f"➡️ Usuario {user_id} avanzó a paso: {proximo_paso}")
        return True
    
    def retroceder_paso(self, user_id: int) -> bool:
        """Retrocede el usuario al paso anterior"""
        pasos_orden = [
            "tipo_mufa",
            "rotulo_mufa",
            "patch_panel",
            "tipo_trabajo",
            "proyecto_edificio",
            "supervisor",
            "nodo",
            "estado",
            "confirmacion"
        ]
        
        sesion = self.sesiones.get(user_id)
        if not sesion:
            logger.error(f"❌ Usuario {user_id} no tiene sesión")
            return False
        
        paso_actual = sesion["paso_actual"]
        
        if paso_actual not in pasos_orden:
            logger.error(f"❌ Paso '{paso_actual}' no válido")
            return False
        
        idx_actual = pasos_orden.index(paso_actual)
        
        if idx_actual == 0:
            #logger.warning(f"⚠️ Ya estamos en primer paso")
            return False
        
        paso_anterior = pasos_orden[idx_actual - 1]
        sesion["paso_actual"] = paso_anterior
        
        #logger.info(f"⬅️ Usuario {user_id} retrocedió a paso: {paso_anterior}")
        return True
    
    def limpiar_sesion(self, user_id: int) -> bool:
        """Elimina la sesión del usuario"""
        if user_id not in self.sesiones:
            #logger.warning(f"⚠️ Usuario {user_id} no tiene sesión")
            return False
        
        del self.sesiones[user_id]
        #logger.info(f"🗑️ Sesión eliminada para usuario {user_id}")
        return True
    
    def sesion_existe(self, user_id: int) -> bool:
        """Verifica si usuario tiene sesión activa"""
        return user_id in self.sesiones