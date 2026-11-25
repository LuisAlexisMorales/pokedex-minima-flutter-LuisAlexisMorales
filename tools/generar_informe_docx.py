r"""Genera el cuerpo del informe de la Práctica 2 (Pokédex mínima en Flutter).

Con USAR_PORTADA=1 se omite el título y los datos de portada: la portada
oficial se inserta como primera página con Word (ver tools/insertar_portada.ps1).
"""
import os
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

root = Path(__file__).resolve().parents[1]
evidencias = root / "evidencias"
doc = Document()

estilo = doc.styles["Normal"]
estilo.font.name = "Calibri"
estilo.font.size = Pt(10.5)


def parrafo(texto, negrita=False):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.bold = negrita
    return p


def tabla(encabezados, filas, anchos=None):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = texto
        for run in celda.paragraphs[0].runs:
            run.bold = True
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = texto
    if anchos:
        for fila in t.rows:
            for i, ancho in enumerate(anchos):
                fila.cells[i].width = Inches(ancho)
    doc.add_paragraph()
    return t


def codigo(texto):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    run = p.add_run(texto)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    return p


def figura(archivo, titulo, descripcion):
    doc.add_heading(titulo, level=2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(evidencias / archivo), width=Inches(6.0))
    p = doc.add_paragraph()
    p.add_run("Descripción: ").bold = True
    p.add_run(descripcion)


# ---------------------------------------------------------------- portada
if os.getenv("USAR_PORTADA") != "1":
    doc.add_heading("Práctica 2: Pokédex mínima en Flutter", 0)
    parrafo("Desarrollo de Aplicaciones Móviles · Unidad 4")
    tabla(
        ["Dato", "Valor"],
        [
            ["Integrante", "Luis Alexis Morales José"],
            ["Grupo", "7US"],
            ["Docente", "Josué Israel Vásquez Martínez"],
            ["Fecha", "24 de noviembre de 2026"],
        ],
        [1.4, 4.9],
    )

doc.add_heading("Objetivo", level=1)
parrafo(
    "Completar una aplicación Flutter que consulta PokéAPI, convierte la respuesta JSON "
    "en un objeto de Dart y muestra en pantalla el nombre, el número, la imagen y los "
    "tipos de un Pokémon, atendiendo los estados de carga y error del FutureBuilder."
)

doc.add_heading("1. Preparación del proyecto", level=1)
tabla(
    ["Elemento", "Acción / resultado"],
    [
        ["Repositorio base", "git clone https://github.com/nallely-lopez/pokedex_minima.git"],
        ["Ubicación", "C:\\Users\\moral\\StudioProjects\\pokedex_minima"],
        ["Dependencias", "flutter pub get (paquete http ya declarado en pubspec.yaml)"],
        ["Flutter / Dart", "Flutter 3.47.0 · Dart 3.13.0"],
        ["Ajuste necesario", "sdk: ^3.13.2 → ^3.13.0 en pubspec.yaml (el Flutter instalado trae Dart 3.13.0)"],
        ["Servicio remoto", "https://pokeapi.co/api/v2/pokemon/pikachu responde HTTP 200"],
        ["Ejecución", "flutter build web --debug y servidor estático local en 127.0.0.1:8083"],
    ],
    [1.5, 4.8],
)
parrafo(
    "La guía indica que el modelo, el servicio y la pantalla llegan con tres TODO. "
    "Se conservaron las firmas, los nombres de archivo y la estructura original; "
    "únicamente se completaron esos puntos y se añadió el reto opcional."
)

doc.add_heading("2. TODO 1 — modelo Pokemon.fromJson", level=1)
parrafo(
    "En lib/models/pokemon.dart se leen los cuatro atributos. id y nombre vienen directo "
    "del JSON; la imagen sigue la ruta sprites → other → official-artwork → front_default "
    "(con ?? '' para evitar un valor nulo) y tipos se construye recorriendo json['types'] "
    "y tomando ['type']['name'] de cada elemento."
)
codigo(
    "factory Pokemon.fromJson(Map<String, dynamic> json) {\n"
    "  return Pokemon(\n"
    "    id: json['id'] as int,\n"
    "    nombre: json['name'] as String,\n"
    "    imagen: json['sprites']['other']['official-artwork']['front_default'] ?? '',\n"
    "    tipos: [for (final t in json['types']) t['type']['name'] as String],\n"
    "  );\n"
    "}"
)

doc.add_heading("3. TODO 2 — petición a PokéAPI", level=1)
parrafo(
    "En lib/services/pokeapi_service.dart se arma la URL con Uri.parse, se normaliza el "
    "texto a minúsculas y sin espacios, se espera http.get(url) y se revisa statusCode: "
    "200 devuelve Pokemon.fromJson(jsonDecode(respuesta.body)), 404 lanza "
    "«No se encontró el Pokémon» y cualquier otro código muestra el código recibido."
)
codigo(
    "final url = Uri.parse(\n"
    "  'https://pokeapi.co/api/v2/pokemon/${nombre.toLowerCase().trim()}',\n"
    ");\n"
    "final respuesta = await http.get(url);\n\n"
    "if (respuesta.statusCode == 200) {\n"
    "  final datos = jsonDecode(respuesta.body) as Map<String, dynamic>;\n"
    "  return Pokemon.fromJson(datos);\n"
    "}\n"
    "if (respuesta.statusCode == 404) {\n"
    "  throw Exception('No se encontró el Pokémon');\n"
    "}\n"
    "throw Exception('Error al consultar PokéAPI (código ${respuesta.statusCode})');"
)

doc.add_heading("4. TODO 3 — estados del FutureBuilder", level=1)
tabla(
    ["Estado", "Interfaz mostrada"],
    [
        ["ConnectionState.waiting", "CircularProgressIndicator centrado"],
        ["snapshot.hasError", "Icono de error y el mensaje de snapshot.error (sin el prefijo «Exception:»)"],
        ["Sin datos", "Texto «Sin datos» como caso defensivo"],
        ["snapshot.hasData", "Imagen, texto «N.º id · nombre», Chip por tipo y altura/peso del reto"],
    ],
    [2.0, 4.3],
)
parrafo(
    "Además se añadió un errorBuilder en Image.network para que una imagen no disponible "
    "no rompa la pantalla. El botón Buscar y el campo de texto son los del proyecto base."
)

doc.add_heading("5. Reto opcional — altura y peso", level=1)
parrafo(
    "PokéAPI entrega height en decímetros y weight en hectogramos. En el modelo se "
    "agregaron altura y peso (double) y se dividen entre 10 para mostrar metros y "
    "kilogramos. La pantalla los formatea con toStringAsFixed(1)."
)
codigo(
    "altura: ((json['height'] as num?) ?? 0) / 10, // metros\n"
    "peso:   ((json['weight'] as num?) ?? 0) / 10, // kilogramos"
)

doc.add_page_break()
doc.add_heading("6. Evidencias", level=1)
figura(
    "figura_1_pikachu.png",
    "Figura 1. Búsqueda de pikachu por nombre (paso 5)",
    "Aparece la imagen oficial, el número 25, el tipo electric y, del reto, 0.4 m y 6.0 kg.",
)
figura(
    "figura_2_error.png",
    "Figura 2. Nombre mal escrito (paso 5)",
    "Al buscar «pikachuu» se muestra «No se encontró el Pokémon» y la aplicación permanece abierta.",
)
figura(
    "figura_3_numero_6.png",
    "Figura 3. Búsqueda por número y reto",
    "Al buscar 6 se muestra charizard, sus tipos fire y flying, 1.7 m y 90.5 kg.",
)

doc.add_heading("7. Comprobaciones finales", level=1)
tabla(
    ["Comprobación", "Resultado"],
    [
        ["Buscar pikachu", "Imagen, N.º 25, tipo electric, 0.4 m y 6.0 kg"],
        ["Buscar por número 6", "N.º 6 · charizard, tipos fire y flying, 1.7 m y 90.5 kg"],
        ["Nombre mal escrito", "Mensaje «No se encontró el Pokémon»; la app no se cierra"],
        ["Prueba unitaria", "flutter test: 1/1 (Pokemon.fromJson lee id, nombre, imagen y tipos)"],
        ["Analizador", "flutter analyze: No issues found!"],
        ["Compilación web", "flutter build web --debug correcto"],
    ],
    [2.1, 4.2],
)

doc.add_heading("8. Conclusión", level=1)
parrafo(
    "La práctica reforzó el flujo visto en JSON local: un modelo con fromJson, una función "
    "asíncrona y un FutureBuilder. La única diferencia fue la fuente de los datos, que en "
    "este caso vino de una petición HTTP a PokéAPI. El manejo explícito de los tres estados "
    "evita pantallas vacías y confirma que un error de búsqueda no debe cerrar la aplicación."
)

destino = root / os.getenv("NOMBRE_SALIDA", "CUERPO_INFORME.docx")
doc.save(destino)
print(destino)
