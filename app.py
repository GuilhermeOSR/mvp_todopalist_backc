from strawberry.fastapi import GraphQLRouter
from typing import Optional
from fastapi import FastAPI
from typing import List
import strawberry
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select


import models

from authService.login_service import (
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    pwd_context,
)

@strawberry.type
class User:
    id: strawberry.ID
    username: str
    password: str
    level: int
    xp: int
    xp_to_next_level: int
    tasks: List['Task']  # Adicionando o relacionamento com tarefas

    @classmethod
    def marshal(cls, model: models.User) -> "User":
        return cls(
            id=strawberry.ID(str(model.id)),
            username=model.username,
            password=model.password,
            level=model.level,
            xp=model.xp,
            xp_to_next_level=model.xp_to_next_level,
            tasks=[Task.marshal(task) for task in model.tasks], 

        )
    async def level_up(self) -> None:
        # Atualiza o nível do usuário no banco de dados
        self.level += 1

        # Redefine o XP para 0 ao subir de nível
        self.xp = 0

        async with models.get_session() as session:
            user_db = await session.get(models.User, self.id)
            user_db.level = self.level
            user_db.xp = self.xp
            await session.commit()

            # Atualiza xp_to_next_level
        await self.update_xp_to_next_level()

    async def gain_xp(self, amount: int) -> None:
        # Atualiza a experiência do usuário no banco de dados
        self.xp += amount

        async with models.get_session() as session:
            user_db = await session.get(models.User, self.id)
            user_db.xp = self.xp
            await session.commit()

            # Verifica se o usuário deve subir de nível
        while self.xp >= self.xp_to_next_level:
            await self.level_up()

    async def complete_task(self, task_id: strawberry.ID) -> None:
        # Marca a tarefa como concluída no banco de dados
        for task in self.tasks:
            if task.id == task_id:
                task.status = True

        async with models.get_session() as session:
            # Decodifica o ID da tarefa de strawberry para obter o valor subjacente (int)
            task_id_int = int(task_id)

            # Atualiza o status da tarefa no banco de dados
            task_db = await session.get(models.Task, task_id_int)
            task_db.status = True
            await session.commit()

    async def update_xp_to_next_level(self) -> None:
        # Atualiza o valor de xp_to_next_level com base no nível atual
        self.xp_to_next_level = int(self.level * 100 * 1.5)

        async with models.get_session() as session:
            user_db = await session.get(models.User, self.id)
            user_db.xp_to_next_level = self.xp_to_next_level
            await session.commit()
    
@strawberry.type
class Task:
    id: strawberry.ID
    title: str
    description: str
    difficulty: int
    status: bool
    data_insercao: str
    user_id: int 
    amount: int

    @classmethod
    def marshal(cls, model: models.Task) -> "Task":
        return cls(
            id=strawberry.ID(str(model.id)),
            title=model.title,
            description=model.description,
            difficulty=model.difficulty,
            amount=model.amount,
            status=model.status,
            data_insercao=model.data_insercao,
            user_id=model.user_id 
        )
    
@strawberry.input
class UserRegisterInput:
    username: str
    password: str

@strawberry.input
class TaskInput:
    title: str
    description: str
    difficulty: int
    amount: Optional[int] = None

@strawberry.type
class CreateTaskResponse:
    task: Task

@strawberry.input
class UserQueryInput:
    termo: Optional[str] = strawberry.UNSET

@strawberry.type
class UserExists:
    message: str = "Usuário de mesmo nome já inserido na base"

@strawberry.type
class UserNotFound:
    message: str = "Não foi possível encontrar o usuário"


AddUserResponse = strawberry.union("AddUserResponse", (User, UserExists, UserNotFound))

# Queries

