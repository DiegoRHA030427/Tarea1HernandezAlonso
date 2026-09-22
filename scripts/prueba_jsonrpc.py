"""
Prueba del servidor de sistema de archivos hablando JSON-RPC 2.0 "a mano" por stdio,
sin ningún modelo de por medio. Sirve para:
  1. Ver los mensajes reales del protocolo (initialize, tools/list, tools/call).
  2. Demostrar que el LÍMITE DE SEGURIDAD lo aplica el SERVIDOR, no el modelo.

Uso (desde C:\dev\Tarea1HernandezAlonso):
    python scripts\prueba_jsonrpc.py
Requisitos: Python 3.10+ y Node.js (npx) en el PATH.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SANDBOX = REPO / "sandbox"
PAQUETE = "@modelcontextprotocol/server-filesystem@2026.8.31"

npx = shutil.which("npx")
if not npx:
    sys.exit("No se encontró npx. Instala Node.js LTS y vuelve a abrir la terminal.")

proc = subprocess.Popen(
    [npx, "-y", PAQUETE, str(SANDBOX)],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    text=True, encoding="utf-8",
)


def enviar(mensaje: dict) -> None:
    linea = json.dumps(mensaje, ensure_ascii=False)
    print(f"\n>>> {linea}")
    proc.stdin.write(linea + "\n")
    proc.stdin.flush()


def recibir(id_esperado: int) -> dict:
    while True:
        linea = proc.stdout.readline()
        if not linea:
            sys.exit("El servidor cerró la conexión.")
        respuesta = json.loads(linea)
        if respuesta.get("id") == id_esperado:
            return respuesta


def llamar(id_: int, herramienta: str, argumentos: dict) -> dict:
    enviar({"jsonrpc": "2.0", "id": id_, "method": "tools/call",
            "params": {"name": herramienta, "arguments": argumentos}})
    r = recibir(id_)
    res = r["result"]
    estado = "ERROR" if res.get("isError") else "OK"
    print(f"<<< [{estado}] {res['content'][0]['text'][:300]}")
    return r


# 1) Saludo (el servidor implementa la revisión 2025-11-25 del protocolo)
enviar({"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                   "clientInfo": {"name": "prueba-manual", "version": "1.0"}}})
print("<<<", json.dumps(recibir(1)["result"], ensure_ascii=False))
enviar({"jsonrpc": "2.0", "method": "notifications/initialized"})

# 2) Descubrimiento del catálogo
enviar({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
herramientas = recibir(2)["result"]["tools"]
print(f"<<< {len(herramientas)} herramientas:")
for h in herramientas:
    print(f"    - {h['name']:<26} {h.get('annotations', {})}")

# 3) Operaciones permitidas
llamar(3, "list_allowed_directories", {})
llamar(4, "list_directory", {"path": str(SANDBOX)})

# 4) Prueba del límite: ruta absoluta fuera del sandbox y ruta con '..'
llamar(5, "read_text_file", {"path": str(REPO / "README.md")})
llamar(6, "read_text_file", {"path": str(SANDBOX / ".." / "README.md")})

proc.stdin.close()
proc.terminate()
