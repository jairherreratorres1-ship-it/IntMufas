## Mufa Telegram Bot

Este bot de Telegram está diseñado para facilitar el registro de intervenciones en Mufas. Permite a los usuarios seguir un flujo estructurado de pasos para ingresar información, validarla contra un catálogo en Google Sheets y generar una plantilla de reporte final.

## Stack Tecnológico

- **Lenguaje**: Python 3.10+
- **Framework**: `python-telegram-bot` (v20.3+)
- **HTTP/Networking**: `requests`, `httpx`
- **Configuración**: `python-dotenv`
- **Fuente de Datos**: Google Sheets (CSV publicado)

## Estructura del Proyecto

El proyecto sigue una arquitectura modular para facilitar el mantenimiento y la escalabilidad.

```
Mufas/
├── handlers/              # Controladores de eventos de Telegram
│   ├── command_handlers.py   # Manejo de comandos (/start, /help)
│   ├── message_handlers.py   # Manejo de mensajes de texto e inputs de usuario
│   └── callback_handlers.py  # Manejo de interacciones con botones (InlineButtons)
│
├── services/              # Lógica de negocio y servicios externos
│   ├── catalog_service.py    # Carga y búsqueda en catálogos (Google Sheets)
│   ├── session_service.py    # Gestión de estado de sesión de usuarios (en memoria)
│   └── validators.py         # Validaciones de entradas (Rótulos, formatos)
│
├── utils/                 # Utilidades generales
│   └── formatters.py         # Formateo de mensajes y teclados
│
├── models/                # Modelos de datos
│   └── structs.py            # Dataclasses para estructurar la información del registro
│
├── config.py                 # Configuración central (Tokens, Constantes, Textos)
├── main.py                   # Punto de entrada de la aplicación
├── .env                      # Variables de entorno (No commitear)
└── requirements.txt          # Dependencias del proyecto
```

## Configuración y Despliegue

### Prerrequisitos
- Python 3.10 o superior
- Un token de bot de Telegram (@BotFather)
- Una hoja de cálculo de Google Sheets publicada como CSV

### Instalación

1. **Clonar el repositorio** y entrar al directorio.
2. **Crear entorno virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   ```
3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar variables de entorno**:
   Crear un archivo `.env` en la raíz basado en el ejemplo:
   ```properties
   TELEGRAM_TOKEN=tu_token_aqui_123456
   WEBHOOK_URL=https://tu-dominio.com/webhook
   PORT=8000
   ```

### Ejecución
```bash
python main.py
```

## Lógica Principal

### Flujo de Conversación
El bot no utiliza `ConversationHandler` (máquina de estados compleja de la librería), sino un **gestor de sesiones propio (`SessionService`)** que almacena el "paso actual" del usuario en memoria.

1. **Inicio**: `/start` crea una sesión para el usuario.
2. **Navegación**:
   - `message_handlers` captura texto libre (ej: Rótulos, Proyectos).
   - `callback_handlers` captura selecciones de botones (ej: Tipo Mufa, Supervisor).
   - Cada acción valida la entrada, guarda el dato en `SessionService` y avanza el puntero de paso.
3. **Finalización**: Se genera una plantilla de texto con todos los datos recolectados.

### Búsqueda de Rótulos
En el paso de "Rótulo", el bot:
1. Recibe el texto del usuario.
2. Invoca `catalogo_service.buscar_mufas()` para buscar coincidencias parciales.
3. Si encuentra coincidencias, presenta botones. Si no, permite guardar el texto ingresado como un nuevo registro.

## Contribución

### Agregar nuevos pasos
1. Definir el nuevo paso en `PASOS_FLUJO` en `config.py`.
2. Crear la lógica de validación/procesamiento en `message_handlers` o `callback_handlers` según corresponda.
3. Actualizar `SessionService` si requiere lógica especial de navegación.

### Actualizar Catálogos
El catálogo se descarga automáticamente al inicio desde la URL definida en `CATALOG_URL` (`config.py`). No se requiere despliegue para actualizar datos, solo reiniciar el bot para recargar la caché.

## Troubleshooting Común

- **Error de Importación Circular**: Evitar importar `handlers` dentro de `main` y viceversa de forma directa sin controlar el ciclo. Usar inyección de dependencias (`set_dependencies`).
- **NameError (MENSAJE_...)**: Verificar que todas las constantes de texto usadas en handlers estén importadas desde `config.py`.

---
*Documentación generada para facilitar el onboarding de nuevos desarrolladores.*
