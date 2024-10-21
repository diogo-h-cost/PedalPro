from connection.database import engine
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Float, func, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(11), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    criado = Column(DateTime, default=func.now(), nullable=False)

class Bike(Base):
    __tablename__ = 'bikes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tamanho = Column(Enum('pequeno', 'medio', 'grande'), nullable=False)
    modelo = Column(String(80), nullable=False)
    disponivel = Column(Boolean, nullable=False, default=True)

class Locacao(Base):
    __tablename__ = 'locacoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    bike_id = Column(Integer, ForeignKey('bikes.id', ondelete='CASCADE'), nullable=False)
    data_retirada = Column(DateTime, nullable=False)
    preco = Column(Float, nullable=False)

def create_tables():
    try:
        Base.metadata.create_all(engine)
        print("Tabelas criadas com sucesso.")
    except SQLAlchemyError as e:
        print(f"Erro ao criar tabelas: {e}")