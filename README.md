# Zayn Resort

API REST de reservas de hotel feita em Python. Projeto de estudo e portfólio, com foco em arquitetura em camadas, integridade de dados e testes.

## Stack

Python 3.14 · FastAPI · Pydantic v2 · PostgreSQL 18 · psycopg v3 (SQL puro, sem ORM) · Alembic · pytest

## Funcionalidades

**Reservas (núcleo do sistema)**
- Criação com validação de datas, verificação de cliente, quarto e categoria, detecção de conflito de período e cálculo automático de `total_amount` (diária × número de dias).
- Alteração de datas (`PATCH /reservations/{id}/dates`) com nova checagem de conflito e recálculo do valor. Não é permitida em reservas `cancelled` ou `checked_out`.
- Alteração de status (`PATCH /reservations/{id}/status`) com máquina de estados.
- Apenas reservas `confirmed` e `checked_in` contam como ocupação do quarto.

**Catálogo e clientes**
- Categorias de quarto (nome, capacidade, diária) e quartos associados a uma categoria.
- Clientes com CPF de 11 dígitos, data de nascimento e opt-in de newsletter.

**Todas as entidades**
- CRUD completo (POST, GET, PUT, PATCH, DELETE) com soft delete (`deleted_at`) e timestamps.
- Normalização de entrada (remoção de espaços nas pontas) e rejeição de campos desconhecidos (`extra="forbid"`).
- Unicidade que ignora maiúsculas/minúsculas (nome de categoria, número de quarto) e que convive com soft delete.
- Bloqueio de exclusão de entidades em uso (409).

### Máquina de estados da reserva

```
confirmed ──► checked_in ──► checked_out
    │
    └──────► cancelled
```

`checked_out` e `cancelled` são estados finais. Qualquer outra transição retorna 409.

## Arquitetura

```
Request → Schema → Route → (Service) → Repository → Banco
```

| Camada | Responsabilidade |
|---|---|
| Schema | Valida e normaliza a entrada com Pydantic. Erros viram 422 sem tocar o banco. |
| Route | Camada HTTP: status, `response_model` e tradução de exceções de domínio em `HTTPException`. |
| Service | Apenas Reservation: máquina de estados, `total_amount` e conflito de datas. Não conhece HTTP. |
| Repository | Apenas SQL, no repository da tabela consultada. Nunca levanta exceção de domínio. |
| `database.py` | Ponto único de acesso ao banco (`execute_query`). |

As exceções de domínio ficam em `app/services/reservation_exceptions.py`.

## Decisões de design

**Reservas e regras de negócio**
- **Service sem HTTP:** o Service levanta exceções de domínio e a Route as traduz em status HTTP.
- **Ordem de validação:** recurso próprio (404) → corpo vazio (400) → recursos relacionados (404) → regra ou unicidade (409). Na criação de reserva: datas (422) → cliente → quarto → categoria (404) → conflito (409) → cálculo → INSERT.
- **UPDATE com `if not result`:** um UPDATE pode afetar zero linhas por race condition, então o resultado vazio vira 404. Já `INSERT ... RETURNING` levanta exceção, não devolve vazio.
- **Enum de status:** `ReservationStatus(str, Enum)` herda a comparação de `str`, mas sobrescreve `__str__`. Por isso o valor é convertido com `.value` na fronteira Service → Repository.

**Dados e banco**
- **Dinheiro:** `Decimal` e `NUMERIC(10,2)`, nunca `float`. No JSON, `Decimal` é serializado como string.
- **Código é UX, banco é integridade:** validações em código dão boas mensagens, e constraints do banco garantem a consistência.
- **Soft delete e unicidade:** `UNIQUE` simples não funciona com soft delete. Uso índices únicos parciais (`WHERE deleted_at IS NULL`) sobre `LOWER(col)` quando a comparação ignora caixa, e a query usa a mesma expressão do índice.
- **FK não protege soft delete:** soft delete é um `UPDATE`, então a linha referenciada continua existindo. A regra "em uso" fica na aplicação, com consultas de leitura antes do delete.
- **Queries explícitas:** colunas nomeadas (sem `*`) e `RETURNING` para devolver o que foi persistido.

