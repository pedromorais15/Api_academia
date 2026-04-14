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

# Configuração robusta de CORS para evitar "Falha na conexão"
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
# FIREBASE / FIRESTORE
# =========================================
if os.getenv("VERCEL"):
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise ValueError("FIREBASE_CREDENTIALS não encontrada no Vercel")
    cred = credentials.Certificate(json.loads(cred_json))
else:
    # Busca o arquivo local conforme sua estrutura
    cred = credentials.Certificate("firebase.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================================
# ROTAS
# =========================================

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "api": "Academia Pro",
        "status": "online",
        "autor": "Joaquim e Pedro"
    }), 200

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados: return jsonify({"error": "Dados ausentes"}), 400
    
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if usuario == ADM_USUARIO and senha == ADM_SENHA:
        token = gerar_token(usuario)
        return jsonify({"message": "Sucesso", "token": token}), 200
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
        contador_ref = db.collection("contador").document("controle_id")
        ultimo_id = contador_ref.get().to_dict().get("ultimo_id", 0)
        novo_id = ultimo_id + 1
        contador_ref.update({"ultimo_id": novo_id})

        db.collection("alunos").add({
            "id": novo_id,
            "nome": dados.get("nome"),
            "cpf": dados.get("cpf"),
            "status": dados.get("status")
        })
        return jsonify({"id": novo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/alunos/<int:id>", methods=["PATCH"])
@token_obrigatorio
def alunos_patch(id):
    dados = request.get_json()
    docs = db.collection("alunos").where("id", "==", id).limit(1).get()
    doc = next(iter(docs), None)
    if not doc: return jsonify({"error": "Não encontrado"}), 404
    
    db.collection("alunos").document(doc.id).update(dados)
    return jsonify({"message": "Atualizado"}), 200

@app.route("/alunos/<int:id>", methods=["DELETE"])
@token_obrigatorio
def alunos_delete(id):
    docs = db.collection("alunos").where("id", "==", id).limit(1).get()
    doc = next(iter(docs), None)
    if not doc: return jsonify({"error": "Não encontrado"}), 404
    
    db.collection("alunos").document(doc.id).delete()
    return jsonify({"message": "Excluído"}), 200

# ROTA DA CATRACA
@app.route("/catraca", methods=["POST"])
def catraca():
    dados = request.get_json()
    if not dados or "cpf" not in dados:
        return jsonify({"error": "CPF obrigatório"}), 400

    docs = db.collection("alunos").where("cpf", "==", dados["cpf"]).limit(1).get()
    doc = next(iter(docs), None)

    if not doc:
        return jsonify({"status": "BLOQUEADO"}), 200

    aluno = doc.to_dict()
    return jsonify({"status": aluno.get("status", "BLOQUEADO")}), 200

# IMPORTANTE PARA VERCEL
app = app

if __name__ == "__main__":
    app.run(debug=True)