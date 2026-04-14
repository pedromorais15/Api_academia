import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app


# =========================================
# GERAR TOKEN JWT
# =========================================
def gerar_token(usuario):
    """
    Gera token JWT para autenticação do administrador.
    Expira em 1 hora.
    """
    payload = {
        "usuario": usuario,
        "perfil": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return token


# =========================================
# DECORATOR DE PROTEÇÃO
# =========================================
def token_obrigatorio(func):
    """
    Protege rotas privadas usando JWT.
    Exige header:
    Authorization: Bearer TOKEN
    """
    @wraps(func)
    def verificar_token(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token ausente. Faça login."}), 401

        partes = auth_header.split()

        if len(partes) != 2 or partes[0] != "Bearer":
            return jsonify({"error": "Cabeçalho Authorization inválido."}), 401

        token = partes[1]

        try:
            dados_token = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            # guarda os dados do usuário logado
            request.usuario_logado = dados_token

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado. Faça login novamente."}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido."}), 401

        return func(*args, **kwargs)

    return verificar_token