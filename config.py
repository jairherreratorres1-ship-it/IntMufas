import os
from dotenv import load_dotenv
load_dotenv()   
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if  not TELEGRAM_TOKEN:
    raise ValueError(
        "Error: TELEGRAM_TOKEN no configurado\n"
        "Agregar en .env: TELEGRAM_TOKEN=tu token"
    )

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tu-dominio.com/webhook")
PORT = int(os.getenv("PORT", "8000"))

if not WEBHOOK_URL:
    raise ValueError(
        "Error: WEBHOOK_URL no configurado\n"
        "Agregar en .env: WEBHOOK_URL=https://tu-dominio.com/webhook"
    )

CATALOG_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQJahSyq-sshf4WrjKApNUzWnzaBeOjHfOBu1aF3Q5oBCw6Q4-QxypyOcoYbzQ2IkpjxCAhdjGfhwTr/pub?gid=0&single=true&output=csv"

TIPOS_MUFA = [
    "Mufa existente",
    "Mufa proyectada"
]

TIPOS_TRABAJO = [
    "Avería",
    "Implementación"
]

ESTADOS_MUFA = [
    "BUEN ESTADO",
    "SATURADA",
    "CRÍTICA"
]

# PASOS DEL FLUJO


PASOS_FLUJO = [
    "tipo_mufa",           # Existente o Proyectada
    "rotulo_mufa",         # Ingresa el rótulo
    "patch_panel",         # Patch panel
    "tipo_trabajo",        # Avería o Implementación
    "proyecto_edificio",   # Solo si es Implementación
    "supervisor",          # Supervisor
    "nodo",                # Nodo
    "estado",              # Estado (solo si es Existente)
    "confirmacion"         # Confirmación final
]

# MENSAJES
MENSAJE_BIENVENIDA = "Bienvenido al de Registro MUFA\n\nEste bot te ayuda a llenar la plantilla de intervenciones Mufas.\n\nPrimero, indica qué tipo de MUFA es:"
MENSAJE_TIPO_MUFA = "¿Qué tipo de MUFA es?"
MENSAJE_ROTULO_MUFA = "Ingresa el rótulo de la MUFA (ej: WN-DM-1531977)"
MENSAJE_PATCH_PANEL = "Escriba el Patch panel"
MENSAJE_TIPO_TRABAJO = "Seleccione el tipo de trabajo"
MENSAJE_PROYECTO_EDIFICIO = "Escribe el proyecto o edificio que está trabajando"
MENSAJE_SUPERVISOR = "Escribe parte del nombre del supervisor"
MENSAJE_NODO = "Escribe parte del nombre del nodo"
MENSAJE_ESTADO = "Selecciona el estado de la MUFA"


# PATRONES DE VALIDACIÓN
PATRON_MUFA = r'^[A-Z0-9\-]{5,50}$'