# handlers/message_handlers.py
# ============================================================================
# RESPONSABILIDAD: Procesar mensajes de texto del usuario
# ============================================================================

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    MENSAJE_ROTULO_MUFA,
    MENSAJE_PATCH_PANEL,
    MENSAJE_PROYECTO_EDIFICIO,
    MENSAJE_SUPERVISOR,
    MENSAJE_NODO,
)
from services.catalog_service import CatalogoService
from services.session_service import SessionService
from services.validators import ValidadorMUFA
from utils.formatters import FormateadorMensajes

logger = logging.getLogger(__name__)

# Inyección de dependencias
catalogo_service: CatalogoService = None
session_service: SessionService = None
validador = ValidadorMUFA()
formateador = FormateadorMensajes()


def set_dependencies(
    catalog_svc: CatalogoService,
    session_svc: SessionService
) -> None:
    """Asigna los servicios necesarios"""
    global catalogo_service, session_service
    catalogo_service = catalog_svc
    session_service = session_svc
    logger.info("✅ Dependencias asignadas a message_handlers")


# ============================================================================
# HANDLER PRINCIPAL
# ============================================================================

async def handle_text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Maneja mensajes de texto del usuario.
    
    Router que dirige según el paso actual.
    """
    user_id = update.effective_user.id
    texto = update.message.text.strip()
    
    #logger.debug(f"📝 Usuario {user_id} escribió: {texto}")
    
    # Obtener sesión
    if not session_service.sesion_existe(user_id):
        logger.warning(f"⚠️ Usuario {user_id} no tiene sesión")
        await update.message.reply_text(
            "❌ No tienes sesión activa. Usa /start para comenzar."
        )
        return
    
    # Obtener paso actual
    paso_actual = session_service.obtener_paso_actual(user_id)
    
    # Procesar según paso
    if paso_actual == "rotulo_mufa":
        await _procesar_rotulo_mufa(update, user_id, texto)
    elif paso_actual == "patch_panel":
        await _procesar_patch_panel(update, user_id, texto)
    elif paso_actual == "proyecto_edificio":
        await _procesar_proyecto_edificio(update, user_id, texto)
    elif paso_actual == "supervisor":
        await _procesar_supervisor(update, user_id, texto)
    elif paso_actual == "nodo":
        await _procesar_nodo(update, user_id, texto)
    else:
        await update.message.reply_text(
            f"ℹ️ En el paso '{paso_actual}' debes seleccionar botones."
        )


# ============================================================================
# PROCESADORES POR CAMPO
# ============================================================================

async def _procesar_rotulo_mufa(
    update: Update,
    user_id: int,
    rotulo: str
) -> None:
    """Procesa entrada de rótulo MUFA"""
    rotulo = rotulo.upper().strip()
    
    #logger.info(f"🔍 Usuario {user_id} ingresa MUFA: {rotulo}")
    
    # 1. Buscar coincidencias en el catálogo
    coincidencias = catalogo_service.buscar_mufas(rotulo, limit=5)
    
    if coincidencias:
        #logger.info(f"✅ Encontradas {len(coincidencias)} coincidencias para '{rotulo}'")
        
        # Crear botones para las coincidencias
        teclado = formateador.crear_teclado_opciones(coincidencias, "rotulo_mufa")
        
        await update.message.reply_text(
            f"🔎 Encontré estas MUFAs con '{rotulo}':\n"
            "Selecciona una o escribe el nombre completo si es nueva.",
            reply_markup=teclado
        )
        return

    # 2. Si no hay coincidencias (o el usuario ignora las opciones y escribe),
    # validar y guardar como nueva (comportamiento original)
    
    # Validar formato
    valido, msg = validador.validar_rotulo(rotulo)
    if not valido:
        await update.message.reply_text(msg)
        return
    
    # Guardar
    session_service.guardar_dato(user_id, "rotulo_mufa", rotulo)
    session_service.avanzar_paso(user_id)
    
    # Responder
    await update.message.reply_text(f"✅ MUFA guardada: {rotulo}")
    await update.message.reply_text(MENSAJE_PATCH_PANEL)


async def _procesar_patch_panel(
    update: Update,
    user_id: int,
    patch: str
) -> None:
    """Procesa entrada de Patch Panel"""
    patch = patch.strip().upper()
    
    #logger.info(f"📍 Usuario {user_id} ingresa Patch: {patch}")
    
    # Guardar
    session_service.guardar_dato(user_id, "patch_panel", patch)
    session_service.avanzar_paso(user_id)
    
    # Responder - mostrar tipos de trabajo
    await update.message.reply_text(f"✅ Patch Panel guardado: {patch}")
    
    # Siguiente paso: tipos de trabajo (callback)
    from config import TIPOS_TRABAJO
    teclado = formateador.crear_teclado_opciones(TIPOS_TRABAJO, "tipo_trabajo")
    await update.message.reply_text(
        "Paso 3️⃣: Selecciona el tipo de trabajo",
        reply_markup=teclado
    )


async def _procesar_proyecto_edificio(
    update: Update,
    user_id: int,
    proyecto: str
) -> None:
    """Procesa entrada de Proyecto/Edificio"""
    proyecto = proyecto.strip()
    
    logger.info(f"ingreso Proyecto: {proyecto}")
    
    # Guardar
    session_service.guardar_dato(user_id, "proyecto_edificio", proyecto)
    session_service.avanzar_paso(user_id)
    
    # Responder
    await update.message.reply_text(f"✅ Proyecto guardado: {proyecto}")
    await update.message.reply_text(MENSAJE_SUPERVISOR)


async def _procesar_supervisor(
    update: Update,
    user_id: int,
    query: str
) -> None:
    """Procesa búsqueda de supervisor"""
    #logger.info(f"🔍 Usuario {user_id} busca supervisor: {query}")
    
    # Buscar supervisores
    resultados = catalogo_service.buscar_supervisores(query, limit=5)
    
    if resultados:
        #logger.info(f"✅ {len(resultados)} supervisores encontrados")
        teclado = formateador.crear_teclado_opciones(resultados, "supervisor")
        await update.message.reply_text(
            "🔍 Supervisores encontrados:",
            reply_markup=teclado
        )
    else:
        logger.warning(f"❌ No encontrados supervisores para: {query}")
        await update.message.reply_text(
            f"❌ No se encontraron supervisores con '{query}'.\n"
            "Intenta con otro nombre."
        )


async def _procesar_nodo(
    update: Update,
    user_id: int,
    query: str
) -> None:
    """Procesa búsqueda de nodo"""
    #logger.info(f"🔍 Usuario {user_id} busca nodo: {query}")
    
    # Buscar nodos
    resultados = catalogo_service.buscar_nodos(query, limit=5)
    
    if resultados:
        #logger.info(f"✅ {len(resultados)} nodos encontrados")
        teclado = formateador.crear_teclado_opciones(resultados, "nodo")
        await update.message.reply_text(
            "🔍 Nodos encontrados:",
            reply_markup=teclado
        )
    else:
        logger.warning(f"❌ No encontrados nodos para: {query}")
        await update.message.reply_text(
            f"❌ No se encontraron nodos con '{query}'.\n"
            "Intenta con otro nombre."
        )