# Servidor MCP propio: `servidor-escom` (parte opcional)

Servidor MCP mínimo escrito en **Python** con el **SDK oficial** (`mcp` 2.2.0). Implementa las **tres primitivas de servidor** para demostrar lo que el servidor de sistema de archivos no expone:

| Primitiva | Nombre | Qué hace |
|---|---|---|
| Herramienta | `contar_palabras(texto)` | Devuelve número de palabras, caracteres y líneas. |
| Herramienta | `estadisticas_calificaciones(calificaciones)` | Promedio, mediana, mínimo, máximo, desviación estándar y si aprueba (≥ 6). Rechaza valores fuera de 0–10 con un error controlado (`ToolError`). |
| Recurso | `info://tarea` | Texto con los datos de la tarea y del alumno. |
| Prompt | `revisar_documento(tema)` | Plantilla para pedir una revisión técnica de un documento. |

Transporte: **stdio** (Claude Desktop lo lanza como proceso hijo).

> **Nota sobre el SDK:** en la versión 2.x del SDK de Python la clase `FastMCP` se renombró a **`MCPServer`** (`from mcp.server import MCPServer`). Muchos tutoriales en internet todavía usan `from mcp.server.fastmcp import FastMCP`, que en 2.x lanza `ModuleNotFoundError`.

## Instalación (Windows, PowerShell)

```powershell
cd C:\dev\Tarea1HernandezAlonso\servidor-propio
py -m venv .venv
.\.venv\Scripts\Activate.ps1          # si PowerShell lo bloquea: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
python -c "from mcp.server import MCPServer; print('SDK OK')"
```

## Conexión con Claude Desktop

Agregar la entrada `servidor-escom` a `%APPDATA%\Claude\claude_desktop_config.json` (ver [../config/claude_desktop_config.con-servidor-propio.json](../config/claude_desktop_config.con-servidor-propio.json)):

```json
"servidor-escom": {
  "command": "C:\\dev\\Tarea1HernandezAlonso\\servidor-propio\\.venv\\Scripts\\python.exe",
  "args": ["C:\\dev\\Tarea1HernandezAlonso\\servidor-propio\\servidor.py"]
}
```

Se usa el `python.exe` **del entorno virtual** (ruta absoluta) para que Claude Desktop encuentre el paquete `mcp` sin depender del PATH.

Cerrar Claude Desktop por completo (también desde la bandeja del sistema) y volver a abrirlo.

## Pruebas sugeridas en el chat

1. *"Usa contar_palabras para contar las palabras de: El protocolo MCP es abierto"*
2. *"Calcula las estadísticas de estas calificaciones: 8, 9.5, 7, 10"*
3. *"Calcula las estadísticas de: 8, 11"* → debe regresar el error controlado.
4. Adjuntar el recurso `info://tarea` desde el menú de conectores/adjuntos.
5. Usar el prompt `revisar_documento` desde el menú de prompts del servidor.

📸 Capturas: `img/13-servidor-propio-herramientas.png`, `img/14-servidor-propio-uso.png`.
