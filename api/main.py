from connection.database import create_db, get_session
from fastapi import Depends, FastAPI, HTTPException
from http import HTTPStatus
from models.tables import Bike, create_tables, Locacao, User
from schemas.schemas import BikeEnt, BikeList, BikeUpdt, BikePub, LocacaoEnt, LocacaoFull, LocacaoList, LocacaoUpdt, Message, UserEnt, UserList, UserPub
from sqlalchemy import select, and_
from security.hashing import get_password
from sms.twilio_sms import send_sms

# ----------------------------- banco + tabelas

create_db()

create_tables()

# ----------------------------- api

app = FastAPI()

# ----------------------------- raiz

@app.get("/", tags=["Raiz"])
def root():
    return {
        "message": "Welcome to the PedalPro API!",
        "version": "1.0.0"
    }

# ----------------------------- cliente

@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPub, tags=["User"])
def create_user(user: UserEnt, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(User.telefone == user.telefone)
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Phone already exists'
        )

    db_user = User(
        nome = user.nome,
        telefone = user.telefone,
        senha = get_password(user.senha)
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

@app.get('/users/', response_model=UserList, tags=["User"])
def read_all_users(ini: int = 0, limit: int = 10, session=Depends(get_session)):
    users = session.scalars(
        select(User).limit(limit).offset(ini)
    )
    return {'users': users}

@app.get('/users/{user_id}', response_model=UserPub, tags=["User"])
def read_user(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(User.id == user_id)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found"
        )

    return db_user

@app.put('/users/{user_id}', response_model=UserPub, tags=["User"])
def update_user(user_id: int, user: UserEnt, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(User.id == user_id)
    )

    if not db_user:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "User not found"
        )

    db_user.nome = user.nome
    db_user.telefone = user.telefone
    db_user.senha = get_password(user.senha)

    session.commit()
    session.refresh(db_user)

    return db_user

@app.delete('/users/{user_id}', response_model=Message, tags=["User"])
def delete_user(user_id: int, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where(User.id == user_id)
    )

    if not db_user:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "User not found"
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted'}

# ----------------------------- bike

@app.post('/bikes/', status_code=HTTPStatus.CREATED, response_model=BikePub, tags=["Bike"])
def create_bike(bike: BikeEnt, session=Depends(get_session)):
    db_bike = session.scalar(
        select(Bike).where(
            and_(
                Bike.tamanho == bike.tamanho,
                Bike.modelo == bike.modelo
            )
        )
    )

    if db_bike:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Bike already exists'
        )

    db_bike = Bike(
        tamanho = bike.tamanho,
        modelo = bike.modelo
    )

    session.add(db_bike)
    session.commit()
    session.refresh(db_bike)

    return db_bike

@app.get('/bikes/', response_model=BikeList, tags=["Bike"])
def read_all_bikes(ini: int = 0, limit: int = 10, session=Depends(get_session)):
    bikes = session.scalars(
        select(Bike).limit(limit).offset(ini)
    )
    return {'bikes': bikes}

@app.get('/bikes/{bike_id}', response_model=BikePub, tags=["Bike"])
def read_bike(bike_id: int, session=Depends(get_session)):
    db_bike = session.scalar(
        select(Bike).where(Bike.id == bike_id)
    )

    if not db_bike:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Bike not found"
        )

    return db_bike

@app.put('/bikes/{bike_id}', response_model=BikePub, tags=["Bike"])
def update_bike(bike_id: int, bike: BikeUpdt, session=Depends(get_session)):
    db_bike = session.scalar(
        select(Bike).where(Bike.id == bike_id)
    )

    if not db_bike:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Bike not found"
        )

    db_bike.tamanho = bike.tamanho
    db_bike.modelo = bike.modelo
    db_bike.disponivel = bike.disponivel

    session.commit()
    session.refresh(db_bike)

    return db_bike

@app.delete('/bikes/{bike_id}', response_model=Message, tags=["Bike"])
def delete_bike(bike_id: int, session=Depends(get_session)):
    db_bike = session.scalar(
        select(Bike).where(Bike.id == bike_id)
    )

    if not db_bike:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Bike not found"
        )

    session.delete(db_bike)
    session.commit()

    return {'message': 'Bike deleted'}

# ----------------------------- locacao

