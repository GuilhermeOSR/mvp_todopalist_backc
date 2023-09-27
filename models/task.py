from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from typing import Union
from  models import Base, User


class Task(Base):

    __tablename__ = 'user_task'

    id = Column(Integer, primary_key=True)
    title = Column(String(4000))
    description = Column(String(4000))
    difficulty = Column(String(4000))
    amount = Column(Integer)
    status = Column(Boolean, default=False)
    data_insercao = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre usuário e tarefas.

    user_id = Column(Integer, ForeignKey('users.pk_user'), nullable=False)
    user = relationship(User, uselist=False, lazy="joined", viewonly=True)

    def __init__(self, title: str, description: str, difficulty: int, amount, status: bool = False, data_insercao: Union[DateTime, None] = None, user_id: int = None):
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.amount = amount
        self.status = status
        if data_insercao:
            self.data_insercao = data_insercao
        self.user_id = user_id
        

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "amount": self.amount,
            "status": self.status,
            "data_insercao": self.data_insercao,
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"Task(id={self.id}, title='{self.title}')"
