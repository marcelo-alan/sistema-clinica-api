from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

# ALTERADO: Mudamos para pbkdf2_sha256 que é nativo em Python puro e resolve o bug de bytes/plataforma do Windows
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Chave secreta para assinar o token
SECRET_KEY = "sua_chave_secreta_super_segura_para_o_projeto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verificar_senha(senha_pura: str, senha_criptografada: str) -> bool:
    """Verifica se a senha digitada bate com o hash salvo no banco"""
    return pwd_context.verify(str(senha_pura), senha_criptografada)

def gerar_hash_senha(senha: str) -> str:
    """Transforma a senha em um hash seguro e irreversível"""
    return pwd_context.hash(str(senha))

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Gera o Token JWT com tempo de expiração de 30 minutos"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt