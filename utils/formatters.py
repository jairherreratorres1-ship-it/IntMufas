# utils/formatters.py
# ============================================================================
# RESPONSABILIDAD: Crear teclados y formatear mensajes para Telegram
# ============================================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict


class FormateadorMensajes:
    """Crea estructuras de mensajes para Telegram"""
    
    @staticmethod
    def crear_teclado_opciones(opciones: List[str], prefijo: str) -> InlineKeyboardMarkup:
        """
        Crea un teclado inline con una opción por botón.
        
        Args:
            opciones (list): Lista de opciones a mostrar
            prefijo (str): Prefijo del callback
            
        Returns:
            InlineKeyboardMarkup: Teclado con botones
        """
        keyboard = []
        
        for opcion in opciones:
            boton = InlineKeyboardButton(
                text=opcion,
                callback_data=f"{prefijo}:{opcion}"
            )
            keyboard.append([boton])
        
        # Agregar botón retroceso
        boton_back = InlineKeyboardButton(
            text="↩️ Retroceder",
            callback_data="back"
        )
        keyboard.append([boton_back])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def crear_teclado_confirmacion() -> InlineKeyboardMarkup:
        """Crea teclado de confirmación"""
        keyboard = [
            [InlineKeyboardButton("✅ Guardar", callback_data="guardar")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")],
            [InlineKeyboardButton("↩️ Retroceder", callback_data="back")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def formatear_confirmacion(datos: Dict[str, str]) -> str:
        """Formatea un mensaje de confirmación"""
        lineas = ["📋 RESUMEN DE REGISTRO 📋\n"]
        
        campos_visibles = [
            ("tipo_mufa", "Tipo MUFA"),
            ("rotulo_mufa", "MUFA"),
            ("patch_panel", "Patch Panel"),
            ("tipo_trabajo", "Tipo de Trabajo"),
            ("proyecto_edificio", "Proyecto/Edificio"),
            ("supervisor", "Supervisor"),
            ("nodo", "Nodo"),
            ("estado", "Estado"),
        ]
        
        for clave, label in campos_visibles:
            valor = datos.get(clave)
            if valor:
                lineas.append(f"• {label}: {valor}")
        
        lineas.append("\n¿Deseas guardar este registro?")
        
        return "\n".join(lineas)