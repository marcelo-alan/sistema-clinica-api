from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ----------------------------------------
# SCHEMAS DE USUÁRIO
# ----------------------------------------

# Dados básicos que todo usuário tem (comum para criação e leitura)
class UsuarioBase(BaseModel):
    nome: str
    email: str # Se quiser validação estrita de e-mail, pode usar EmailStr depois
    role: Optional[str] = "cliente"

# Dados que a API recebe quando alguém se cadastra (precisa da senha)
class UsuarioCreate(UsuarioBase):
    password: str

# Dados que a API devolve quando alguém consulta um usuário (nunca devolvemos a senha por segurança!)
class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True # Antigo orm_mode=True, permite ler modelos do SQLAlchemy


# ----------------------------------------
# SCHEMAS DE AGENDAMENTO
# ----------------------------------------

# Dados básicos para criar um agendamento
class AgendamentoCreate(BaseModel):
    data_hora: datetime
    servico: str

# Dados que a API retorna ao consultar um agendamento
class AgendamentoResponse(BaseModel):
    id: int
    cliente_id: int
    data_hora: datetime
    servico: str
    status: str
    # Inclui os dados simplificados do cliente dono do agendamento
    cliente: UsuarioResponse 

    class Config:
        from_attributes = True


# ----------------------------------------
# SCHEMAS DE AUTENTICAÇÃO (JWT)
# ----------------------------------------

# ADICIONADO: O formato do token que a API devolve no login bem-sucedido
class Token(BaseModel):
    access_token: str
    token_type: str

# ADICIONADO: Os dados que ficam guardados de forma criptografada dentro do token
class TokenData(BaseModel):
    email: Optional[str] = None