from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
# IMPORTANTE: Importando a função de criptografia real do arquivo que você criou
from app.security import gerar_hash_senha 

# --- Operações de Usuário ---

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    # Alterado: Agora a senha passa pelo bcrypt antes de ir para o banco de dados
    senha_segura = gerar_hash_senha(usuario.password)
    
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_criptografada=senha_segura, # Salvando o hash seguro e criptografado
        role=usuario.role
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# --- Operações de Agendamento ---

def criar_agendamento(db: Session, agendamento: schemas.AgendamentoCreate, cliente_id: int):
    # REGRA DE NEGÓCIO: Verifica se já existe agendamento ativo exatamente no mesmo horário
    horario_ocupado = db.query(models.Agendamento).filter(
        models.Agendamento.data_hora == agendamento.data_hora,
        models.Agendamento.status != "cancelado"
    ).first()
    
    if horario_ocupado:
        return None # Retorna None indicando conflito de horário
        
    db_agendamento = models.Agendamento(
        data_hora=agendamento.data_hora,
        servico=agendamento.servico,
        cliente_id=cliente_id
    )
    db.add(db_agendamento)
    db.commit()
    db.refresh(db_agendamento)
    return db_agendamento

def listar_agendamentos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Agendamento).offset(skip).limit(limit).all()

def cancelar_agendamento(db: Session, agendamento_id: int, cliente_id: int):
    """
    Busca o agendamento pelo ID e garante que ele pertence ao cliente logado.
    Se encontrar, muda o status para 'cancelado'.
    """
    db_agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.cliente_id == cliente_id # Trava de segurança: um cliente não cancela o horário do outro
    ).first()
    
    if db_agendamento:
        db_agendamento.status = "cancelado"
        db.commit()
        db.refresh(db_agendamento)
        return db_agendamento
        
    return None

def listar_horarios_disponiveis(db: Session, data_busca: str):
    """
    Gera uma lista de horários das 08:00 às 17:00 e remove
    aqueles que já possuem um agendamento ativo para o dia informado.
    """
    # 1. Define a lista de horários padrão que a clínica atende (de hora em hora)
    horarios_padrao = [
        "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00"
    ]
    
    # 2. Busca no banco todos os agendamentos daquela data que NÃO estão cancelados
    # Usamos o 'like' para buscar pela string da data (ex: '2026-05-30%')
    agendamentos_do_dia = db.query(models.Agendamento).filter(
        models.Agendamento.data_hora.like(f"{data_busca}%"),
        models.Agendamento.status != "cancelado"
    ).all()
    
    # 3. Extrai apenas a hora e minuto (HH:MM) dos agendamentos que já existem
    horarios_ocupados = []
    for agendamento in agendamentos_do_dia:
        # Pega a parte do tempo do objeto datetime (HH:MM)
        hora_formatada = agendamento.data_hora.strftime("%H:%M")
        horarios_ocupados.append(hora_formatada)
        
    # 4. Filtra a lista padrão removendo os horários que estão ocupados
    horarios_livres = [hora for hora in horarios_padrao if hora not in horarios_ocupados]
    
    return horarios_livres