@strawberry.type
class Query:

    @strawberry.field
    async def users(self) -> List[User]:
        async with models.get_session() as session:
            sql = select(models.User).order_by(models.User.username)
            db_users = (await session.execute(sql)).scalars().unique().all()
            
            # Carrega as propriedades relacionadas 'tasks' dentro da sessão
            for user in db_users:
                user.tasks  # Isso carregará as tarefas relacionadas

        return [User.marshal(user) for user in db_users]
    
    @strawberry.field
    async def user(self, token: str) -> User:
        # Decodificar o token JWT para obter o ID do usuário
        user_id = decode_jwt_token(token)

        async with models.get_session() as session:
            # Buscar o usuário pelo user_id
            user_db = await session.get(models.User, user_id)

        if not user_db:
            raise Exception("Usuário não encontrado")

        return User.marshal(user_db)
    
    @strawberry.field
    async def tasks(self, token: str, termo: Optional[str] = None, offset: int = 0, limit: int = 4) -> List[Task]:
        # Decodificar o token JWT para obter o ID do usuário
        user_id = decode_jwt_token(token)

        async with models.get_session() as session:
            # Buscar as tarefas associadas ao usuário pelo user_id
            sql = select(models.Task).filter(models.Task.user_id == user_id)

            if termo:
                sql = sql.filter(
                    models.Task.title.ilike(f"%{termo}%") |
                    models.Task.description.ilike(f"%{termo}%")
            )
            # Aplica a paginação
            sql = sql.offset(offset).limit(limit)

            db_tasks = (await session.execute(sql)).scalars().unique().all()

        return [Task.marshal(task) for task in db_tasks]

    @strawberry.field
    async def busca(self, query_input: Optional[UserQueryInput] = None) -> List[User]:
        async with models.get_session() as session:
            if query_input:
                sql = select(models.User) \
                        .filter(models.User.username.ilike(f"%{query_input.termo}%")).\
                            order_by(models.User.username)
            else:
                sql = select(models.User).order_by(models.User.username)

            db_users = (await session.execute(sql)).scalars().unique().all()
        return [User.marshal(user) for user in db_users]
    
