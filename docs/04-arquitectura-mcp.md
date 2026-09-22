# 4. Arquitectura de MCP

> **Versión de la especificación que consulté:** MCP **2026-07-28**, que es la versión *Current* cuando hice esta tarea (la revisé el 21 de septiembre de 2026 en <https://modelcontextprotocol.io/specification/2026-07-28>).
> También revisé la versión anterior, **2025-11-25**, porque es la que todavía usa el servidor de archivos que instalé (lo explico al final).

## Host, cliente y servidor

MCP tiene tres roles, y es fácil confundirlos, así que los pongo con lo que yo instalé:

| Rol | Qué es | En mi instalación |
|---|---|---|
| **Host** | La aplicación de IA que usa el usuario. Coordina a los clientes, maneja los permisos y habla con el modelo. | Claude Desktop en Windows. |
| **Cliente** | Un conector que vive *dentro* del host. El host crea un cliente por cada servidor y cada uno tiene su propia conexión 1 a 1. | El conector MCP que Claude Desktop crea por dentro para hablar con el servidor `filesystem` (y otro para `servidor-escom` si agrego mi servidor propio). |
| **Servidor** | El programa que ofrece las capacidades (herramientas, recursos, prompts). | `@modelcontextprotocol/server-filesystem`, un proceso de Node.js que se ejecuta con `npx` en mi compu. |

¿Y el modelo? El modelo **no es un rol del protocolo**. Solo ve el catálogo de herramientas y propone llamadas, pero no habla MCP directamente; el que habla MCP es el cliente.

```
+-------------------- Mi compu (Windows) --------------------+
|                                                            |
|   HOST: Claude Desktop                                     |
|     Cliente MCP 1  ---stdio--->  Servidor "filesystem" ---> carpeta sandbox
|     Cliente MCP 2  ---stdio--->  Servidor "servidor-escom" (opcional)
|           ^                                                |
+-----------|------------------------------------------------+
            | HTTPS (chat + lista de herramientas + resultados)
            v
     Modelo Claude (servidores de Anthropic)
```

Dos errores que hay que evitar: el cliente **no** es todo Claude Desktop ni es el modelo, es la parte del host que se conecta con *un* servidor. Y el servidor **no** es el modelo, es el programa local que sí toca el disco.

## Capas

El protocolo tiene dos capas:

- **Capa de datos:** los mensajes JSON-RPC 2.0. Hay peticiones (con `id`, `method` y `params`), respuestas (con `result` o `error`) y notificaciones (que no llevan `id` porque no esperan respuesta).
- **Capa de transporte:** por dónde viajan esos mensajes (stdio o Streamable HTTP, más abajo lo explico).

## Primitivas

### Las que ofrece el servidor

- **Herramientas (*tools*):** son acciones que el **modelo** decide usar (con permiso del usuario). Por ejemplo leer o escribir archivos, consultar una base de datos o llamar a una API. Se usan con `tools/list` y `tools/call`. Ejemplo: `write_file(path, content)`.
- **Recursos (*resources*):** son datos de solo lectura que se identifican con una URI, como el contenido de un archivo o el esquema de una base de datos. Aquí la que decide qué se adjunta como contexto es la **aplicación**, no el modelo. Se usan con `resources/list`, `resources/read` y `resources/templates/list`. Ejemplo: `info://tarea` en mi servidor propio.
- **Plantillas de prompt (*prompts*):** son mensajes o flujos ya armados, con parámetros, que el **usuario** elige (por ejemplo como un comando `/`). Se usan con `prompts/list` y `prompts/get`. Ejemplo: `revisar_documento(tema)`.

Algo que noté al probarlo: el servidor de sistema de archivos **solo tiene herramientas**. Cuando se conecta dice que sus capacidades son `{"tools": {"listChanged": true}}` y si le pides `resources/list` te contesta `Method not found`. Por eso en mi servidor propio ([servidor-propio/](../servidor-propio/)) puse las tres primitivas, para que se vean recursos y prompts funcionando.

### Las que ofrece el cliente

Estas son cosas que el cliente le ofrece al servidor:

- **Roots:** el cliente le dice al servidor qué carpetas le "tocan", por ejemplo las carpetas del proyecto abierto en el editor. El servidor de archivos puede usar los roots en lugar de las carpetas que le pasas al arrancarlo. **Ojo:** en la versión 2026-07-28 roots quedó como **obsoleto** (*deprecated*, SEP-2577). Todavía funciona, pero la recomendación es pasar las carpetas por la configuración del servidor.
- **Elicitation:** el servidor le puede pedir al usuario información extra por medio del cliente, como llenar un formulario, confirmar algo o abrir una URL. Sigue vigente; en la versión 2026-07-28 se hace con un patrón llamado *Multi Round-Trip Requests*: el servidor contesta `resultType: "input_required"` y el cliente vuelve a mandar la petición con lo que respondió el usuario.
- **Sampling:** el servidor le pide al cliente que genere texto con *su* modelo, para que el servidor no necesite su propia llave de algún proveedor de IA. También quedó obsoleto en 2026-07-28.

## Transportes

- **stdio:** es para servidores **locales** y es el que uso con el servidor de archivos. El host ejecuta el servidor como un **proceso hijo** (`npx ... server-filesystem <carpeta>`). El cliente le escribe los mensajes JSON-RPC por la **entrada estándar** y lee las respuestas por la **salida estándar**, un mensaje por línea. La salida de errores (`stderr`) se usa para los logs. No hay red de por medio.
- **Streamable HTTP:** es para servidores **remotos**, por ejemplo uno en la nube que usan muchos clientes. El cliente manda cada mensaje con un **POST** a un solo endpoint (tipo `https://servidor/mcp`) y el servidor contesta con JSON o con un flujo SSE (*Server-Sent Events*) si tiene que mandar varios mensajes. Para autorización se usa OAuth 2.1. En la versión 2026-07-28 se quitaron las sesiones (ya no existe el header `Mcp-Session-Id`).

Antes había otro transporte, HTTP+SSE con dos endpoints, pero está obsoleto desde la versión 2025-03-26.

## Cómo pasa una llamada, paso a paso

Con mi instalación sería así:

1. Abro Claude Desktop, lee `claude_desktop_config.json` y ejecuta `npx -y @modelcontextprotocol/server-filesystem C:\dev\Tarea1HernandezAlonso\sandbox`.
2. El cliente y el servidor se ponen de acuerdo en la versión y las capacidades.
3. El cliente pide `tools/list` y el host agrega las 14 herramientas a lo que le manda al modelo.
4. Yo escribo: "Lista los archivos de mi sandbox".
5. El modelo contesta con una solicitud para usar una herramienta: `list_directory({ "path": "C:\\dev\\...\\sandbox" })`.
6. Claude Desktop me pregunta si lo permito (una vez, siempre o no).
7. El cliente manda `tools/call`, el servidor revisa que la ruta sea válida, lee la carpeta y regresa el resultado.
8. El host le pasa el resultado al modelo y el modelo me contesta.

## Lo que cambió en la versión 2026-07-28

Esta versión cambió bastante comparada con la 2025-11-25:

- MCP ahora es **sin estado** (*stateless*). Ya no existe el saludo inicial `initialize` / `notifications/initialized`; ahora **cada** petición lleva en `_meta` la versión del protocolo y las capacidades del cliente.
- Se agregó `server/discover`, que el servidor tiene que implementar para decir qué versiones y capacidades soporta.
- Se quitaron `ping`, `logging/setLevel` y las sesiones de Streamable HTTP.
- Las *tasks* (tareas largas asíncronas) ahora son una extensión oficial aparte.
- Roots, Sampling y Logging quedaron obsoletos.

Lo curioso es que cuando probé el servidor de archivos (versión npm `2026.8.31`), **todavía contesta al saludo `initialize` con `protocolVersion: "2025-11-25"`**. O sea, las implementaciones van atrasadas respecto a la especificación, y por eso la misma especificación tiene reglas para que clientes nuevos puedan hablar con servidores de la versión anterior. Por lo mismo es importante decir siempre sobre qué versión está escrito un documento de MCP.
