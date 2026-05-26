# Ingressos App

Sistema web de venda de ingressos de cinema inspirado no ingresso.com, desenvolvido para a disciplina **INF1013 - Modelagem de Software**.

O projeto utiliza **Django**, **PostgreSQL**, **Redis** e **Docker**. A ideia inicial é construir um monólito modular organizado por domínios, com possibilidade de evolução futura para microserviços.

## Resumo

O sistema tem como objetivo permitir o gerenciamento e a venda de ingressos de cinema.

Funcionalidades previstas:

- Cadastro e gerenciamento de filmes.
- Cadastro de cinemas e salas.
- Cadastro de sessões.
- Controle de assentos por sessão.
- Reserva temporária de assentos.
- Venda de ingressos.
- Aplicação de cupons.
- Simulação de pagamento.
- Cancelamento de venda.

## Tecnologias

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Docker
- Docker Compose

## Estrutura básica

```txt
ingressos-app/
  backend/
    apps/
    config/
    manage.py
    Dockerfile
    requirements.txt
  docker-compose.yml
  .env.example
  README.md
```

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd ingressos-app
```

### 2. Criar o arquivo `.env`

No Linux/macOS:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 3. Subir os containers

```bash
docker compose up --build
```

### 4. Rodar as migrations

Em outro terminal, execute:

```bash
docker compose exec web python manage.py migrate
```

### 5. Criar um superusuário

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acessar o sistema

Admin Django:

```txt
http://localhost:8000/admin
```

Aplicação:

```txt
http://localhost:8000
```

## Comandos úteis

Subir o projeto:

```bash
docker compose up
```

Subir reconstruindo a imagem:

```bash
docker compose up --build
```

Parar os containers:

```bash
docker compose down
```

Criar migrations:

```bash
docker compose exec web python manage.py makemigrations
```

Aplicar migrations:

```bash
docker compose exec web python manage.py migrate
```

Criar superusuário:

```bash
docker compose exec web python manage.py createsuperuser
```

Ver logs:

```bash
docker compose logs -f web
```

Acessar o container:

```bash
docker compose exec web bash
```

## Status

- [x] Estrutura inicial do projeto
- [x] Configuração com Docker
- [x] Projeto Django criado
- [x] PostgreSQL configurado
- [x] Redis configurado
- [ ] Models principais
- [ ] Admin Django
- [ ] APIs REST
- [ ] Fluxo de compra
- [ ] Reserva de assentos
- [ ] Pagamento simulado

## Autores

Projeto desenvolvido para a disciplina **INF1013 - Modelagem de Software**.