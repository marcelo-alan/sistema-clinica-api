# 🏥— API de Agendamentos Médicos

O **ClinicaMedControl** é uma API RESTful de alta performance desenvolvida para gerenciar o fluxo de agendamentos e consultas de uma clínica médica de forma inteligente, segura e automatizada. 

O foco principal do projeto foi construir uma arquitetura de backend robusta, aplicando regras de negócio realistas, criptografia de ponta e controle rígido de segurança por níveis de acesso.

---

## 🚀 Principais Funcionalidades

* **Autenticação e Segurança Avançada (JWT):** Sistema de login seguro que gera tokens JWT (JSON Web Tokens) válidos para autenticar as requisições. As senhas dos usuários passam por criptografia hash usando o algoritmo `pbkdf2_sha256` (via Passlib).
* **Controle de Acesso por Perfil (RBAC):** Sistema inteligente de permissões baseado em papéis (`roles`):
    * **`cliente`**: Permissões limitadas (pode criar agendamentos para si e cancelar suas próprias consultas).
    * **`admin`**: Acesso global (pode listar, gerenciar e auditar todos os agendamentos da clínica).
* **Filtro Inteligente de Horários Disponíveis:** Endpoint que calcula em tempo real, direto no banco de dados, quais horários (das 08:00 às 17:00) estão livres em uma data específica, removendo conflitos e devolvendo vagas geradas por consultas canceladas.
* **Trava de Segurança de Agendamento Duplo:** Regra de negócio automatizada que impede o sistema de aceitar dois agendamentos ativos exatamente na mesma data e horário.
* **Cancelamento Seguro (Método PATCH):** Rota protegida que altera o status do agendamento para `"cancelado"` e libera o horário de volta para o sistema imediatamente, impedindo que um cliente altere o agendamento de outro.

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

* **Linguagem:** Python 3.10+
* **Framework Principal:** **FastAPI** (Alta performance, validação nativa com Pydantic e documentação automatizada)
* **Banco de Dados:** SQLite (leve e rápido para ambiente de desenvolvimento)
* **ORM / Persistência:** **SQLAlchemy** (Mapeamento objeto-relacional para manipulação das tabelas via código Python)
* **Criptografia:** Passlib (Bcrypt) e Python-Jose
* **Arquitetura e DevOps:** **Docker** e **Docker Compose** (Infraestrutura pronta para containerização e deploy isolado)

---

## 📂 Estrutura Arquitetural do Código

O projeto segue as melhores práticas de organização do ecossistema FastAPI, dividindo as responsabilidades de forma limpa:

* `app/main.py`: Ponto de entrada da aplicação, inicialização das rotas e middlewares.
* `app/models.py`: Definição das tabelas do banco de dados (Usuários e Agendamentos) via SQLAlchemy.
* `app/schemas.py`: Modelos de validação de dados (Pydantic) para entrada e saída da API.
* `app/crud.py`: Camada de persistência contendo toda a lógica de consultas e regras de negócio do banco.
* `app/security.py`: Funções utilitárias de hashing de senha e criação do JWT.
* `app/routers/`: Centralização das rotas divididas por contexto (Autenticação, Usuários e Agendamentos) com validadores personalizados de permissões (`PermissaoPorRole`).

---

## 🔧 Como Executar o Projeto

### Pré-requisitos
* Python 3.10 ou superior instalado.

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/marcelo-alan/SEU_REPOSITORIO.git](https://github.com/marcelo-alan/SEU_REPOSITORIO.git)
   cd SEU_REPOSITORIO
