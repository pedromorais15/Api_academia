from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from auth import token_obrigatorio, gerar_token
from dotenv import load_dotenv
import os
import json
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)

# Configuração de CORS completa para liberar o acesso do Front-End
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

app.config["SWAGGER"] = {"openapi": "3.0.0"}
swagger = Swagger(app, template_file="openapi.yaml")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

# =========================================
# CONEXÃO FIREBASE
# =========================================
if os.getenv("VERCEL"):
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise ValueError("Variável FIREBASE_CREDENTIALS não configurada no Vercel")
    cred = credentials.Certificate(json.loads(cred_json))
else:
    # Usa o arquivo local se estiver no seu computador
    cred = credentials.Certificate("firebase.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================================
# ROTAS DE ADMINISTRAÇÃO
# =========================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({"api": "Academia Pro", "status": "online"}), 200

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados: return jsonify({"error": "Sem dados"}), 400
    if dados.get("usuario") == ADM_USUARIO and dados.get("senha") == ADM_SENHA:
        return jsonify({"message": "Login OK", "token": gerar_token(dados.get("usuario"))}), 200
    return jsonify({"error": "Incorreto"}), 401

@app.route("/alunos", methods=["GET"])
def get_alunos():
    alunos = [doc.to_dict() for doc in db.collection("alunos").stream()]
    return jsonify(alunos), 200

@app.route("/alunos", methods=["POST"])
@token_obrigatorio
def post_aluno():
    dados = request.get_json()
    try:
        cont_ref = db.collection("contador").document("controle_id")
        novo_id = cont_ref.get().to_dict().get("ultimo_id", 0) + 1
        cont_ref.update({"ultimo_id": novo_id})
        db.collection("alunos").add({"id": novo_id, **dados})
        return jsonify({"id": novo_id}), 201
    except Exception as e: return jsonify({"error": str(e)}), 500

# =========================================
# ROTA DA CATRACA (REQUISIÇÃO JSON: CPF)
# =========================================
@app.route("/catraca", methods=["POST"])
def catraca():
    dados = request.get_json()
    if not dados or "cpf" not in dados:
        return jsonify({"error": "CPF é obrigatório"}), 400

    docs = db.collection("alunos").where("cpf", "==", dados["cpf"]).limit(1).get()
    doc = next(iter(docs), None)

    if not doc:
        return jsonify({"status": "BLOQUEADO"}), 200

    aluno = doc.to_dict()
    return jsonify({"status": aluno.get("status", "BLOQUEADO")}), 200

# EXPORTAÇÃO PARA O VERCEL
app = app

if __name__ == "__main__":
    app.run(debug=True)