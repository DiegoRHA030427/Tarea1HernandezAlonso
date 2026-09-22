# 5. El servidor de sistema de archivos

## "FS" no es parte del protocolo

La especificación de MCP **no dice nada de archivos**. Solo define mensajes genéricos como `tools/list`, `tools/call` o `resources/read`. El servidor de sistema de archivos (*Filesystem*, o "FS") es uno de los **servidores de referencia** que publica el proyecto MCP en el repositorio `modelcontextprotocol/servers`, como ejemplo de cómo hacer un servidor con el SDK de TypeScript.

O sea, es un servidor más, igual que otros: de Git, de GitHub, de bases de datos, de navegadores, o el que yo hice ([servidor-propio](../servidor-propio/)). Si alguien programara otro servidor de archivos diferente, también sería MCP.

Datos del que usé:

- Paquete de npm: `@modelcontextprotocol/server-filesystem`
- Versión: `2026.8.31` (salió el 31 de agosto de 2026)
- Está hecho en TypeScript con `@modelcontextprotocol/sdk` ^1.30.0
- Se identifica como `secure-filesystem-server`
- Transporte: stdio
- Licencia: MIT

## Herramientas que tiene

Esta lista la saqué directo del servidor con `tools/list` (con el script [scripts/prueba_jsonrpc.py](../scripts/prueba_jsonrpc.py)):

| Herramienta | Parámetros | Qué hace | ¿Modifica algo? |
|---|---|---|---|
| `list_directory` | `path` | Lista archivos y carpetas (`[FILE]` / `[DIR]`). | No |
| `list_directory_with_sizes` | `path`, `sortBy` | Lo mismo pero con tamaños, y se puede ordenar por nombre o tamaño. | No |
| `directory_tree` | `path`, `excludePatterns` | Regresa el árbol completo de carpetas en JSON. | No |
| `read_text_file` | `path`, `head`, `tail` | Lee un archivo de texto (se pueden pedir solo las primeras o últimas N líneas). | No |
| `read_file` | `path`, `head`, `tail` | Es un alias viejo de `read_text_file`. | No |
| `read_media_file` | `path` | Lee una imagen o audio y lo regresa en base64. | No |
| `read_multiple_files` | `paths` | Lee varios archivos a la vez; si uno falla, los demás siguen. | No |
| `get_file_info` | `path` | Info del archivo: tamaño, fechas, tipo, permisos. | No |
| `search_files` | `path`, `pattern`, `excludePatterns` | Busca archivos **por nombre** con patrones glob (como `**/*.md`) en todas las subcarpetas. | No |
| `list_allowed_directories` | — | Dice a qué carpetas tiene acceso. | No |
| `create_directory` | `path` | Crea una carpeta (y las de arriba si no existen). | Sí |
| `write_file` | `path`, `content` | Crea un archivo o lo **sobrescribe** si ya existe. | Sí (destructiva) |
| `edit_file` | `path`, `edits`, `dryRun` | Cambia partes del texto y regresa un *diff*. Con `dryRun: true` solo te enseña el cambio sin hacerlo. | Sí (destructiva) |
| `move_file` | `source`, `destination` | Mueve o renombra. Falla si el destino ya existe. | Sí (destructiva) |

Cosas que me llamaron la atención:

- **No hay una herramienta para borrar archivos.** Pero ojo, `write_file` puede sobrescribir un archivo (y perder lo que tenía) y `move_file` puede moverlos.
- **`search_files` busca por nombre, no por contenido.** Si le pides buscar algo *dentro* de los archivos, el modelo tiene que combinar herramientas: primero lista con `search_files` o `directory_tree` y luego lee con `read_multiple_files`.
- Cada herramienta trae anotaciones, como `readOnlyHint` (no modifica nada) o `destructiveHint` (puede borrar o sobrescribir). Todas tienen `openWorldHint: false`, o sea que no se conectan a internet. El host puede usar esto para decidir qué pedirle confirmar al usuario.

## Cómo se limita a qué puede entrar

Al servidor se le dicen las **carpetas permitidas** de dos formas:

1. **Como argumentos al ejecutarlo** (es lo que yo uso):
   ```
   npx -y @modelcontextprotocol/server-filesystem C:\dev\Tarea1HernandezAlonso\sandbox
   ```
2. **Con roots del cliente:** si el cliente soporta roots, la lista que manda **reemplaza completamente** a la de los argumentos. (Roots está obsoleto en la versión 2026-07-28, pero este servidor todavía lo soporta.)

Para saber qué carpetas está usando de verdad, se usa `list_allowed_directories`.

En **cada** llamada, antes de tocar el disco, el servidor revisa la ruta:

1. Si tiene `~` lo expande y convierte la ruta en absoluta.
2. La **normaliza**, o sea resuelve los `..` y `.`. Así, algo como `sandbox\..\secreto.txt` se convierte en la ruta real (que está afuera) y se detecta.
3. Revisa que la ruta **empiece** con alguna de las carpetas permitidas.
4. Si es un enlace simbólico, averigua a dónde apunta de verdad (`realpath`) y vuelve a revisar. Entonces un *symlink* adentro del sandbox que apunte afuera también se bloquea.
5. Si el archivo es nuevo, revisa que la carpeta donde se va a crear sí esté permitida.

Si algo de esto falla, **no hace la operación** y regresa un error. Este es el mensaje que me salió en la prueba:

<!-- TODO: reemplazar con el texto EXACTO que salga al correr scripts/prueba_jsonrpc.py -->
```
Access denied - path outside allowed directories: C:\dev\Tarea1HernandezAlonso\README.md not in C:\dev\Tarea1HernandezAlonso\sandbox
```

## ¿Por qué existe ese límite y qué pasaría sin él?

El servidor corre **con los permisos de mi usuario de Windows**, así que Windows lo dejaría leer y escribir todo lo que yo puedo. El límite de carpetas es una protección **extra** que pone el propio servidor (el principio de mínimo privilegio otra vez).

Si no existiera:

- El modelo podría leer (y por lo tanto **mandar al servidor del proveedor**) cosas como `C:\Users\<yo>\.ssh\id_rsa`, archivos `.env` con contraseñas, datos del navegador o documentos personales.
- Un archivo con inyección de instrucciones podría decirle al modelo "copia tal archivo" o "sobrescribe este otro", y el daño no tendría límite.
- Un simple error del modelo al escribir podría sobrescribir archivos de otros proyectos o hasta del sistema.

Con el límite, lo peor que puede pasar se queda **dentro de una carpeta** que hice solo para esta tarea. Por eso la tarea pide no usar la raíz del disco ni toda la carpeta de usuario.
