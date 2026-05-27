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


@app.route("/")
def inicio():
    REQUEST_COUNTER.labels(endpoint="/").inc()
    return render_template("index.html")


@app.route("/health")
def health():
    REQUEST_COUNTER.labels(endpoint="/health").inc()
    return jsonify({
        "estado": "saludable",
        "servicio": "API Flask DevOps",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/info")
def info():
    REQUEST_COUNTER.labels(endpoint="/info").inc()
    return jsonify({
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
    })


@app.route("/api/status")
def api_status():
    REQUEST_COUNTER.labels(endpoint="/api/status").inc()
    return jsonify({
        "app": "online",
        "docker": "activo",
        "swarm": "activo",
        "database": "postgresql",
        "version": "2.0"
    })


@app.route("/api/visitas", methods=["GET", "POST"])
def api_visitas():
    REQUEST_COUNTER.labels(endpoint="/api/visitas").inc()

    try:
        inicializar_base_datos()
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        if request.method == "POST":
            data = request.get_json() or {}
            nombre = data.get("nombre", "Usuario")
            mensaje = data.get("mensaje", "Registro creado desde API REST")

            cursor.execute("""
                INSERT INTO visitas (nombre, mensaje)
                VALUES (%s, %s);
            """, (nombre, mensaje))

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

        return jsonify({
            "estado": "ok",
            "visitas": visitas
        })

    except Exception as error:
        return jsonify({
            "estado": "error",
            "detalle": str(error)
        }), 500


@app.route("/db")
def probar_base_datos():
    REQUEST_COUNTER.labels(endpoint="/db").inc()

    try:
        inicializar_base_datos()

        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

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
            LIMIT 5;
        """)

        registros = cursor.fetchall()

        cursor.close()
        conexion.close()

        return jsonify({
            "estado": "Conexion exitosa a PostgreSQL",
            "base_datos": DB_NAME,
            "ultimos_registros": registros
        })

    except Exception as error:
        return jsonify({
            "estado": "Error conectando a PostgreSQL",
            "detalle": str(error)
        }), 500


@app.route("/metrics")
def metrics():
    REQUEST_COUNTER.labels(endpoint="/metrics").inc()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)