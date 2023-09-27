from typing import Optional
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret_key = "chavesecreta321"

# Função para gerar tokens JWT
def create_jwt_token(user_id: int) -> str:
    payload = {"user_id": user_id}
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

# Função para decodificar um token JWT e obter o user_id
def decode_jwt_token(token: str) -> int:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise Exception("Token JWT expirado")
    except jwt.InvalidTokenError:
        raise Exception("Token JWT inválido")

# Função para hashear uma senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
