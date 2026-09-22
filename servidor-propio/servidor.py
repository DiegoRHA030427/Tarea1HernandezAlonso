"""
Servidor MCP propio - Tarea 1 (Desarrollo de Aplicaciones Moviles Nativas)
Autor: Diego Raymundo Hernandez Alonso - 7CV4

Expone las tres primitivas de servidor de MCP:
  - 2 herramientas (tools): contar_palabras, estadisticas_calificaciones
  - 1 recurso (resource):   info://tarea
  - 1 plantilla de prompt:  revisar_documento

Transporte: stdio (el cliente lo lanza como proceso hijo).
SDK oficial: mcp (Python) 2.x  ->  `FastMCP` ahora se llama `MCPServer`.
"""
import statistics

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("servidor-escom")


# ---------------------------------------------------------------- tools
@mcp.tool()
def contar_palabras(texto: str) -> dict:
    """Cuenta palabras, caracteres y lineas de un texto.

    Util para verificar la extension de un documento Markdown.
    """
    return {
        "palabras": len(texto.split()),
        "caracteres": len(texto),
        "lineas": len(texto.splitlines()) or (1 if texto else 0),
    }


@mcp.tool()
def estadisticas_calificaciones(calificaciones: list[float]) -> dict:
    """Calcula promedio, mediana, minimo, maximo y desviacion estandar
    de una lista de calificaciones (escala 0 a 10).
    """
    if not calificaciones:
        raise ToolError("La lista de calificaciones esta vacia.")
    fuera = [c for c in calificaciones if not 0 <= c <= 10]
    if fuera:
        raise ToolError(f"Calificaciones fuera del rango 0-10: {fuera}")
    return {
        "n": len(calificaciones),
        "promedio": round(statistics.mean(calificaciones), 2),
        "mediana": statistics.median(calificaciones),
        "minimo": min(calificaciones),
        "maximo": max(calificaciones),
        "desviacion_estandar": round(statistics.pstdev(calificaciones), 2),
        "aprobado": statistics.mean(calificaciones) >= 6,
    }


# ------------------------------------------------------------- resource
@mcp.resource("info://tarea")
def info_tarea() -> str:
    """Datos de la tarea a la que pertenece este servidor."""
    return (
        "Tarea 1 - MCP vs API y servidor de sistema de archivos\n"
        "Materia: Desarrollo de Aplicaciones Moviles Nativas (ESCOM-IPN)\n"
        "Alumno: Diego Raymundo Hernandez Alonso - Grupo 7CV4\n"
    )


# --------------------------------------------------------------- prompt
@mcp.prompt()
def revisar_documento(tema: str) -> str:
    """Plantilla para pedir una revision tecnica de un documento."""
    return (
        f"Revisa el documento sobre '{tema}'. Senala errores conceptuales, "
        "afirmaciones sin fuente y secciones incompletas. No reescribas el "
        "documento: devuelve una lista numerada de observaciones."
    )


if __name__ == "__main__":
    mcp.run()  # stdio por defecto
