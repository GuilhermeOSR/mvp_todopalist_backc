# API TODOPALIST em GraphQL

MVP **Desenvolvimento Full Stack Avançado** 

Api desenvolvida com objetivo de motivar usuários a fazerem tarefas ganhando Xp e subindo de Nivel como um jogo


As principais tecnologias usadas:
 - [FastAPI](https://fastapi.tiangolo.com/)
 - [SQLAlchemy](https://www.sqlalchemy.org/)
 - [Strawberry](https://strawberry.rocks/docs)
 - [SQLite](https://www.sqlite.org/index.html)

---
### Instalação


Será necessário ter todas as libs python listadas no `requirements.txt` instaladas.
Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

Criação do ambiente virtual:

```
python -m venv {nome do ambiente}
```

```
{nomeDoAmbiente}\Scripts\activate
```
Para ativa-lo, deve ser inserido este comando:


```
(env)$ pip install -r requirements.txt
```
Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.


---
### Criando o Banco

A comunicação utilizando o Strawberry acontece de forma assíncrona, ao contrário do que foi feito na API REST. Com isso, a criação do banco aqui vai ser diferente.

Para criar o banco será necessário executar:

```
python creat_db.py 
```

---
### Executando o servidor

Para executar a API basta executar:

```
(env)$ uvicorn app:app --host 0.0.0.0
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte. 

```
(env)$ uvicorn app:app --reload --host 0.0.0.0
```

Uma vez executando o servidor, você pode acessar o painel do GraphiQL pelo link [http://127.0.0.1:8000/graphql](http://127.0.0.1:8000/graphql ).

---
## Uso do GraphiQL

O GraphiQL é um ambiente de desenvolvimento para o GraphQL. Você não precisa instalar nada para ter acesso, ele já vem junto com o strawberry.

Nesse painel é possível fazer consultas simples aqui temos alguns exemplos relacionados a minha aplicação.


# Queries

> **Listando usuários cadastrados**
> ```
> query {
>  users{
>    username
>    level
>    xp
>  }
>}
> ```
>
>
> **Fazendo uma busca por usuário pelo token de acesso**
> ```
> query{
>   user(token:"SEU_TOKEN_JWT_AQUI"){
>     username
>
>   }
> }
> ```
> tasks
>    
>
>
# Mutations 

> **Registrando um usuário na base de dados**
> ```
> mutation {
>   registerUser(input: {username: "luiz", password: "teste"}) {
>      username
>    }
>  }
>
> **Fazendo login na aplicação**
> mutation {
>   loginUser(username: "luiz", password: "teste")
> }
> ```
>
>
> **Criando uma nova Tarefa para o usuário autenticado**
> ```
> mutation {
>  createTask(token: "SEU_TOKEN_JWT_AQUI", input: {title: "Desenhar", description: "Por 5h", difficulty: 2}) {
>    ... on CreateTaskResponse {
>      task {
>        id
>        title
>        description
>        difficulty
>        status
>        dataInsercao
>        userId
>      }
>    }
>  }
>}
> ```
>
> ```
> mutation {
>    deleteTask(token: "SEU_TOKEN_JWT_AQUI", taskId: id da tarefa) {
>       title
>        }
>}
> ```
>
>
> ```
> mutation {
>    updateTask(token: "SEU_TOKEN_JWT_AQUI", taskId: id da tarefa, input: {title: "Novo titulo", description: "Nova descrição", difficulty: 1 (nova dificuldade)}) {
>       title
>        description
>        difficulty
>     }
>        }
> ```
>
> ```
> mutation {
>   levelUp(token:  "SEU_TOKEN_JWT_AQUI") {
>    username
>    level
>  }
>    }
> ```
  # (Amount é definida no cliente pela dificuldade da tarefa) #
> ```
> mutation {           
>    gainXp(token: "SEU_TOKEN_JWT_AQUI", amount: int ) {
>        username
>        xp
>    }
> }
> ```
>
> ```
> mutation {
>    completeTask(token: "SEU_TOKEN_JWT_AQUI", taskId: int) {
>            username
>            tasks {
>                title
>                status
>          }
>       }
>     }
> ```
>
>
> dockerfile:
>Montar imagem do docker
>```docker build -t (nome da imagem) ```
>Rodar o container do docker
>``` docker run -p 8000:8000 {nome do container} ```


