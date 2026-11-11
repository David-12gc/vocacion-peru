
from flask import Flask, render_template, request
import json
import random
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ==========================================
# FAMILIAS PROFESIONALES
# ==========================================

FAMILIAS = [
    {
        "codigo": "ING",
        "nombre": "Ingenierías y tecnología",
        "areas": ["R", "I", "C"],
        "carreras": [
            "Ingeniería de Software",
            "Ingeniería de Sistemas",
            "Ingeniería Civil",
            "Ingeniería Industrial",
            "Ingeniería Mecatrónica"
        ]
    },
    {
        "codigo": "ADM",
        "nombre": "Ciencias administrativas y económicas",
        "areas": ["E", "C", "I"],
        "carreras": [
            "Administración de Empresas",
            "Economía",
            "Contabilidad",
            "Negocios Internacionales",
            "Marketing"
        ]
    },
    {
        "codigo": "SAL",
        "nombre": "Ciencias de la salud",
        "areas": ["S", "I"],
        "carreras": [
            "Medicina Humana",
            "Enfermería",
            "Nutrición",
            "Obstetricia",
            "Odontología",
            "Psicología"
        ]
    },
    {
        "codigo": "SOC",
        "nombre": "Ciencias sociales y humanidades",
        "areas": ["S", "E", "A"],
        "carreras": [
            "Derecho",
            "Sociología",
            "Antropología",
            "Historia",
            "Trabajo Social"
        ]
    },
    {
        "codigo": "ART",
        "nombre": "Arte, diseño y comunicación",
        "areas": ["A", "I"],
        "carreras": [
            "Diseño Gráfico",
            "Arquitectura",
            "Comunicación Audiovisual",
            "Artes Visuales",
            "Publicidad"
        ]
    },
    {
        "codigo": "NAT",
        "nombre": "Ciencias naturales y ambientales",
        "areas": ["I", "R"],
        "carreras": [
            "Biología",
            "Química",
            "Física",
            "Ingeniería Ambiental",
            "Geología"
        ]
    },
    {
        "codigo": "EDU",
        "nombre": "Educación",
        "areas": ["S", "A", "E"],
        "carreras": [
            "Educación Inicial",
            "Educación Primaria",
            "Educación Secundaria",
            "Educación Especial"
        ]
    },
    {
        "codigo": "AGR",
        "nombre": "Ciencias agrarias y veterinarias",
        "areas": ["R", "I", "S"],
        "carreras": [
            "Agronomía",
            "Medicina Veterinaria",
            "Ingeniería Agrícola",
            "Zootecnia",
            "Ingeniería Forestal"
        ]
    }
]


# ==========================================
# ÁREAS RIASEC
# ==========================================

NOMBRES_AREAS = {
    "R": "Realista",
    "I": "Investigativa",
    "A": "Artística",
    "S": "Social",
    "E": "Emprendedora",
    "C": "Convencional"
}


def convertir_porcentaje(puntuacion):
    """
    Convierte una escala de 1 a 5
    en una escala normalizada de 0 a 100.
    """

    porcentaje = ((puntuacion - 1) / 4) * 100

    return max(0, min(100, round(porcentaje)))


# ==========================================
# CARGAR ARCHIVOS JSON
# ==========================================

def cargar_json(nombre_archivo):

    ruta = os.path.join(
        BASE_DIR,
        "data",
        nombre_archivo
    )

    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}"
        )

    with open(
        ruta,
        "r",
        encoding="utf-8-sig"
    ) as archivo:

        return json.load(archivo)


def cargar_preguntas():

    preguntas = cargar_json("preguntas.json")

    if not isinstance(preguntas, list) or not preguntas:
        raise ValueError(
            "El banco de preguntas no es válido."
        )

    return preguntas


# ==========================================
# CARGAR UNIVERSIDADES
# ==========================================

def cargar_universidades():

    universidades = cargar_json("universidades.json")

    if not isinstance(universidades, list):
        raise ValueError(
            "El JSON debe contener una lista."
        )

    print("\n========== DIAGNÓSTICO UNIVERSIDADES ==========")

    print(
        "Universidades encontradas:",
        len(universidades)
    )

    for universidad in universidades:

        print("\nUNIVERSIDAD:", universidad.get("nombre"))

        sedes = universidad.get("sedes", [])

        if not sedes:
            print("  No tiene sedes registradas.")

        for sede in sedes:

            programas = sede.get("programas", {})

            print(
                "  SEDE:",
                sede.get("nombre")
            )

            print(
                "  FAMILIAS:",
                list(programas.keys())
            )

    print("\n===============================================\n")

    return universidades


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    return render_template("index.html")


