# handlers/command_handlers.py
# ============================================================================
# RESPONSABILIDAD: Procesar comandos (/start, /help, /cancel)
# ============================================================================

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import MENSAJE_BIENVENIDA, TIPOS_MUFA, MENSAJE_TIPO_MUFA
from services.session_service import SessionService
from utils.formatters import FormateadorMensajes

logger = logging.getLogger(__name__)

# Inyección de dependencias
session_service: SessionService = None
formateador = FormateadorMensajes()


def set_session_service(svc: SessionService) -> None:
    """Asigna el servicio de sesión"""
    global session_service
    session_service = svc
    logger.info("✅ session_service asignado a command_handlers")


# ============================================================================
# COMANDOS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja el comando /start.
    
    Inicia nuevo flujo de registro:
    1. Crea sesión nueva
    2. Muestra bienvenida
    3. Presenta botones: Mufa Existente / Mufa Proyectada
    """
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    logger.info(f"👤 Usuario {user_id} ({user_name}) ejecutó /start")
    
    # Crear nueva sesión
    if not session_service.crear_sesion(user_id):
        logger.warning(f"⚠️ Usuario {user_id} ya tiene sesión abierta")
        await update.message.reply_text(
            "⚠️ Ya tienes un registro en progreso.\n"
            "Presiona /start si deseas empezar uno nuevo."
        )
        return
    
    # Enviar bienvenida
    await update.message.reply_text(MENSAJE_BIENVENIDA)
    
    # Mostrar opciones de tipo MUFA
    teclado = formateador.crear_teclado_opciones(TIPOS_MUFA, "tipo_mufa")
    await update.message.reply_text(
        MENSAJE_TIPO_MUFA,
        reply_markup=teclado
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /help"""
    user_id = update.effective_user.id
    
    logger.info(f"👤 Usuario {user_id} ejecutó /help")
    
    ayuda = """
ℹ️ AYUDA - Bot de Registro MUFA

**Comandos disponibles:**
/start - Iniciar nuevo registro
/help - Mostrar esta ayuda
/cancel - Cancelar registro actual

**Cómo usar el bot:**
1. Ejecuta /start
2. Selecciona si es Mufa Existente o Proyectada
3. Completa todos los campos solicitados
4. Revisa el resumen y presiona "Guardar"

**Durante el registro:**
- Presiona botones para seleccionar opciones
- Escribe texto para ingresar datos
- Presiona "↩️ Retroceder" para volver atrás
- Presiona "❌ Cancelar" para cancelar el registro
"""
    
    await update.message.reply_text(ayuda)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /cancel"""
    user_id = update.effective_user.id
    
    logger.info(f"👤 Usuario {user_id} ejecutó /cancel")
    
    if not session_service.sesion_existe(user_id):
        await update.message.reply_text(
            "❌ No tienes un registro en progreso."
        )
        return
    
    session_service.limpiar_sesion(user_id)
    
    await update.message.reply_text(
        "❌ Registro cancelado.\n"
        "Usa /start para iniciar uno nuevo."
    )