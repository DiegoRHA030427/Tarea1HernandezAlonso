# 7. Casos de uso: herramientas que ya usan MCP

Todas estas herramientas funcionan como **host MCP** (tienen clientes MCP adentro) y dejan conectar servidores locales (stdio), remotos (Streamable HTTP) o los dos.

- **Claude Desktop (Anthropic).** Es una app de escritorio para chatear con Claude. Con MCP le conectas servidores locales (archivos, bases de datos, Git) y remotos ("conectores") para que Claude lea y modifique tus datos, siempre pidiendo permiso. Es el que usé en esta tarea.
- **Claude Code (Anthropic).** Es un agente de programación que corre en la terminal o en el IDE. Aparte de sus herramientas para editar el repositorio, se le pueden agregar servidores MCP (`claude mcp add`) para conectarse con GitHub, Sentry, bases de datos, documentación, etc.
- **VS Code + GitHub Copilot (Microsoft / GitHub).** En el **modo agente**, Copilot puede usar herramientas MCP que configuras en `.vscode/mcp.json` o en la configuración de usuario. VS Code le manda al servidor las carpetas del proyecto abierto como *roots*.
- **Cursor.** Es un editor con IA basado en VS Code. Los servidores se ponen en `.cursor/mcp.json` para que su agente pueda consultar bases de datos, tickets, documentación o diseños de Figma sin que tú copies y pegues.
- **Google Antigravity (Google).** Este sí es un **entorno de desarrollo agéntico**: sus agentes planean y hacen tareas sobre el proyecto. Tiene una "MCP Store" y un archivo `mcp_config.json` para conectarse a servicios como BigQuery, AlloyDB, Firebase o Google Workspace.
- **Qwen Code (equipo Qwen de Alibaba).** Aquí hay que tener cuidado con el nombre: **Qwen es una familia de modelos**, no una plataforma. La herramienta que sí usa MCP es **Qwen Code**, un agente de terminal (basado en Gemini CLI) hecho para los modelos Qwen3-Coder. Los servidores MCP se ponen en la sección `mcpServers` de su `settings.json`.
- **Zed.** Es un editor de código que soporta servidores MCP como "context servers" para su panel de agente.

## ¿Cómo editan repositorios completos sin que subas los archivos?

Me costó un poco entenderlo, pero la clave es que **no necesitan que les subas nada**, porque hay un proceso **local** que va leyendo los archivos cuando los necesita:

1. **El host corre en tu compu** (o tiene un proceso local) y tiene acceso a la carpeta del proyecto que abriste. En VS Code, Cursor o Antigravity, el proyecto abierto es el límite (en MCP eso es lo que eran los *roots*).
2. **Lee solo lo que necesita.** En lugar de meter todo el repositorio en el prompt (que de todos modos no cabría), el modelo va **explorando**: lista las carpetas, busca por nombre o con `grep` y abre solo los archivos que le sirven. Como cuando uno llega a un proyecto nuevo y va navegando el código en lugar de imprimirlo todo.
3. **Edita con *diffs*.** Para cambiar algo, el modelo propone cambios puntuales (reemplazar un pedazo, como `edit_file`) y el host te enseña el *diff* para que lo aceptes o no.
4. **Lo hace en ciclo.** El modelo repite *pensar → usar herramienta → ver el resultado* muchas veces en una misma tarea: lee un archivo, lo edita, corre las pruebas (otra herramienta), ve el error y lo corrige.
5. **Con más servidores MCP va más allá del disco.** Puede leer el *issue* de GitHub, ver el esquema de la base de datos o revisar un error en Sentry, todo con el mismo protocolo.

Una aclaración: algunas de estas herramientas (Claude Code, Copilot, Cursor) tienen sus operaciones de archivos como **herramientas internas** del host, y usan MCP para conectarse a cosas externas. Otras, como Claude Desktop en esta tarea, tienen acceso a archivos **por medio de un servidor MCP** como el de sistema de archivos. Pero en los dos casos la idea es la misma: **el modelo propone, un proceso local ejecuta y el usuario aprueba**.
