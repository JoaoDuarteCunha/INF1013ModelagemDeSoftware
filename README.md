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

Para rodar os testes

```bash
docker compose exec web python manage.py test
```

Para criar dados de demonstração:

```bash
docker compose exec web python manage.py seed
```

## Dados iniciais

Para popular o banco com dados de demonstração:

```bash
docker compose exec web python manage.py seed
```

O comando cria:

- usuário administrador;
- usuário cliente;
- filmes;
- cinema;
- sala;
- assentos;
- sessões futuras;
- cupons de desconto.

Usuários de teste:

```txt
Admin:
usuário: admin
senha: admin123

Cliente:
usuário: cliente
senha: cliente123
```

## Principais endpoints da API

### Catálogo

Listar filmes:

```http
GET /api/filmes/
```

Detalhar filme:

```http
GET /api/filmes/{id}/
```

### Cinemas, salas e assentos

Listar cinemas:

```http
GET /api/cinemas/
```

Listar salas:

```http
GET /api/salas/
```

Listar assentos físicos:

```http
GET /api/assentos/
```

### Sessões

Listar sessões:

```http
GET /api/sessoes/
```

Filtrar sessões:

```http
GET /api/sessoes/?filme={id}
GET /api/sessoes/?cinema={id}
GET /api/sessoes/?data=2026-06-16
GET /api/sessoes/?ativas=true
GET /api/sessoes/?futuras=true
GET /api/sessoes/?filme={id}&cinema={id}&data=2026-06-16&ativas=true&futuras=true
```

Detalhar sessão:

```http
GET /api/sessoes/{id}/
```

Exibir mapa de assentos da sessão:

```http
GET /api/sessoes/{id}/assentos/
```

Reservar assentos temporariamente:

```http
POST /api/sessoes/{id}/reservar-assentos/
```

Exemplo de corpo:

```json
{
  "assento_ids": [1, 2]
}
```

### Venda

Confirmar venda:

```http
POST /api/sessoes/{id}/confirmar-venda/
```

Exemplo de corpo sem cupom:

```json
{
  "itens": [
    {
      "assento_id": 1,
      "tipo": "inteira"
    },
    {
      "assento_id": 2,
      "tipo": "meia"
    }
  ],
  "forma_pagamento": "pix",
  "pagamento_aprovado": true
}
```

Exemplo de corpo com cupom:

```json
{
  "itens": [
    {
      "assento_id": 1,
      "tipo": "inteira"
    },
    {
      "assento_id": 2,
      "tipo": "meia"
    }
  ],
  "codigo_cupom": "PROMO20",
  "forma_pagamento": "pix",
  "pagamento_aprovado": true
}
```

Listar compras do usuário autenticado:

```http
GET /api/vendas/
```

Detalhar venda:

```http
GET /api/vendas/{id}/
```

Cancelar venda:

```http
POST /api/vendas/{id}/cancelar/
```

### Cupons

Listar cupons ativos:

```http
GET /api/cupons/
```

Validar cupom:

```http
POST /api/cupons/validar/
```

Exemplo de corpo:

```json
{
  "codigo": "PROMO20",
  "valor_bruto": "100.00"
}
```

## Exemplos de teste com PowerShell

Reservar assentos:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/api/sessoes/1/reservar-assentos/" `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"assento_ids": [1, 2]}'
```

Validar cupom:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/api/cupons/validar/" `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"codigo": "PROMO20", "valor_bruto": "100.00"}'
```

Confirmar venda com autenticação básica:

```powershell
$credencial = "cliente:cliente123"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($credencial)
$token = [Convert]::ToBase64String($bytes)

Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/api/sessoes/1/confirmar-venda/" `
  -Headers @{
    Authorization = "Basic $token"
    "Content-Type" = "application/json"
  } `
  -Body '{
    "itens": [
      {
        "assento_id": 1,
        "tipo": "inteira"
      },
      {
        "assento_id": 2,
        "tipo": "meia"
      }
    ],
    "codigo_cupom": "PROMO20",
    "forma_pagamento": "pix",
    "pagamento_aprovado": true
  }'
```

Listar vendas do cliente autenticado:

```powershell
$credencial = "cliente:cliente123"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($credencial)
$token = [Convert]::ToBase64String($bytes)

Invoke-RestMethod `
  -Method GET `
  -Uri "http://localhost:8000/api/vendas/" `
  -Headers @{ Authorization = "Basic $token" }
```

Cancelar venda:

```powershell
$credencial = "cliente:cliente123"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($credencial)
$token = [Convert]::ToBase64String($bytes)

Invoke-RestMethod `
  -Method POST `
  -Uri "http://localhost:8000/api/vendas/1/cancelar/" `
  -Headers @{ Authorization = "Basic $token" }
```

## Autores

Projeto desenvolvido para a disciplina **INF1013 - Modelagem de Software**.