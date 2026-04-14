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

CORS(app, resources={r"/*": {"origins": "*"}})


app.config["SWAGGER"] = {
    "openapi": "3.0.0"}

swagger = Swagger(app, template_file="openapi.yaml")


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# No seu app.py, garanta que o CORS cubra o header Authorization
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

# =========================================
# FIREBASE / FIRESTORE
# =========================================
if os.getenv("VERCEL"):
    cred_json = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_json:
        raise ValueError("FIREBASE_CREDENTIALS não encontrada")
    cred = credentials.Certificate(json.loads(cred_json))
else:
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
        "api": "Academia",
        "version": "1.0",
        "autor": "Joaquim e Pedro"
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
# GET - LISTAR TODOS
# =========================================
@app.route("/alunos", methods=["GET"])
def get_alunos():
    alunos = []

    for doc in db.collection("alunos").stream():
        aluno = doc.to_dict()
        alunos.append(aluno)

    return jsonify(alunos), 200


# =========================================
# GET - POR ID
# =========================================
@app.route("/alunos/<int:id>", methods=["GET"])
def get_aluno_by_id(id):
    docs = db.collection("alunos").where("id", "==", id).limit(1).get()

    doc = next(iter(docs), None)

    if not doc:
        return jsonify({"error": "Aluno(a) não encontrado"}), 404

    return jsonify(doc.to_dict()), 200


# =========================================
# POST - ADICIONAR
# =========================================
@app.route("/alunos", methods=["POST"])
@token_obrigatorio
def post_aluno():
    dados = request.get_json()

    if not dados:
        return jsonify({"error": "Envie os dados!"}), 400

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

        return jsonify({
            "message": "Aluno adicionado com sucesso!",
            "id": novo_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# PUT - ALTERAÇÃO TOTAL
# =========================================
@app.route("/alunos/<int:id>", methods=["PUT"])
@token_obrigatorio
def alunos_put(id):
    dados = request.get_json()

    if not dados or "status" not in dados:
        return jsonify({"error": "status é obrigatório"}), 400

    try:
        docs = db.collection("alunos").where("id", "==", id).limit(1).get()
        doc = next(iter(docs), None)

        if not doc:
            return jsonify({"error": "Aluno(a) não encontrado"}), 404

        db.collection("alunos").document(doc.id).update({
            "status": dados["status"]
        })

        return jsonify({"message": "Aluno alterado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# PATCH - ALTERAÇÃO PARCIAL
# =========================================
@app.route("/alunos/<int:id>", methods=["PATCH"])
@token_obrigatorio
def alunos_patch(id):
    dados = request.get_json()

    if not dados:
        return jsonify({"error": "Envie os dados"}), 400

    try:
        docs = db.collection("alunos").where("id", "==", id).limit(1).get()
        doc = next(iter(docs), None)

        if not doc:
            return jsonify({"error": "Aluno(a) não encontrado"}), 404

        update_data = {}

        if "nome" in dados:
            update_data["nome"] = dados["nome"]

        if "cpf" in dados:
            update_data["cpf"] = dados["cpf"]

        if "status" in dados:
            update_data["status"] = dados["status"]

        db.collection("alunos").document(doc.id).update(update_data)

        return jsonify({"message": "Aluno(a) atualizado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# DELETE
# =========================================
@app.route("/alunos/<int:id>", methods=["DELETE"])
@token_obrigatorio
def alunos_delete(id):
    try:
        docs = db.collection("alunos").where("id", "==", id).limit(1).get()
        doc = next(iter(docs), None)

        if not doc:
            return jsonify({"message": "Aluno(a) não encontrado!"}), 404

        db.collection("alunos").document(doc.id).delete()

        return jsonify({"message": "Aluno(a) excluído com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================
# CATRACA
# =========================================
@app.route("/catraca", methods=["POST"])
def catraca():
    dados = request.get_json()

    if not dados or "cpf" not in dados:
        return jsonify({"error": "CPF é obrigatório"}), 400

    cpf = dados["cpf"]

    docs = db.collection("alunos").where("cpf", "==", cpf).limit(1).get()
    doc = next(iter(docs), None)

    if not doc:
        return jsonify({"status": "BLOQUEADO"}), 200

    aluno = doc.to_dict()

    return jsonify({
        "status": aluno.get("status", "BLOQUEADO")
    }), 200


# =========================================
# ERROS
# =========================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Página não encontrada!"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erro interno do servidor!"}), 500


if __name__ == "__main__":
    app.run(debug=True)
