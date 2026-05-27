# Usa uma imagem oficial leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /code

# Copia o arquivo de dependências primeiro (otimiza o cache das camadas do Docker)
COPY ./requirements.txt /code/requirements.txt

# Instala as dependências sem salvar cache para manter a imagem leve
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia todo o restante do código do projeto para dentro do container
COPY ./app /code/app

# Comando padrão para iniciar o Uvicorn apontando para o main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]