from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.database import engine, Base, get_db
from app.routers import auth
# CORRIGIDO: Importações unificadas e limpas do módulo de autenticação
from app.routers.auth import get_usuario_atual, PermissaoPorRole

# Mantém você logado no Swagger mesmo atualizando a página com F5
app = FastAPI(
    title="Clinica Med Control - Agendamentos", 
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Ativa as rotas do arquivo auth.py
app.include_router(auth.router)

# Garante a criação das tabelas
Base.metadata.create_all(bind=engine)


# --- ROTAS DE USUÁRIO ---

@app.post("/usuarios/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED, tags=["Usuários"])
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_email(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(
            status_code=400, 
            detail="Este e-mail já está cadastrado no sistema."
        )
    return crud.criar_usuario(db=db, usuario=usuario)


# --- ROTAS DE AGENDAMENTO ---

@app.post("/agendamentos/", response_model=schemas.AgendamentoResponse, status_code=status.HTTP_201_CREATED, tags=["Agendamentos"])
def criar_agendamento(
    agendamento: schemas.AgendamentoCreate, 
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual) # Qualquer usuário logado pode criar
):
    """
    Cria um agendamento para o cliente logado. 
    O cliente_id é obtido automaticamente através do Token JWT enviado.
    """
    novo_agendamento = crud.criar_agendamento(db=db, agendamento=agendamento, cliente_id=usuario_atual.id)
    
    if not novo_agendamento:
        raise HTTPException(
            status_code=400, 
            detail="Horário indisponível. Já existe um agendamento ativo para este momento."
        )
    return novo_agendamento


# ALTERADO: Agora apenas usuários com a role 'admin' têm permissão de listar tudo
@app.get("/agendamentos/", response_model=List[schemas.AgendamentoResponse], tags=["Agendamentos"])
def listar_agendamentos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    # TRAVA AQUI: Substituímos o get_usuario_atual pelo validador do papel de Admin
    usuario_atual: models.Usuario = Depends(PermissaoPorRole(["admin"])) 
):
    """
    Retorna todos os agendamentos da clínica.
    Acesso restrito apenas para administradores.
    """
    return crud.listar_agendamentos(db=db, skip=skip, limit=limit)


@app.patch("/agendamentos/{agendamento_id}/cancelar", response_model=schemas.AgendamentoResponse, tags=["Agendamentos"])
def cancelar_consulta(
    agendamento_id: int,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual) # O cliente cancela o seu próprio horário
):
    """
    Cancela um agendamento ativo do cliente logado.
    Isso altera o status para 'cancelado' e libera o horário de volta para o sistema.
    """
    agendamento_atualizado = crud.cancelar_agendamento(
        db=db, 
        agendamento_id=agendamento_id, 
        cliente_id=usuario_atual.id
    )
    
    if not agendamento_atualizado:
        raise HTTPException(
            status_code=404, 
            detail="Agendamento não encontrado ou você não tem permissão para cancelá-lo."
        )
        
    return agendamento_atualizado


@app.get("/agendamentos/disponiveis", tags=["Agendamentos"])
def listar_vagas(data: str, db: Session = Depends(get_db)):
    """
    Retorna quais horários estão livres para agendamento em uma data específica.
    Formato esperado do parâmetro 'data': YYYY-MM-DD (Exemplo: 2026-05-30)
    """
    if len(data) != 10:
        raise HTTPException(
            status_code=400, 
            detail="Formato de data inválido. Use o padrão AAAA-MM-DD (ex: 2026-05-30)."
        )
        
    horarios_livres = crud.listar_horarios_disponiveis(db=db, data_busca=data)
    
    return {
        "data": data,
        "horarios_disponiveis": horarios_livres
    }


@app.get("/")
def home():
    return {
        "status": "API rodando perfeitamente", 
        "fase": "Fase 6 - Controle de Acesso por Perfil (RBAC) Pronto"
    }