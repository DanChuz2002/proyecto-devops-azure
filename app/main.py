from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def inicio():
    return jsonify({
        "proyecto": "Infraestructura DevOps en Azure",
        "mensaje": "Aplicacion desplegada correctamente en Microsoft Azure",
        "estado": "OK"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/info")
def info():
    return jsonify({
        "curso": "Sistemas Operativos II",
        "cloud": "Microsoft Azure",
        "servicios": [
            "Azure Virtual Machine",
            "Docker",
            "Docker Swarm",
            "GitHub Actions",
            "Docker Hub"
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)