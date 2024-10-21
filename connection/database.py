from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def create_db():
    engine = create_engine("mysql+mysqlconnector://root:mysql@000.00.0.0:3306") # Colocar o id do banco
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS pedal_pro"))

engine = create_engine("mysql+mysqlconnector://root:mysql@000.00.0.0:3306/pedal_pro") # Colocar o id do banco
Session = sessionmaker(bind=engine)

def get_session():
    with Session() as session:
        yield session