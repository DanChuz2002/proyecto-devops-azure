from flask import Flask, jsonify, render_template, request
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "proyectodb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_PORT = os.getenv("DB_PORT", "5432")

REQUEST_COUNTER = Counter(
    "devops_app_requests_total",
    "Total de solicitudes recibidas por la aplicacion",
    ["endpoint"]
)


def obtener_conexion():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


def inicializar_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitas (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            mensaje VARCHAR(255),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conexion.commit()
    cursor.close()
    conexion.close()


def datos_health():
    return {
        "estado": "saludable",
        "servicio": "API Flask DevOps",
        "timestamp": datetime.now().isoformat()
    }


def datos_info():
    return {
        "proyecto": "Infraestructura DevOps en Azure",
        "cloud": "Microsoft Azure",
        "orquestador": "Docker Swarm",
        "registro": "Docker Hub",
        "cicd": "GitHub Actions",
        "base_datos": "PostgreSQL",
        "monitoreo": "Prometheus y Grafana",
        "seguridad": [
            "SSH con llave privada",
            "GitHub Secrets",
            "Docker Hub Token",
            "Escaneo de vulnerabilidades con Trivy"
        ]
    }


def datos_status():
    return {
        "app": "online",
        "docker": "activo",
        "swarm": "activo",
        "database": "postgresql",
        "version": "2.0"
    }


def obtener_visitas(insertar=False):
    inicializar_base_datos()

    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    if insertar:
        cursor.execute("""
            INSERT INTO visitas (nombre, mensaje)
            VALUES (%s, %s);
        """, ("Azure", "Conexion exitosa entre Flask y PostgreSQL"))
        conexion.commit()

    cursor.execute("""
        SELECT 
            id,
            nombre,
            mensaje,
            TO_CHAR(fecha, 'YYYY-MM-DD HH24:MI:SS') AS fecha
        FROM visitas
        ORDER BY id DESC
        LIMIT 10;
    """)

    visitas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return {
        "estado": "Conexion exitosa a PostgreSQL",
        "base_datos": DB_NAME,
        "visitas": visitas
    }


@app.route("/")
def inicio():
    REQUEST_COUNTER.labels(endpoint="/").inc()
    return render_template("index.html")


# APIs JSON
@app.route("/health")
def health():
    REQUEST_COUNTER.labels(endpoint="/health").inc()
    return jsonify(datos_health())


@app.route("/info")
def info():
    REQUEST_COUNTER.labels(endpoint="/info").inc()
    return jsonify(datos_info())


@app.route("/api/status")
def api_status():
    REQUEST_COUNTER.labels(endpoint="/api/status").inc()
    return jsonify(datos_status())


@app.route("/api/visitas", methods=["GET", "POST"])
def api_visitas():
    REQUEST_COUNTER.labels(endpoint="/api/visitas").inc()

    try:
        insertar = request.method == "POST"
        return jsonify(obtener_visitas(insertar=insertar))
    except Exception as error:
        return jsonify({
            "estado": "error",
            "detalle": str(error)
        }), 500


@app.route("/db")
def probar_base_datos():
    REQUEST_COUNTER.labels(endpoint="/db").inc()

    try:
        return jsonify(obtener_visitas(insertar=True))
    except Exception as error:
        return jsonify({
            "estado": "Error conectando a PostgreSQL",
            "detalle": str(error)
        }), 500


@app.route("/metrics")
def metrics():
    REQUEST_COUNTER.labels(endpoint="/metrics").inc()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# Paneles visuales bonitos
@app.route("/panel/health")
def panel_health():
    return render_template(
        "panel.html",
        titulo="Health Check",
        subtitulo="Estado general de la aplicación desplegada en Azure.",
        etiqueta="ONLINE",
        datos=datos_health()
    )


@app.route("/panel/info")
def panel_info():
    return render_template(
        "panel.html",
        titulo="Información del Proyecto",
        subtitulo="Tecnologías y componentes implementados.",
        etiqueta="INFO",
        datos=datos_info()
    )


@app.route("/panel/status")
def panel_status():
    return render_template(
        "panel.html",
        titulo="Estado de la API",
        subtitulo="Estado operativo de los servicios principales.",
        etiqueta="API",
        datos=datos_status()
    )


@app.route("/panel/db")
def panel_db():
    try:
        datos = obtener_visitas(insertar=True)
        etiqueta = "POSTGRESQL OK"
    except Exception as error:
        datos = {
            "estado": "Error conectando a PostgreSQL",
            "detalle": str(error)
        }
        etiqueta = "ERROR"

    return render_template(
        "panel.html",
        titulo="Base de Datos PostgreSQL",
        subtitulo="Validación de conexión, inserción y consulta de registros.",
        etiqueta=etiqueta,
        datos=datos
    )


@app.route("/panel/visitas")
def panel_visitas():
    try:
        datos = obtener_visitas(insertar=False)
        etiqueta = "REST API"
    except Exception as error:
        datos = {
            "estado": "Error consultando visitas",
            "detalle": str(error)
        }
        etiqueta = "ERROR"

    return render_template(
        "panel.html",
        titulo="API REST de Visitas",
        subtitulo="Consulta de registros almacenados en PostgreSQL.",
        etiqueta=etiqueta,
        datos=datos
    )


@app.route("/panel/metrics")
def panel_metrics():
    datos = {
        "estado": "Metricas disponibles",
        "endpoint_prometheus": "/metrics",
        "descripcion": "La aplicacion expone metricas compatibles con Prometheus.",
        "metricas_principales": [
            "devops_app_requests_total",
            "python_gc_objects_collected_total",
            "process_resident_memory_bytes"
        ]
    }

    return render_template(
        "panel.html",
        titulo="Métricas de la Aplicación",
        subtitulo="Endpoint utilizado por Prometheus para recolectar métricas.",
        etiqueta="METRICS",
        datos=datos
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)