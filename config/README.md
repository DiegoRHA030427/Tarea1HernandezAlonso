# Archivos de configuración

Ninguno contiene credenciales, llaves ni tokens.

| Archivo | Uso |
|---|---|
| `claude_desktop_config.json` | **Configuración principal** de la tarea: servidor de sistema de archivos limitado a `C:\dev\Tarea1HernandezAlonso\sandbox`. |
| `claude_desktop_config.con-servidor-propio.json` | Igual que la anterior + el servidor MCP propio (`servidor-escom`, parte opcional). |
| `claude_desktop_config.solo-lectura-docker.json` | Alternativa de mitigación (no es la que se usa en la demo): corre el servidor en Docker y monta el sandbox **en solo lectura** (`,ro`). Requiere Docker Desktop. |

Ubicación en Windows: `%APPDATA%\Claude\claude_desktop_config.json`
(la forma más segura de abrirlo es Claude Desktop → *Settings* → *Developer* → *Edit Config*).

Notas:
- En JSON las diagonales invertidas de Windows se escriben dobles: `C:\\dev\\...`.
- La versión del paquete está **fijada** (`@2026.8.31`) para que la instalación sea reproducible y para no ejecutar automáticamente versiones nuevas no revisadas.
