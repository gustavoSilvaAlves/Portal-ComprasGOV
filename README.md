# API Solver de hCaptcha para o ComprasGov

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.35-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Uma API assíncrona e robusta construída com FastAPI para automatizar a resolução do desafio hCaptcha presente no portal ComprasGov. O projeto utiliza Selenium para simular a interação humana em um navegador e é totalmente containerizado com Docker para facilitar a execução e o deploy em qualquer ambiente.

## ✨ Sobre o Projeto

Este projeto foi desenvolvido para resolver programaticamente o desafio hCaptcha do portal ComprasGov. Em vez de uma interação manual, a API expõe um endpoint RESTful que, ao ser chamado, inicia uma instância de navegador em background, navega até a página, resolve o captcha e extrai o token de resposta.

O principal objetivo é fornecer um meio automatizado de obter o token de acesso necessário para interagir com outros endpoints do portal ComprasGov, viabilizando a criação de outras automações. A API possui um controle para limitar o número de execuções concorrentes, garantindo o uso consciente dos recursos.

## 🚀 Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

* **[Python 3.11](https://www.python.org/)**: Linguagem de programação principal.
* **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web assíncrono para a construção da API.
* **[Uvicorn](https://www.uvicorn.org/)** & **[Gunicorn](https://gunicorn.org/)**: Servidores ASGI/WSGI para rodar a aplicação em ambiente de produção.
* **[Selenium](https://www.selenium.dev/)**: Ferramenta de automação de navegadores para interagir com a página e resolver o captcha.
* **[Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)**: Versão customizada do Chromedriver para evitar detecção por sistemas anti-bot.
* **[Docker](https://www.docker.com/)** & **[Docker Compose](https://docs.docker.com/compose/)**: Para containerização e orquestração do ambiente da aplicação.

## 📁 Estrutura do Projeto

A estrutura de arquivos do projeto é organizada da seguinte forma:

```text
hcaptchaComprasGov/
├── app/
│   └── main.py           # Ponto de entrada e lógica principal da API com FastAPI.
├── .dockerignore         # Define arquivos a serem ignorados pelo Docker no build.
├── .gitignore            # Define arquivos a serem ignorados pelo Git.
├── Dockerfile            # Receita para construir a imagem Docker da aplicação.
├── docker-compose.yml    # Arquivo para orquestrar a execução do contêiner com Docker Compose.
└── requirements.txt      # Lista de dependências Python do projeto.
```

## ⚙️ Como Começar

Siga os passos abaixo para executar a aplicação localmente.

### Pré-requisitos

Você precisa ter o **Docker** e o **Docker Compose** instalados na sua máquina.

* [Instalar Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_AQUI]
    cd hcaptchaComprasGov
    ```

2.  **Construa e execute com Docker Compose:**
    Este único comando irá construir a imagem Docker (se ainda não existir) e iniciar o contêiner da aplicação em background.
    ```bash
    docker compose up --build -d
    ```

3.  **Acesse a API:**
    A aplicação estará rodando e acessível em `http://localhost:8000`.

## 📖 API - Uso e Endpoints

A API é auto-documentada usando o padrão OpenAPI. Você pode acessar a documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI em:

**`http://localhost:8000/docs`**

### Status da API

* **Endpoint:** `GET /api/v1/status`
* **Descrição:** Verifica se a API está online e respondendo.
* **Exemplo de Requisição:**
    ```bash
    curl -X 'GET' 'http://localhost:8000/api/v1/status'
    ```
* **Resposta de Sucesso (200 OK):**
    ```json
    {
      "status": "ok"
    }
    ```

### Obter Token hCaptcha

* **Endpoint:** `GET /api/v1/get_hcaptcha`
* **Descrição:** Inicia o processo de resolução do hCaptcha e retorna o token obtido. Esta é uma operação demorada e de uso intensivo de recursos.
* **Exemplo de Requisição:**
    ```bash
    curl -X 'GET' 'http://localhost:8000/api/v1/get_hcaptcha'
    ```
* **Resposta de Sucesso (200 OK):**
    ```json
    {
      "hcaptcha_token": "P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ...etc"
    }
    ```
* **Resposta de Erro (503 Service Unavailable):**
    Ocorre quando o número máximo de execuções concorrentes é atingido.
    ```json
    {
      "detail": "O serviço está ocupado. Tente novamente mais tarde."
    }
    ```
* **Resposta de Erro (500 Internal Server Error):**
    Ocorre se a API não conseguir resolver o captcha após múltiplas tentativas.
    ```json
    {
      "detail": "Não foi possível capturar o hCaptcha após múltiplas tentativas"
    }
    ```