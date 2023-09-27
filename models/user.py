from sqlalchemy import Column, String, Integer, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from  models import Base

class User(Base):

    __tablename__ = 'users'

    # prod_catalog.pk_prod, o sufixo pk está sendo utilizado para 
    # indicar que é uma chave primária
    id = Column("pk_user", Integer, primary_key=True)


    username = Column(String(140))  # 140 é o número máximo de caracteres
    password = Column(String)
    level = Column(Integer, default=1)  # Valor padrão para level
    xp = Column(Integer, default=0)     # Valor padrão para xp
    xp_to_next_level = Column(Integer, default=100)  # Valor padrão para xp_to_next_level
    tasks = relationship('Task', backref='user_tasks', lazy="joined")


    # A data de inserção será o instante de inserção caso não tenha
    data_insercao = Column(DateTime, default=datetime.now())

    # Criando um requisito de unicidade envolvendo uma par de informações
    __table_args__ = (UniqueConstraint("username", name="user_unique_id"),)

    
    def __init__(self, username, password, level, xp, xp_to_next_level,
                 data_insercao:Union[DateTime, None] = None):

        self.username = username
        self.password = password
        self.level = level
        self.xp = xp
        self.xp_to_next_level = xp_to_next_level

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao

    def to_dict(self):

        return{
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "data_insercao": self.data_insercao,
            "tasks": [c.to_dict() for c in self.tasks]
        }

    def __repr__(self):
        """
        Retorna uma representação do usuário em forma de texto.
        """
        return f"User(id={self.id}, username='{self.username}', password={self.password}, level='{self.level}', xp='{self.xp}', tasks='{self.tasks}')"