@app.post('/locacoes/', status_code=HTTPStatus.CREATED, response_model=LocacaoFull, tags=["Locacao"])
def create_locacao(locacao: LocacaoEnt, session=Depends(get_session)):
    # Verificação se o usuário existe
    db_user = session.scalar(
        select(User).where(
            User.id == locacao.user_id
        )
    )
    if not db_user:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "User not found"
        )

    # Verificação se a bike existe
    db_bike = session.scalar(
        select(Bike).where(
            Bike.id == locacao.bike_id
        )
    )
    if not db_bike:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Bike not found"
        )

    # Verificação se a bike está disponível
    if not db_bike.disponivel:
        raise HTTPException(
            status_code = HTTPStatus.CONFLICT,
            detail = 'Bike is currently rented'
        )

    # Verificação de conflito de locação para a mesma data
    conflit_locacao = session.scalar(
        select(Locacao).where(
            and_(
                Locacao.bike_id == locacao.bike_id,
                Locacao.data_retirada == locacao.data_retirada
            )
        )
    )
    if conflit_locacao:
        raise HTTPException(
            status_code = HTTPStatus.CONFLICT,
            detail = "Bike is already rented for the selected date and time"
        )

    # Verificação se a locação já existe para esse usuário e essa bike
    db_locacao = session.scalar(
        select(Locacao).where(
            and_(
                Locacao.user_id == locacao.user_id,
                Locacao.bike_id == locacao.bike_id
            )
        )
    )
    if db_locacao:
        raise HTTPException(
            status_code = HTTPStatus.BAD_REQUEST,
            detail = 'Locacao already exists'
        )

    db_locacao = Locacao(
        user_id = locacao.user_id,
        bike_id = locacao.bike_id,
        data_retirada = locacao.data_retirada,
        preco = locacao.preco
    )

    session.add(db_locacao)
    session.commit()
    session.refresh(db_locacao)

    data = db_locacao.data_retirada
    data_formt = data.strftime("%H:%M %d/%m/%y")

    msg = f"""Olá {db_user.nome} sua locação foi confirmada!
---------------------------|
Bicicleta: {db_bike.modelo}
Tamanho: {db_bike.tamanho}
---------------------------|
Data: {data_formt}
Valor: R${db_locacao.preco}"""
    number = f"+55{db_user.telefone}"

    send_sms(msg, number)

    return {
        "id": db_locacao.id,
        "user_id": db_locacao.user_id,
        "user_nome": db_user.nome,
        "user_telefone": db_user.telefone,
        "bike_id": db_locacao.bike_id,
        "bike_tamanho": db_bike.tamanho,
        "bike_modelo": db_bike.modelo,
        "data_retirada": db_locacao.data_retirada,
        "preco": db_locacao.preco
    }

@app.get('/locacoes/', response_model=LocacaoList, tags=["Locacao"])
def read_all_locacoes(ini: int = 0, limit: int = 10, session=Depends(get_session)):
    locacoes = session.scalars(
        select(Locacao).limit(limit).offset(ini)
    )
    return {'locacoes': locacoes}

@app.get('/locacoes/{locacao_id}', response_model=LocacaoFull, tags=["Locacao"])
def read_locacao(locacao_id: int, session=Depends(get_session)):
    db_locacao = session.scalar(
        select(Locacao).where(Locacao.id == locacao_id)
    )

    if not db_locacao:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Locacao not found"
        )

    db_user = session.scalar(
        select(User).where(User.id == db_locacao.user_id)
    )

    db_bike = session.scalar(
        select(Bike).where(Bike.id == db_locacao.bike_id)
    )

    return {
        "id": db_locacao.id,
        "user_id": db_locacao.user_id,
        "user_nome": db_user.nome,
        "user_telefone": db_user.telefone,
        "bike_id": db_locacao.bike_id,
        "bike_tamanho": db_bike.tamanho,
        "bike_modelo": db_bike.modelo,
        "data_retirada": db_locacao.data_retirada,
        "preco": db_locacao.preco
    }

@app.put('/locacoes/{locacao_id}', response_model=LocacaoFull, tags=["Locacao"])
def update_locacao(locacao_id: int, locacao: LocacaoUpdt, session=Depends(get_session)):
    db_locacao = session.scalar(
        select(Locacao).where(Locacao.id == locacao_id)
    )

    if not db_locacao:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Locacao not found"
        )

    db_locacao.data_retirada = locacao.data_retirada
    db_locacao.preco = locacao.preco

    session.commit()
    session.refresh(db_locacao)

    db_user = session.scalar(
        select(User).where(User.id == db_locacao.user_id)
    )

    db_bike = session.scalar(
        select(Bike).where(Bike.id == db_locacao.bike_id)
    )

    return {
        "id": db_locacao.id,
        "user_id": db_locacao.user_id,
        "user_nome": db_user.nome,
        "user_telefone": db_user.telefone,
        "bike_id": db_locacao.bike_id,
        "bike_tamanho": db_bike.tamanho,
        "bike_modelo": db_bike.modelo,
        "data_retirada": db_locacao.data_retirada,
        "preco": db_locacao.preco
    }

@app.delete('/locacoes/{locacao_id}', response_model=Message, tags=["Locacao"])
def delete_locacao(locacao_id: int, session=Depends(get_session)):
    db_locacao = session.scalar(
        select(Locacao).where(Locacao.id == locacao_id)
    )

    if not db_locacao:
        raise HTTPException(
            status_code = HTTPStatus.NOT_FOUND,
            detail = "Locacao not found"
        )

    session.delete(db_locacao)
    session.commit()

    return {'message': 'Locacao deleted'}