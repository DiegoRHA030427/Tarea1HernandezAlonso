#!/usr/bin/env node
/*
 * Adaptador (proxy) stdio para servidores MCP.
 *
 * Problema: el servidor @modelcontextprotocol/server-filesystem declara los
 * esquemas de sus herramientas (inputSchema / outputSchema) con
 * "$schema": "http://json-schema.org/draft-07/schema#".
 * La especificación MCP 2026-07-28 (SEP-2106) usa JSON Schema 2020-12 y el
 * validador de Claude Desktop rechaza el dialecto draft-07.
 *
 * Solución: este proceso se pone EN MEDIO del host y del servidor.
 *   host  --stdin-->  proxy  --stdin-->  servidor
 *   host  <--stdout-- proxy  <--stdout-- servidor
 * Reenvía todos los mensajes JSON-RPC sin cambios, excepto la respuesta de
 * tools/list, a la que le quita la llave "$schema" de los esquemas. Sin esa
 * llave, el validador usa su dialecto por defecto (2020-12); las palabras clave
 * que usa el servidor (type, properties, required, items, enum...) son iguales
 * en ambos dialectos.
 *
 * Uso:  node mcp-schema-proxy.js <comando> [argumentos...]
 * Ej.:  node mcp-schema-proxy.js npx -y @modelcontextprotocol/server-filesystem@2026.8.31 C:\ruta
 */
const { spawn } = require("child_process");
const readline = require("readline");

const [cmd, ...args] = process.argv.slice(2);
if (!cmd) {
  console.error("Uso: node mcp-schema-proxy.js <comando> [argumentos...]");
  process.exit(1);
}

// En Windows "npx" es npx.cmd, por eso se necesita shell en ese sistema.
const hijo = spawn(cmd, args, {
  stdio: ["pipe", "pipe", "inherit"], // stderr (logs) pasa directo
  shell: process.platform === "win32",
});

function quitarSchema(obj) {
  if (Array.isArray(obj)) return obj.map(quitarSchema);
  if (obj && typeof obj === "object") {
    const limpio = {};
    for (const [k, v] of Object.entries(obj)) {
      if (k !== "$schema") limpio[k] = quitarSchema(v);
    }
    return limpio;
  }
  return obj;
}

// host -> servidor: se reenvía tal cual
process.stdin.pipe(hijo.stdin);

// servidor -> host: un mensaje JSON-RPC por línea
readline.createInterface({ input: hijo.stdout }).on("line", (linea) => {
  try {
    const msg = JSON.parse(linea);
    if (msg.result && Array.isArray(msg.result.tools)) {
      msg.result.tools = msg.result.tools.map((t) => ({
        ...t,
        inputSchema: quitarSchema(t.inputSchema),
        ...(t.outputSchema ? { outputSchema: quitarSchema(t.outputSchema) } : {}),
      }));
      console.error("[proxy] tools/list: se quitó $schema de", msg.result.tools.length, "herramientas");
    }
    process.stdout.write(JSON.stringify(msg) + "\n");
  } catch {
    process.stdout.write(linea + "\n"); // si no es JSON, se reenvía igual
  }
});

hijo.on("exit", (code) => process.exit(code ?? 0));
process.stdin.on("end", () => hijo.stdin.end());
