
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TELEGRAM_TOKEN, CATALOG_URL

# Importar servicios
from services.catalog_service import CatalogoService
from services.session_service import SessionService

# Importar handlers
from handlers import command_handlers, message_handlers, callback_handlers

# ============================================================================
# CONFIGURAR LOGGING
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """
    Función principal que orquesta la ejecución del bot.
    
    Pasos:
    1. Cargar catálogos desde Google Sheets
    2. Crear servicios
    3. Inicializar handlers (inyección de dependencias)
    4. Crear aplicación Telegram
    5. Registrar handlers
    6. Iniciar bot en polling
    """
    
    logger.info("=" * 40)
    logger.info("🤖 INICIANDO BOT MUFA")
    logger.info("=" * 40)
    
    # ========================================================================
    # PASO 1: Cargar catálogos
    # ========================================================================
    
    logger.info("📥 PASO 1: Cargando catálogos desde Google Sheets...")
    
    try:
        catalogo_service = CatalogoService(CATALOG_URL)
        logger.info("✅ Catálogos cargados exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al cargar catálogos: {e}")
        logger.error("⚠️ El bot no puede iniciar sin catálogos")
        return
    
    # ========================================================================
    # PASO 2: Crear servicios
    # ========================================================================
    
    logger.info("🔧 PASO 2: Creando servicios... ")
    
    session_service = SessionService()
    
    logger.info("✅ Servicios creados")
    
    # ========================================================================
    # PASO 3: Inicializar handlers (inyección de dependencias)
    # ========================================================================
    
    logger.info("📨 PASO 3: Inicializando handlers...")
    
    # Command handlers - solo necesita session_service
    command_handlers.set_session_service(session_service)
    
    # Message handlers - necesita catalogo_service y session_service
    message_handlers.set_dependencies(catalogo_service, session_service)
    
    # Callback handlers - necesita catalogo_service y session_service
    callback_handlers.set_dependencies(catalogo_service, session_service)
    
    logger.info("✅ Handlers inicializados")
    
    # ========================================================================
    # PASO 4: Crear aplicación Telegram
    # ========================================================================
    
    logger.info("🔌 PASO 4: Creando aplicación Telegram...")
    
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        logger.info("✅ Aplicación Telegram creada")
    except Exception as e:
        logger.error(f"❌ Error al crear aplicación: {e}")
        logger.error("⚠️ Verifica que TELEGRAM_TOKEN sea válido")
        return
    
    # ========================================================================
    # PASO 5: Registrar handlers
    # ========================================================================
    
    logger.info("📋 PASO 5: Registrando handlers...")
    
    # ---- COMMAND HANDLERS ----
    app.add_handler(CommandHandler("start", command_handlers.start))
    logger.info("  ✅ /start registrado")
    
    app.add_handler(CommandHandler("help", command_handlers.help_command))
    logger.info("  ✅ /help registrado")
    
    app.add_handler(CommandHandler("cancel", command_handlers.cancel_command))
    logger.info("  ✅ /cancel registrado")
    
    # ---- MESSAGE HANDLERS ----
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handlers.handle_text_message
        )
    )
    logger.info("  ✅ Handler de mensajes de texto registrado")
    
    # ---- CALLBACK HANDLERS ----
    app.add_handler(CallbackQueryHandler(callback_handlers.handle_callback_query))
    logger.info("  ✅ Handler de callbacks registrado")
    
    logger.info("✅ Todos los handlers registrados")
    
    # ========================================================================
    # PASO 6: Ejecutar bot
    # ========================================================================
    
    logger.info("=" * 60)
    logger.info("🚀 BOT INICIADO - Escuchando mensajes")
    logger.info("=" * 60)
    logger.info("Presiona Ctrl+C para detener")
    
    # ⚠️ IMPORTANTE: No usar await aquí, run_polling() es síncrono
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)