**API e schemas**
- **PUT substitui, PATCH altera parcialmente:** o PATCH usa `model_dump(exclude_unset=True)`.
- **Schemas separados:** entrada com `extra="forbid"`, e respostas sem essa restrição. Campos opcionais no banco usam `| None = None` na resposta.
- **Respostas:** POST, PUT e PATCH devolvem o objeto completo, e DELETE devolve 204 sem corpo.
- **DELETE:** 404 se o recurso nunca existiu e 409 se já foi deletado.

**Migrations**
- Alembic, com migrations pequenas e reversíveis (`downgrade` inverso, em ordem inversa). Migrations aplicadas nunca são editadas.
- Constraints e índices atuais: CHECK em `reservations.status`, índice único parcial de CPF (`customers_cpf_active_unique`), índice único parcial de nome de categoria e de número de quarto (sobre `LOWER`) e índice parcial em `reservations.room_id`.

**Configuração**
- A conexão vem de `DATABASE_URL`, definida no `.env` (fora do Git). O `.env.example` documenta o formato.

## Como rodar

**Pré-requisitos:** Python 3.14 e PostgreSQL 18 com um banco chamado `zayn_resort`.

```powershell
git clone <url-do-repositorio>
cd zayn-resort
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Edite o `.env` com os seus dados. Ele nunca deve ser commitado:

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/zayn_resort
```

Caracteres especiais na senha devem ser codificados na URL (`@` vira `%40`, `%` vira `%25`).

Documentação interativa: `http://localhost:8000/docs`

## Endpoints

| Recurso | Rotas |
|---|---|
| Clientes | `GET/POST /customers`, `GET/PUT/PATCH/DELETE /customers/{customer_id}` |
| Categorias de quarto | `GET/POST /room-categories`, `GET/PUT/PATCH/DELETE /room-categories/{id}` |
| Quartos | `GET/POST /rooms`, `GET/PUT/PATCH/DELETE /rooms/{id}` |
| Reservas | `GET/POST /reservations`, `GET/DELETE /reservations/{id}`, `PATCH /reservations/{id}/dates`, `PATCH /reservations/{id}/status` |

### Códigos de status

| Código | Uso |
|---|---|
| 201 | Recurso criado |
| 204 | Delete bem-sucedido, sem corpo |
| 400 | Requisição válida, mas sem sentido (PATCH vazio) |
| 404 | Recurso não existe |
| 409 | Conflito de estado (duplicidade, já deletado, em uso, período indisponível, transição inválida) |
| 422 | Requisição inválida, rejeitada antes de tocar o banco |

## Testes

```powershell
python -m pytest -v
```

A suíte segue o padrão AAA (Arrange, Act, Assert) e DRY, com `monkeypatch` no ponto onde a função é usada. Como os repositories são mockados, **os testes não executam SQL**. As queries, constraints e índices foram validados manualmente no `psql` e pela API.

## Estrutura do projeto

```
app/
  main.py
  database.py
  repositories/    # SQL, um arquivo por tabela
  routes/          # camada HTTP
  schemas/         # entrada e resposta (Pydantic)
  services/        # regras de Reservation e exceções de domínio
alembic/versions/  # migrations
tests/             # testes e conftest.py (fixture client)
.env.example
alembic.ini.example
```

## Limitações conhecidas

- **Uma conexão por query:** sem pool e sem transação por requisição. Checar e gravar acontecem em transações separadas, então há risco de race condition (por exemplo, duas reservas simultâneas no mesmo período, ou delete concorrente com checagem de uso).
- Sem testes de integração com PostgreSQL real.
- Sem autenticação e sem autorização.
- Mensagens 409 ainda não estão padronizadas entre as entidades.
- Os endpoints GET devolvem dicts montados à mão, sem `response_model`.

## Roadmap

- Connection pool e uma transação por requisição (com `SELECT ... FOR UPDATE`).
- Exclusion constraint para impedir reservas sobrepostas no banco.
- Testes de integração com PostgreSQL real.
- Autenticação.
- `response_model` nos GETs e proteção contra `KeyError` nas transições de status.