from datetime import datetime
from sqlalchemy.orm import relation,backref,relationship
from sqlalchemy import Column, Integer, Unicode,DateTime,Numeric,ForeignKey,LargeBinary
from myprojectname.model import DeclarativeBase

from sqlalchemy import Table, Column
from myprojectname.model import metadata

solicitante_entrevistador_tabla = Table('solicitante_entrevistador', metadata,
                         Column('id_solicitante', Integer,
                                ForeignKey('solicitante.id_solicitante',
                                           onupdate="CASCADE",
                                           ondelete="CASCADE"),
                                primary_key=True),
                         Column('id_entrevistador', Integer,
                                ForeignKey('entrevistador.id_entrevistador',
                                           onupdate="CASCADE",
                                           ondelete="CASCADE"),
                                primary_key=True))



class Solicitante(DeclarativeBase):
    __tablename__ = 'solicitante'
    id_solicitante = Column(Integer, autoincrement=True, primary_key=True)
    nombre_solicitante = Column(Unicode(30))
    edad = Column(Integer)
    foto_solicitante = Column(LargeBinary(length=(2 ** 32) - 1))


class Entrevistador(DeclarativeBase):
    __tablename__ = 'entrevistador'
    id_entrevistador = Column(Integer, autoincrement=True, primary_key=True)
    nombre_entrevistador = Column(Unicode(30))
    departamento = Column(Unicode(30))
    foto_entrevistador = Column(LargeBinary(length=(2 ** 32) - 1))
    solicitantes = relation('Solicitante', secondary=solicitante_entrevistador_tabla, backref='entrevistador')


