from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List # CORRIGIDO: Importação do List adicionada

from app import crud, schemas, security, models # CORRIGIDO: Adicionado models no import
from app.database import get_db

router = APIRouter(tags=["Autenticação"])

# Configura o FastAPI para saber onde procurar o token (no cabeçalho Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# --- ROTA DE LOGIN (GERA O TOKEN) ---

@router.post("/auth/login", response_model=schemas.Token)
def login_para_obter_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # O formulário padrão do FastAPI usa 'username' para o campo de e-mail
    usuario = crud.get_usuario_by_email(db, email=form_data.username)
    
    if not usuario or not security.verificar_senha(form_data.password, usuario.senha_criptografada):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gera o Token JWT válido por 30 minutos
    tempo_expiracao = security.timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_acesso = security.criar_token_acesso(
        data={"sub": usuario.email, "role": usuario.role}, 
        expires_delta=tempo_expiracao
    )
    
    return {"access_token": token_acesso, "token_type": "bearer"}


# --- DEPENDÊNCIA DE SEGURANÇA (VALIDA O TOKEN) ---

def get_usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependência que valida o token JWT e retorna o usuário logado no banco"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de acesso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token usando a chave secreta e o algoritmo definidos em security.py
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    # Busca o usuário dono do token no banco de dados
    usuario = crud.get_usuario_by_email(db, email=token_data.email)
    if usuario is None:
        raise credentials_exception
        
    return usuario


# --- VALIDADOR DE PERMISSÕES POR PERFIL (ROLES) ---

class PermissaoPorRole:
    def __init__(self, roles_permitidos: List[str]):
        # Recebe a lista de quem pode acessar a rota (ex: ["admin", "recepcionista"])
        self.roles_permitidos = roles_permitidos

    def __call__(self, usuario_atual: models.Usuario = Depends(get_usuario_atual)):
        # Verifica se o perfil do usuário logado está na lista de autorizados
        if usuario_atual.role not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, # CORRIGIDO: Ajustado para o código HTTP correto (403)
                detail="Acesso negado. Seu perfil não tem permissão para acessar este recurso."
            )
        return usuario_atual