# ==========================================
# CUESTIONARIO
# ==========================================

@app.route("/test")
def test():

    preguntas = cargar_preguntas()

    cantidad = min(50, len(preguntas))

    seleccionadas = random.sample(
        preguntas,
        cantidad
    )

    return render_template(
        "test.html",
        preguntas=seleccionadas
    )


# ==========================================
# RESULTADOS
# ==========================================

@app.route("/resultado", methods=["POST"])
def resultado():

    areas = ["R", "I", "A", "S", "E", "C"]

    puntajes = {
        area: 0 for area in areas
    }

    cantidades = {
        area: 0 for area in areas
    }

    # RECOPILAR RESPUESTAS

    for clave, valor in request.form.items():

        if not clave.startswith("respuesta_"):
            continue

        identificador = clave.replace(
            "respuesta_", ""
        )

        area = request.form.get(
            f"area_{identificador}"
        )

        if area not in areas:
            return "Área vocacional inválida.", 400

        try:
            puntuacion = int(valor)

        except (ValueError, TypeError):
            return "Respuesta inválida.", 400

        if puntuacion not in range(1, 6):
            return "Puntuación fuera de rango.", 400

        puntajes[area] += puntuacion
        cantidades[area] += 1

    if sum(cantidades.values()) == 0:
        return "No se recibieron respuestas.", 400

    # CALCULAR PROMEDIOS

    promedios = {}

    for area in areas:

        if cantidades[area] > 0:

            promedios[area] = (
                puntajes[area] / cantidades[area]
            )

        else:

            promedios[area] = 0

    # PREPARAR RESULTADOS RIASEC

    areas_resultado = []

    for area in areas:

        areas_resultado.append({

            "codigo": area,

            "nombre": NOMBRES_AREAS[area],

            "promedio": round(promedios[area], 2),

            "porcentaje": convertir_porcentaje(
                promedios[area]
            )

        })

    # CARGAR UNIVERSIDADES

    universidades = cargar_universidades()

    recomendaciones = []

    # PROCESAR CADA FAMILIA

    for familia in FAMILIAS:

        valores = [
            promedios[area]
            for area in familia["areas"]
        ]

        compatibilidad = (
            sum(valores) / len(valores)
        )

        porcentaje = convertir_porcentaje(
            compatibilidad
        )

        universidades_familia = []

        # RECORRER UNIVERSIDADES

        for universidad in universidades:

            sedes = universidad.get("sedes", [])

            # COMPATIBILIDAD CON EL FORMATO ANTIGUO

            if not sedes and "programas" in universidad:

                sedes = [{
                    "nombre": universidad.get(
                        "campus", "Sede no especificada"
                    ),
                    "region": universidad.get(
                        "region", "No especificada"
                    ),
                    "url": universidad.get("url", ""),
                    "programas": universidad.get(
                        "programas", {}
                    )
                }]

            # RECORRER CADA SEDE

            for sede in sedes:

                programas = sede.get(
                    "programas", {}
                )

                carreras_sede = programas.get(
                    familia["codigo"], []
                )

                if not carreras_sede:
                    continue

                universidades_familia.append({

                    "nombre": universidad.get("nombre"),

                    "tipo": universidad.get(
                        "tipo", "No especificado"
                    ),

                    "region": sede.get(
                        "region", "No especificada"
                    ),

                    "campus": sede.get(
                        "nombre", "Sede no especificada"
                    ),

                    "url": sede.get(
                        "url",
                        universidad.get("url", "")
                    ),

                    "carreras": carreras_sede

                })

        print(
            f"Familia {familia['codigo']}: "
            f"{len(universidades_familia)} sedes encontradas."
        )

        recomendaciones.append({

            "codigo": familia["codigo"],

            "nombre": familia["nombre"],

            "carreras": familia["carreras"],

            "compatibilidad": round(compatibilidad, 2),

            "porcentaje": porcentaje,

            "universidades": universidades_familia

        })

    # ORDENAR RESULTADOS

    recomendaciones.sort(
        key=lambda item: item["compatibilidad"],
        reverse=True
    )

    mejores = recomendaciones[:5]

    return render_template(
        "resultado.html",
        resultados=mejores,
        areas_resultado=areas_resultado
    )


# ==========================================
# INICIAR SERVIDOR
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
