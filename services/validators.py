# services/validators.py
# ============================================================================
# RESPONSABILIDAD: Validar datos que ingresa el usuario
# ============================================================================

import re
from config import PATRON_MUFA
import logging

logger = logging.getLogger(__name__)


class ValidadorMUFA:
    """Valida datos relacionados con MUFAs"""
    
    @staticmethod
    def validar_rotulo(rotulo: str) -> tuple:
        """
        Valida formato de rótulo MUFA.
        
        Reglas:
        - No puede estar vacío
        - Máximo 50 caracteres
        - Solo letras, números y guiones
        - Patrón: WN-XXXXX
        
        Args:
            rotulo (str): Rótulo a validar
            
        Returns:
            tuple: (es_válido, mensaje)
            
        Ejemplos:
            >>> ValidadorMUFA.validar_rotulo("WN-FALLBACK-1")
            (True, "✅ Válido")
            
            >>> ValidadorMUFA.validar_rotulo("INVALIDO!")
            (False, "❌ Solo letras, números y guiones permitidos")
        """
        
        # Vacío
        if not rotulo or len(rotulo.strip()) == 0:
            return False, "❌ El rótulo no puede estar vacío"
        
        # Demasiado largo
        if len(rotulo) > 50:
            return False, "❌ Rótulo demasiado largo (máx 50 caracteres)"
        
        # Formato: solo alfanuméricos y guiones
        if not re.match(PATRON_MUFA, rotulo.upper()):
            return False, "❌ Solo letras, números y guiones permitidos"
        
        return True, "✅ Válido"
    
    @staticmethod
    def validar_campo_texto(campo: str, max_largo: int = 100) -> tuple:
        """
        Valida que un campo de texto sea válido.
        
        Args:
            campo (str): Texto a validar
            max_largo (int): Máximo de caracteres permitidos
            
        Returns:
            tuple: (es_válido, mensaje)
        """
        
        if not campo or len(campo.strip()) == 0:
            return False, "❌ El campo no puede estar vacío"
        
        if len(campo) > max_largo:
            return False, f"❌ Campo demasiado largo (máx {max_largo} caracteres)"
        
        return True, "✅ Válido"