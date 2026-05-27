from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_criptografada = Column(String, nullable=False)
    role = Column(String, default="cliente") # Pode ser 'cliente', 'medico', 'admin'

    # Relacionamento: Um usuário pode ter vários agendamentos vinculados
    agendamentos = relationship("Agendamento", back_populates="cliente")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_hora = Column(DateTime, nullable=False, index=True)
    servico = Column(String, nullable=False) # Ex: "Consulta Geral", "Cardiologia"
    status = Column(String, default="pendente") # 'pendente', 'confirmado', 'cancelado'

    # Permite acessar os dados do cliente direto pelo objeto agendamento (ex: agendamento.cliente.nome)
    cliente = relationship("Usuario", back_populates="agendamentos")