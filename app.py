from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from auth import token_obrigatorio, gerar_token
from dotenv import load_dotenv
import os
import json
from flasgger import Swagger

# Carrega variáveis do .env localmente
load_dotenv()

app = Flask(__name__)

# IMPORTANTE: Esta linha ajuda o Vercel a localizar sua instância do Flask
app = app 

# Configuração ÚNICA e COMPLETA do CORS para evitar "Falha na conexão"
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Configuração do Swagger
app.config["SWAGGER"] = {"openapi": "3.0.0"}
swagger = Swagger(app, template_file="openapi.yaml")

# Chave secreta para o JWT vinda das variáveis de ambiente
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

# =========================================
# FIREBASE / FIRESTORE
# =========================================
if os.getenv("VERCEL"):
    # No Vercel, usamos a string JSON salva nas Environment Variables
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise ValueError("FIREBASE_CREDENTIALS não encontrada no painel do Vercel")
    cred = credentials.Certificate(json.loads(cred_json))
else:
    # Localmente, usamos o arquivo físico
    cred = credentials.Certificate("firebase.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================================
# ROTA PRINCIPAL
# =========================================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "api": "Academia Pro",
        "version": "1.0",
        "autor": "Joaquim e Pedro",
        "status": "online"
    }), 200

# =========================================
# LOGIN
# =========================================
@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Envie os dados para login!"}), 400

    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if not usuario or not senha:
        return jsonify({"error": "Usuário e senha são obrigatórios!"}), 400

    if usuario == ADM_USUARIO and senha == ADM_SENHA:
        token = gerar_token(usuario)
        return jsonify({
            "message": "Login realizado com sucesso!",
            "token": token
        }), 200

    return jsonify({"error": "Usuário ou senha inválidos"}), 401

# =========================================
# ALUNOS - CRUD
# =========================================
@app.route("/alunos", methods=["GET"])
def get_alunos():
    alunos = []
    for doc in db.collection("alunos").stream():
        aluno = doc.to_dict()
        alunos.append(aluno)
    return jsonify(alunos), 200

@app.route("/alunos/<int:id>", methods=["GET"])
def get_aluno_by_id(id):
    docs = db.collection("alunos").where("id", "==", id).limit(1).get()
    doc = next(iter(docs), None)
    if not doc:
        return jsonify({"error": "Aluno(a) não encontrado"}), 404
    return jsonify(doc.to_dict()), 200

@app.route("/alunos", methods=["POST"])
@token_obrigatorio
def post_aluno():
    dados = request.get_json()
    nome = dados.get("nome")
    cpf = dados.get("cpf")
    status = dados.get("status")

    if not nome or not cpf or not status:
        return jsonify({"error": "nome, cpf e status são obrigatórios"}), 400

    try:
        contador_ref = db.collection("contador").document("controle_id")
        contador_doc = contador_ref.get()
        ultimo_id = contador_doc.to_dict().get("ultimo_id", 0)
        novo_id = ultimo_id + 1

        contador_ref.update({"ultimo_id": novo_id})

        db.collection("alunos").add({
            "id": novo_id,
            "nome": nome,
            "cpf": cpf,
            "status": status
        })

        return jsonify({"message": "Sucesso!", "id": novo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/alunos/<int:id>", methods=["PATCH"])
@token_obrigatorio
def alunos_patch(id):
    dados = request.get_json()
    try:
        docs = db.collection("alunos").where("id", "==", id).limit(1).get()
        doc = next(iter(docs), None)
        if not doc:
            return jsonify({"error": "Não encontrado"}), 404

        update_data = {k: v for k, v in dados.items() if k in ["nome", "cpf", "status"]}
        db.collection("alunos").document(doc.id).update(update_data)
        return jsonify({"message": "Atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/alunos/<int:id>", methods=["DELETE"])
@token_obrigatorio
def alunos_delete(id):
    try:
        docs = db.collection("alunos").where("id", "==", id).limit(1).get()
        doc = next(iter(docs), None)
        if not doc:
            return jsonify({"message": "Não encontrado!"}), 404
        db.collection("alunos").document(doc.id).delete()
        return jsonify({"message": "Excluído com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# CATRACA (REQUISIÇÃO SEM TOKEN)
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

# =========================================
# ERROS
# =========================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Página não encontrada!"}), 404

if __name__ == "__main__":
    app.run(debug=True)