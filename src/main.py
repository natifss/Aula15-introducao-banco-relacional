from datetime import datetime
from http import HTTPStatus
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional
from sqlmodel import SQLModel, create_engine, Field, Session, select

#ORM = Object Relational Mapping

class manutencao(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    placa: str 
    marca: str
    modelo: str
    cor: str
    nome_cliente: str
    nome_mecanico: str
    data_chegada: str
    data_finalizacao: Optional[str] = Field(default=None)

sqlite_filename = 'database.db'
sqlite_url = f'sqlite:///{sqlite_filename}'

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "ok"}

@app.post("/manutencao")
def cria_registro(manutencao: manutencao):
    with Session(engine) as session:
        session.add(manutencao)
        session.commit()
        session.refresh(manutencao)
        return manutencao
    
@app.patch("/manutencao/{id}/finalizar")
def finalizar_manutencao(id: int):
    with Session(engine) as session:
        statement = select(manutencao).where(manutencao.id==id)
        Manutencao = session.exec(statement=statement).first()

        if Manutencao.data_finalizacao: 
            return JSONResponse(content={"message": "Manutenção já finalizada"}, 
                                status_code=HTTPStatus.BAD_REQUEST)
        
        
        Manutencao.data_finalizacao = str(datetime.now())
        session.commit()
        session.refresh(Manutencao)
        return Manutencao
    
@app.delete("/manutencao/{id}")
def deletar_manutencao(id: int):
    with Session(engine) as session:
        statement = select(manutencao).where(manutencao.id==id)
        Manutencao = session.exec(statement=statement).first()

        if not Manutencao:
            return JSONResponse(content={"message": "Manutenção não existe"},
                                status_code=HTTPStatus.NOT_FOUND)

        if Manutencao.data_finalizacao:
            return JSONResponse(content={"message": "Manutenção já finalizada"},
                                status_code=HTTPStatus.BAD_REQUEST)
        
        session.delete(Manutencao)
        session.commit()
        
    

