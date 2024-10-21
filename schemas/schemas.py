from pydantic import BaseModel, field_validator
from datetime import datetime

# ----------------------------- geral

class Message(BaseModel):
    message: str

# ----------------------------- cliente

class UserEnt(BaseModel):
    nome: str
    telefone: str
    senha: str

class UserPub(BaseModel):
    id: int
    nome: str
    telefone: str

class UserList(BaseModel):
    users: list[UserPub]

# ----------------------------- bike

class BikeEnt(BaseModel):
    tamanho: str
    modelo: str

    @field_validator('tamanho')
    def validate_tamanho(cls, value):
        if value not in ('pequeno', 'medio', 'grande'):
            raise ValueError('Tamanho inválido, deve ser [pequeno], [medio] ou [grande]')
        return value

class BikePub(BaseModel):
    id: int
    tamanho: str
    modelo: str
    disponivel: bool

class BikeList(BaseModel):
    bikes: list[BikePub]

class BikeUpdt(BaseModel):
    tamanho: str
    modelo: str
    disponivel: bool

    @field_validator('tamanho')
    def validate_tamanho(cls, value):
        if value not in ('pequeno', 'medio', 'grande'):
            raise ValueError('Tamanho inválido, deve ser [pequeno], [medio] ou [grande]')
        return value

# ----------------------------- locacao

class LocacaoEnt(BaseModel):
    user_id: int
    bike_id: int
    data_retirada: datetime
    preco: float

class LocacaoFull(BaseModel):
    id: int
    user_id: int
    user_nome: str
    user_telefone: str
    bike_id: int
    bike_tamanho: str
    bike_modelo: str
    data_retirada: datetime
    preco: float

class LocacaoPub(BaseModel):
    id: int
    user_id: int
    bike_id: int
    data_retirada: datetime
    preco: float

class LocacaoList(BaseModel):
    locacoes: list[LocacaoPub]

class LocacaoUpdt(BaseModel):
    data_retirada: datetime
    preco: float