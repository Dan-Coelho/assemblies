# Copilot Instructions for matic_votes

## Build, Test, and Lint Commands

- **Build/Run:**
  - Start server: `python manage.py runserver`
- **Migrations:**
  - Apply: `python manage.py migrate`
- **Tests:**
  - Run all: `python manage.py test`
  - Run single test: `python manage.py test <app>.<TestCaseClass>.<test_method>`
- **Lint:**
  - Ruff (if installed): `ruff .`

## High-Level Architecture

- Django 6.x project, Python 3.12+
- Apps: `organizations`, `assemblies`, `audits`, `votings`, `minutes`
- Multi-tenant: todas entidades possuem `org_id`
- Frontend: Django templates + TailwindCSS
- Banco: SQLite (MVP)
- Veja docs/ e PRD.md para domínio, requisitos e padrões

## Key Conventions

- Autenticação: email/senha (Django padrão)
- Papéis: síndico/presidente, secretário, conselheiro, membro
- Status de membros: ativo, inativo, inadimplente
- Fluxo de assembleia: Rascunho → Convocada → Em andamento → Encerrada → Arquivada
- Votações: abertas ou secretas, integridade auditável
- Atas: geradas automaticamente, assinaturas digitais
- Logs: auditoria imutável

## Docs

- Veja `docs/readme.md` para índice da documentação
- Veja `PRD.md` para requisitos detalhados
