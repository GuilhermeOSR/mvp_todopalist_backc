# Use uma imagem base do Python
FROM python:3.8

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Instale as dependências
RUN pip install -r requirements.txt

# Copie todo o conteúdo do diretório do projeto para o contêiner
COPY . .

# Exponha a porta em que o seu aplicativo estará em execução (substitua a porta apropriada)
EXPOSE 8000

# Comando para iniciar o seu aplicativo (substitua pelo comando apropriado)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