#Mutations

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register_user(self, input: UserRegisterInput) -> User:
        # Verifica se o nome de usuário já existe no banco de dados
        async with models.get_session() as session:
            existing_user = (
                await session.execute(select(models.User).filter(models.User.username == input.username))
            ).scalar() 
            if existing_user:
                raise Exception("Nome de usuário já em uso")

            # Cria um novo usuário com a senha criptografada
            hashed_password = hash_password(input.password) 
            new_user = models.User(
                username=input.username,
                password=hashed_password,
                level=None,
                xp=None,
                xp_to_next_level=None
            )

            session.add(new_user)
            await session.commit()

    
        # Cria uma nova sessão para carregar as tarefas do novo usuário após o commit
        async with models.get_session() as session:
            new_user = (
                await session.execute(select(models.User).filter(models.User.username == input.username))
            ).scalar()

            # Carrega as propriedades relacionadas 'tasks' dentro da nova sessão
            new_user.tasks  # Isso carregará as tarefas relacionadas

        return User.marshal(new_user)
        
    @strawberry.mutation
    async def login_user(self, username: str, password: str) -> str:
        async with models.get_session() as session:
            # Verifica se o usuário existe
            user = (
                await session.execute(select(models.User).filter(models.User.username == username))
            ).scalar()

            if not user:
                raise Exception("Usuário não encontrado")

            # Verifica se a senha está correta
            if not pwd_context.verify(password, user.password):
                raise Exception("Senha incorreta")

            # Gera e retorna um token JWT válido
            token = create_jwt_token(user.id)
            return token
        
    @strawberry.mutation
    async def create_task(self, token: str, input: TaskInput) -> CreateTaskResponse:
        # Decodificar o token JWT para obter o ID do usuário
        user_id = decode_jwt_token(token)
        # Mapeia as opções de dificuldade para valores inteiros
        difficulty_map = {
        1: 10,
        2: 20,
        3: 30,
            }

            # Certifica-se de que a dificuldade escolhida seja válida
        if input.difficulty not in difficulty_map:
            raise Exception("Dificuldade inválida")
        
        # Obtém o valor de `amount` com base na dificuldade escolhida
        amount = difficulty_map[input.difficulty]

        async with models.get_session() as session:
            # Verifica se o usuário existe
            user = (
                await session.execute(select(models.User).filter(models.User.id == user_id))
            ).scalar()

            if not user:
                raise Exception("Usuário não encontrado")

            # Cria uma nova tarefa associada ao usuário
            db_task = models.Task(
                title=input.title,
                description=input.description,
                difficulty=input.difficulty,
                amount = amount,
                status=False,  # Status padrão como False
                user_id = user_id
            )

            session.add(db_task)
            await session.commit()

        return CreateTaskResponse(task=Task.marshal(db_task))
    
    @strawberry.mutation
    async def delete_task(self, token: str, task_id: strawberry.ID) -> Task:
        # Decodificar o token JWT para obter o ID do usuário
        user_id = decode_jwt_token(token)

        async with models.get_session() as session:
            # Verifica se a tarefa existe e pertence ao usuário
            task_id_int = int(task_id)
            task_db = await session.get(models.Task, task_id_int)

            if not task_db:
                raise Exception("Tarefa não encontrada")

            if task_db.user_id != user_id:
                raise Exception("Você não tem permissão para excluir esta tarefa")

            # Exclui a tarefa
            await session.delete(task_db)
            await session.commit()

        return Task.marshal(task_db)
    
    @strawberry.mutation
    async def update_task(
        self,
        token: str,
        task_id: strawberry.ID,
        input: TaskInput,
    ) -> Task:
        # Decodificar o token JWT para obter o ID do usuário
        user_id = decode_jwt_token(token)


        async with models.get_session() as session:
            # Verifica se a tarefa existe e pertence ao usuário
            task_id_int = int(task_id)
            task_db = await session.get(models.Task, task_id_int)

            if not task_db:
                raise Exception("Tarefa não encontrada")

            if task_db.user_id != user_id:
                raise Exception("Você não tem permissão para alterar esta tarefa")

            # Verifica se a tarefa pode ser alterada (status = False)
            if task_db.status:
                raise Exception("Você não pode alterar uma tarefa concluída")
            
            difficulty_map = {
                1: 10,
                2: 20,
                3: 30,
                    }


            # Atualiza os atributos da tarefa
            task_db.title = input.title
            task_db.description = input.description
            task_db.difficulty = input.difficulty
            task_db.amount = difficulty_map[input.difficulty]  # Atualiza o amount com base na dificuldade

            await session.commit()

        return Task.marshal(task_db)
    
# Funções de Gameficação

    @strawberry.mutation
    async def level_up(self, token: str) -> User:
        user_id = decode_jwt_token(token)
        async with models.get_session() as session:
            user_db = await session.get(models.User, user_id)

            if not user_db:
                raise Exception("Usuário não encontrado")

            user = User.marshal(user_db)
            await user.level_up()

        return user

    @strawberry.mutation
    async def gain_xp(self, token: str, amount: int) -> User:
        user_id = decode_jwt_token(token)
        async with models.get_session() as session:
            user_db = await session.get(models.User, user_id)

            if not user_db:
                raise Exception("Usuário não encontrado")

            user = User.marshal(user_db)
            await user.gain_xp(amount)

        return user
    
    @strawberry.mutation
    async def complete_task(self, token: str, task_id: strawberry.ID) -> User:
        # Decodificar o token JWT para obter o ID do usuário
        user_id = decode_jwt_token(token)

        async with models.get_session() as session:
            # Verifica se o usuário existe
            user_db = await session.get(models.User, user_id)

            if not user_db:
                raise Exception("Usuário não encontrado")

            user = User.marshal(user_db)
            await user.complete_task(task_id)  # Chama a função complete_task no objeto User

        return user
        
    

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
    # Configurar CORS para permitir a origem do front-end
origins = ["http://localhost:3000", "http://localhost:8000"]  # Adicione todos os domínios que você estiver usando
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


