# 3. MCP frente a una API

La idea principal que saqué de este punto es esta: con una API, **yo como programador** decido desde antes qué se llama y cuándo. Con MCP, **el modelo** ve en el momento qué herramientas hay y decide cuál usar según lo que le pidió el usuario.

## ¿Qué es una API?

Una API (*Application Programming Interface*) es un contrato entre programas. Dice qué operaciones ofrece un servicio, qué parámetros recibe cada una y qué te regresa. Por ejemplo, una API REST tiene endpoints así:

```
GET  /api/usuarios/42
POST /api/usuarios        { "nombre": "Diego", "grupo": "7CV4" }
```

Cuando uso una API el proceso es más o menos este:

1. Leo la documentación (o el Swagger / OpenAPI).
2. Decido qué endpoint me sirve.
3. Armo la petición: URL, método, headers, body, token.
4. Escribo el código que procesa la respuesta (parsear el JSON, manejar errores, etc.).

Un ejemplo de lo que hemos hecho en la materia, una app Android que consume una API con Retrofit:

```kotlin
interface UsuariosApi {
    @GET("api/usuarios/{id}")
    suspend fun getUsuario(@Path("id") id: Int): Usuario
}

override fun onResume() {
    super.onResume()
    lifecycleScope.launch { mostrar(api.getUsuario(42)) }
}
```

Aquí la decisión de "llamar a `getUsuario` cuando se abre la pantalla" ya está escrita en el código. Si la API agrega un endpoint nuevo mañana, mi app no lo va a usar hasta que yo lea la documentación, escriba el código y saque otra versión.

## ¿Qué es MCP?

MCP (*Model Context Protocol*) es un **protocolo abierto** basado en **JSON-RPC 2.0** que estandariza cómo una aplicación de IA se conecta con herramientas y fuentes de datos externas. Lo presentó Anthropic en noviembre de 2024 como estándar abierto, y en diciembre de 2025 lo donaron a la **Agentic AI Foundation** de la Linux Foundation, donde también participan empresas como OpenAI, Google y Microsoft (Anthropic, 2025; Linux Foundation, 2025). O sea, no es algo de una sola empresa: lo usan clientes de varias, como Claude, VS Code con Copilot, Cursor, Zed, Google Antigravity o Qwen Code.

En MCP, un servidor publica un **catálogo de herramientas**. Cada herramienta tiene:

- un nombre (por ejemplo `read_text_file`),
- una descripción en lenguaje normal de lo que hace,
- y un esquema JSON con sus parámetros (`inputSchema`).

El cliente le pide ese catálogo al servidor con `tools/list`:

```json
{ "jsonrpc": "2.0", "id": 2, "method": "tools/list" }
```

Y el servidor contesta algo así (esto es un pedazo de la respuesta real del servidor de archivos):

```json
{
  "jsonrpc": "2.0", "id": 2,
  "result": {
    "tools": [
      {
        "name": "read_text_file",
        "description": "Read the complete contents of a file from the file system as text...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "path": { "type": "string" },
            "head": { "type": "number" },
            "tail": { "type": "number" }
          },
          "required": ["path"]
        },
        "annotations": { "readOnlyHint": true, "openWorldHint": false }
      }
    ]
  }
}
```

La app host le pasa ese catálogo al modelo. Entonces si yo escribo "¿qué dice mi archivo de notas?", el modelo lee las descripciones, decide que le sirve `read_text_file` y genera los argumentos. El host manda:

```json
{
  "jsonrpc": "2.0", "id": 3,
  "method": "tools/call",
  "params": { "name": "read_text_file", "arguments": { "path": "C:\\dev\\Tarea1HernandezAlonso\\sandbox\\notas.md" } }
}
```

Nadie programó un `if (preguntan por notas) leerArchivo()`. La decisión se toma **en tiempo de ejecución**, a partir de lo que escribí.

## Tabla comparativa

| Criterio | API tradicional (REST, por ejemplo) | MCP |
|---|---|---|
| ¿Quién decide qué se invoca? | El programador, cuando escribe el código. Queda fijo. | El modelo, cuando se está usando, según lo que pidió el usuario. El host puede pedir que el usuario apruebe. |
| ¿Cómo se descubren las capacidades? | Leyendo la documentación antes de programar. | El cliente llama a `tools/list`, `resources/list` y `prompts/list` cuando se conecta. El catálogo lo puede leer una máquina y trae descripciones pensadas para el modelo. Además puede cambiar en vivo (notificación `list_changed`). |
| ¿Qué tan acoplado está el cliente al servicio? | Mucho. El cliente tiene que conocer las URLs, parámetros y formatos de cada endpoint; si algo cambia, se rompe. | Poco. El cliente solo conoce el protocolo; si el servidor agrega una herramienta, se puede usar sin cambiar el cliente. |
| Formato de los mensajes | Cada API usa el suyo: JSON, XML, GraphQL, gRPC… | Siempre JSON-RPC 2.0 (`method`, `params`, `id`, `result`/`error`), ya sea por stdio o por Streamable HTTP. |
| Autenticación | Cada API tiene la suya (API key, OAuth, JWT, sesiones…) y hay que programarla. | En servidores locales normalmente son variables de entorno del proceso. En servidores remotos la especificación define un flujo de autorización basado en OAuth 2.1. |
| Consentimiento | No es parte del contrato, cada app decide si le pregunta algo al usuario. | Es un principio de la especificación: el host debe pedir consentimiento antes de usar herramientas o compartir datos. Las anotaciones (`readOnlyHint`, `destructiveHint`) ayudan a decidir qué confirmar. |
| Reutilización entre aplicaciones | Cada app hace su propia integración. Si hay N apps y M servicios, son N×M integraciones. | Un servidor se hace una vez y funciona en cualquier host compatible. Son N+M piezas. |

Una analogía que me ayudó: las APIs son como los cargadores de celular de antes, cada marca tenía el suyo. MCP es como USB-C: cada aparato hace sus cosas por dentro, pero todos se conectan igual.

## MCP no sustituye a las APIs

Esto hay que dejarlo claro porque es fácil confundirse: **MCP no hace que las APIs ya no sirvan, funciona encima de ellas.**

Un servidor MCP casi siempre "envuelve" una API o un recurso que ya existe:

- El servidor MCP de GitHub por dentro usa la API de GitHub.
- Un servidor MCP de base de datos usa el driver de PostgreSQL (que también es una API).
- El servidor de sistema de archivos usa la API del sistema operativo (en Node.js es el módulo `fs`).

```
Modelo
  |  (decide qué usar)
Host / Cliente MCP
  |  JSON-RPC 2.0 (tools/list, tools/call)
Servidor MCP  ----->  API que ya existía (REST, SDK, fs, SQL...)
```

Lo que agrega MCP es una forma estándar de descubrir y llamar esas cosas para que un modelo las pueda usar sin que alguien tenga que programar la integración para cada app.

Y también hay casos donde una API normal sigue siendo lo mejor. Por ejemplo, en una app móvil que solo guarda un formulario en el backend, no tiene sentido meter MCP; lo que necesitas es un `POST` que sea rápido y siempre haga lo mismo.

## En corto (para la exposición)

- **API:** yo leo la documentación, decido y programo la llamada. El contrato es fijo y cada integración se hace a la medida.
- **MCP:** el servidor dice qué puede hacer, el modelo decide qué usar y el host pide permiso. Es estándar y se puede reutilizar.
- **Cómo se relacionan:** MCP es una capa **encima** de las APIs, no las reemplaza.
