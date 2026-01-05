# handlers/callback_handlers.py
# ============================================================================
# RESPONSABILIDAD: Procesar clicks en botones (callbacks)
# ============================================================================

import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    TIPOS_TRABAJO,
    ESTADOS_MUFA,
    MENSAJE_ROTULO_MUFA,
    MENSAJE_PATCH_PANEL,
    MENSAJE_PROYECTO_EDIFICIO,
    MENSAJE_SUPERVISOR,
    MENSAJE_NODO,
    MENSAJE_ESTADO,
)
from services.catalog_service import CatalogoService
from services.session_service import SessionService
from utils.formatters import FormateadorMensajes

logger = logging.getLogger(__name__)

# Inyección de dependencias
catalogo_service: CatalogoService = None
session_service: SessionService = None
formateador = FormateadorMensajes()


def set_dependencies(
    catalog_svc: CatalogoService,
    session_svc: SessionService
) -> None:
    """Asigna los servicios necesarios"""
    global catalogo_service, session_service
    catalogo_service = catalog_svc
    session_service = session_svc
    logger.info("✅ Dependencias asignadas a callback_handlers")


# ============================================================================
# HANDLER PRINCIPAL
# ============================================================================

async def handle_callback_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Maneja clicks en botones (callbacks).
    
    Router que dirige según callback_data.
    """
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    #logger.info(f"🔘 Usuario {user_id} hizo click: {callback_data}")
    
    # Responder al click
    await query.answer()
    
    # Obtener sesión
    if not session_service.sesion_existe(user_id):
        await query.edit_message_text("❌ Sesión expirada. Usa /start.")
        return
    
    # Procesar según tipo de callback
    if callback_data.startswith("tipo_mufa:"):
        await _handle_tipo_mufa(query, user_id, callback_data)
    elif callback_data.startswith("tipo_trabajo:"):
        await _handle_tipo_trabajo(query, user_id, callback_data)
    elif callback_data.startswith("supervisor:"):
        await _handle_supervisor(query, user_id, callback_data)
    elif callback_data.startswith("nodo:"):
        await _handle_nodo(query, user_id, callback_data)
    elif callback_data.startswith("estado:"):
        await _handle_estado(query, user_id, callback_data)
    elif callback_data.startswith("rotulo_mufa:"):
        await _handle_rotulo_mufa_seleccionado(query, user_id, callback_data)
    elif callback_data == "guardar":
        await _handle_guardar(query, user_id)
    elif callback_data == "cancelar":
        await _handle_cancelar(query, user_id)
    elif callback_data == "back":
        await _handle_retroceder(query, user_id)
    else:
        logger.warning(f"⚠️ Callback desconocido: {callback_data}")
        await query.edit_message_text("❌ Opción no reconocida.")


# ============================================================================
# SELECTORES
# ============================================================================

async def _handle_tipo_mufa(
    query,
    user_id: int,
    callback_data: str
) -> None:
    """Maneja selección de tipo MUFA (Existente o Proyectada)"""
    tipo_mufa = callback_data.split(":", 1)[1]
    
    logger.info(f"Tipo MUFA: {tipo_mufa}")
    
    # Guardar
    session_service.guardar_dato(user_id, "tipo_mufa", tipo_mufa)
    session_service.avanzar_paso(user_id)
    
    # Responder
    await query.edit_message_text(f"✅ Tipo MUFA: {tipo_mufa}")
    await query.message.reply_text(MENSAJE_ROTULO_MUFA)


async def _handle_tipo_trabajo(
    query,
    user_id: int,
    callback_data: str
) -> None:
    """Maneja selección de tipo de trabajo (Avería o Implementación)"""
    tipo_trabajo = callback_data.split(":", 1)[1]
    
    logger.info(f"Tipo de trabajo: {tipo_trabajo}")
    
    # Guardar
    session_service.guardar_dato(user_id, "tipo_trabajo", tipo_trabajo)
    
    # Lógica: si es Implementación, solicitar Proyecto
    if tipo_trabajo == "Implementación":
        session_service.avanzar_paso(user_id)  # Ir a proyecto_edificio
        
        await query.edit_message_text(f"✅ Tipo de trabajo: {tipo_trabajo}")
        await query.message.reply_text(MENSAJE_PROYECTO_EDIFICIO)
    else:
        # Si es Avería, saltar Proyecto y ir a Supervisor
        # Avanzar dos pasos: tipo_trabajo → proyecto_edificio → supervisor
        session_service.avanzar_paso(user_id)  # proyecto_edificio
        session_service.avanzar_paso(user_id)  # supervisor
        
        await query.edit_message_text(f"✅ Tipo de trabajo: {tipo_trabajo}")
        await query.message.reply_text(MENSAJE_SUPERVISOR)


async def _handle_supervisor(
    query,
    user_id: int,
    callback_data: str
) -> None:
    """Maneja selección de supervisor"""
    supervisor = callback_data.split(":", 1)[1]
    
    logger.info(f"Supervisor: {supervisor}")
    
    # Guardar
    session_service.guardar_dato(user_id, "supervisor", supervisor)
    session_service.avanzar_paso(user_id)
    
    # Responder
    await query.edit_message_text(f"✅ Supervisor: {supervisor}")
    await query.message.reply_text(MENSAJE_NODO)


async def _handle_nodo(
    query,
    user_id: int,
    callback_data: str
) -> None:
    """Maneja selección de nodo"""
    nodo = callback_data.split(":", 1)[1]
    
    logger.info(f"Nodo: {nodo}")
    
    # Guardar
    session_service.guardar_dato(user_id, "nodo", nodo)
    
    # Lógica: si fue MUFA Proyectada, no solicitar estado
    datos = session_service.obtener_datos(user_id)
    if datos.get("tipo_mufa") == "Mufa proyectada":
        # Mufa proyectada: no solicitar estado, ir directamente a confirmación
        session_service.avanzar_paso(user_id)  # nodo → estado (saltamos)
        session_service.avanzar_paso(user_id)  # estado → confirmacion
        
        await query.edit_message_text(f"✅ Nodo: {nodo}")
        await _mostrar_confirmacion(query, user_id)
    else:
        # Mufa existente: solicitar estado
        session_service.avanzar_paso(user_id)  # nodo → estado
        
        await query.edit_message_text(f"✅ Nodo: {nodo}")
        teclado = formateador.crear_teclado_opciones(ESTADOS_MUFA, "estado")
        await query.message.reply_text(
            MENSAJE_ESTADO,
            reply_markup=teclado
        )


async def _handle_estado(
    query,
    user_id: int,
    callback_data: str
) -> None:
    """Maneja selección de estado (solo para MUFA Existente)"""
    estado = callback_data.split(":", 1)[1]
    
    logger.info(f"Estado: {estado}")
    
    # Guardar
    session_service.guardar_dato(user_id, "estado", estado)
    session_service.avanzar_paso(user_id)  # estado → confirmacion
    
    await query.edit_message_text(f"✅ Estado: {estado}")
    await _mostrar_confirmacion(query, user_id)


async def _handle_rotulo_mufa_seleccionado(
    query,
    user_id: int,
    callback_data: str
) -> None:
    """Maneja selección de Rótulo MUFA desde búsqueda"""
    rotulo = callback_data.split(":", 1)[1]
    
    logger.info(f"Rótulo MUFA: {rotulo}")
    
    # Guardar
    session_service.guardar_dato(user_id, "rotulo_mufa", rotulo)
    session_service.avanzar_paso(user_id)
    
    # Responder
    await query.edit_message_text(f"✅ MUFA seleccionada: {rotulo}")
    await query.message.reply_text(MENSAJE_PATCH_PANEL)


async def _mostrar_confirmacion(query, user_id: int) -> None:
    """Muestra resumen y solicita confirmación"""
    datos = session_service.obtener_datos(user_id)
    
    # Crear resumen
    mensaje_confirmacion = formateador.formatear_confirmacion(datos)
    teclado = formateador.crear_teclado_confirmacion()
    
    await query.message.reply_text(
        mensaje_confirmacion,
        reply_markup=teclado
    )


# ============================================================================
# ACCIONES: Guardar, Cancelar, Retroceder
# ============================================================================

async def _handle_guardar(query, user_id: int) -> None:
    """Maneja el click en 'Guardar'"""
    logger.info("Presiono Guardar")
    
    datos = session_service.obtener_datos(user_id)
    
    # Crear registro y generar plantilla
    from models.structs import RegistroMUFA
    
    registro = RegistroMUFA(
        user_id=user_id,
        tipo_mufa=datos.get("tipo_mufa", ""),
        rotulo_mufa=datos.get("rotulo_mufa", ""),
        patch_panel=datos.get("patch_panel", ""),
        tipo_trabajo=datos.get("tipo_trabajo", ""),
        proyecto_edificio=datos.get("proyecto_edificio"),
        supervisor=datos.get("supervisor"),
        nodo=datos.get("nodo"),
        estado=datos.get("estado")
    )
    
    # Generar plantilla
    plantilla = registro.generar_plantilla()
    
    # Limpiar sesión
    session_service.limpiar_sesion(user_id)
    
    # Responder con plantilla
    await query.edit_message_text("✅ Registro guardado con éxito.")
    await query.message.reply_text(plantilla)
    await query.message.reply_text("Usa /start para iniciar un nuevo registro.")
    logger.info(f"✅ Registro guardado para usuario {user_id}")


async def _handle_cancelar(query, user_id: int) -> None:
    """Maneja el click en 'Cancelar'"""
    logger.info(f"❌ Usuario {user_id} presiona cancelar")
    
    session_service.limpiar_sesion(user_id)
    
    await query.edit_message_text("❌ Registro cancelado.")
    await query.message.reply_text(
        "Usa /start para iniciar un nuevo registro."
    )


async def _handle_retroceder(query, user_id: int) -> None:
    """Maneja el click en 'Retroceder'"""
    logger.info(f"⬅️ Usuario {user_id} retrocede")
    
    if not session_service.retroceder_paso(user_id):
        await query.edit_message_text(
            "⚠️ No se puede retroceder más. Estamos en el primer paso."
        )
        return
    
    paso_actual = session_service.obtener_paso_actual(user_id)
    
    await query.edit_message_text(f"↩️ Retrocediendo al paso: {paso_actual}")