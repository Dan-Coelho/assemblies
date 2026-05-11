## 1. Lista de Tarefas por Sprint

---

### Sprint 0 — Fundação do Projeto
**Objetivo:** Ambiente configurado, estrutura de pastas criada e projeto Django rodando.

#### 1. Configuração do ambiente
- [x] 1.1 Criar pasta raiz do projeto
- [x] 1.2 Criar arquivo `.python-version` com `3.13`
- [x] 1.3 Inicializar projeto com `uv init`
- [x] 1.4 Instalar Django com `uv add django`
- [x] 1.5 Instalar ruff com `uv add --dev ruff`
- [x] 1.6 Criar `pyproject.toml` com configurações de ruff (aspas simples, linha 100, PEP8)
- [x] 1.7 Criar `.gitignore` com entradas para Python, Django, SQLite e uv

#### 2. Inicialização do projeto Django
- [x] 2.1 Executar `django-admin startproject core .` (ponto = pasta raiz)
- [x] 2.2 Criar pasta `core/` manualmente com `__init__.py`
- [x] 2.3 Criar apps: `organizations`, `assemblies`, `votings`, `minutes`, `audits`
  - [x] 2.3.1 `python manage.py startapp organizations`
  - [x] 2.3.2 `python manage.py startapp assemblies`
  - [x] 2.3.3 `python manage.py startapp votings`
  - [x] 2.3.4 `python manage.py startapp minutes`
  - [x] 2.3.5 `python manage.py startapp audits`
- [x] 2.4 Registrar todos os apps em `INSTALLED_APPS` no `settings.py`
- [x] 2.5 Configurar `BASE_DIR`, `TEMPLATES`, `STATICFILES_DIRS` no `settings.py`

#### 3. Configuração do TailwindCSS
- [x] 3.1 Instalar Node.js localmente (apenas para build do Tailwind)
- [x] 3.2 Instalar TailwindCSS via `npm install -D tailwindcss`
- [x] 3.3 Criar `tailwind.config.js` apontando para templates Django
- [x] 3.4 Criar arquivo `static/css/input.css` com diretivas Tailwind
- [x] 3.5 Configurar script de build no `package.json`
- [x] 3.6 Configurar `STATICFILES_DIRS` no Django para servir o CSS compilado
- [x] 3.7 Testar build com `npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css`

#### 4. Configuração de logging
- [x] 4.1 Adicionar configuração `LOGGING` no `settings.py`
- [x] 4.2 Configurar handler de console com formatação: `[LEVEL] app.module: mensagem`
- [x] 4.3 Definir level `DEBUG` para desenvolvimento e `INFO` para produção
- [x] 4.4 Testar log simples em uma view temporária

#### 5. BaseModel e TenantModel
- [x] 5.1 Criar arquivo `core/models.py`
- [x] 5.2 Implementar `BaseModel` abstrato com `id` (UUID), `created_at`, `updated_at`
- [x] 5.3 Implementar `TenantModel` abstrato herdando de `BaseModel` com FK para `Organization`
- [x] 5.4 Adicionar docstrings explicativas em ambas as classes
- [x] 5.5 Adicionar type hints em todos os campos e métodos

#### 6. Autenticação com e-mail
- [x] 6.1 Criar arquivo `core/backends.py` com `EmailAuthBackend`
- [x] 6.2 Implementar `authenticate()` usando e-mail ao invés de username
- [x] 6.3 Adicionar `AUTHENTICATION_BACKENDS` no `settings.py` apontando para o backend
- [x] 6.4 Adicionar docstring e type hints no backend

#### 7. Templates base
- [x] 7.1 Criar pasta `core/templates/`
- [x] 7.2 Criar `base.html` com estrutura HTML5, importação do CSS Tailwind e bloco `content`
- [x] 7.3 Criar estrutura de sidebar e topbar no `base.html`
- [x] 7.4 Aplicar paleta de cores definida no design system (fundo escuro, gradientes)
- [x] 7.5 Criar `base_auth.html` para páginas de login/cadastro (layout centralizado)
- [x] 7.6 Verificar responsividade do layout base em mobile e desktop

---

### Sprint 1 — Autenticação e Landing Page
**Objetivo:** Usuário consegue se cadastrar, fazer login, ver dashboard básico e a landing page pública.

#### 8. Landing page pública
- [x] 8.1 Criar view `LandingView` em `core/views.py` como `TemplateView`
- [x] 8.2 Criar template `core/templates/landing.html` estendendo `base_auth.html`
- [x] 8.3 Implementar seção hero com título, subtítulo e botões "Cadastre-se" e "Login"
- [x] 8.4 Aplicar gradiente de fundo e glow decorativo no hero
- [x] 8.5 Implementar seção de features (3 cards com ícones SVG e textos)
- [x] 8.6 Adicionar rodapé com nome do produto e ano
- [x] 8.7 Configurar rota `/` apontando para `LandingView` em `core/urls.py`
- [x] 8.8 Verificar responsividade da landing em mobile

#### 9. Cadastro de usuário
- [x] 9.1 Criar `core/forms.py` com `UserRegistrationForm` herdando de `UserCreationForm`
- [x] 9.2 Substituir campo `username` por `email` no formulário
- [x] 9.3 Adicionar campo `name` (nome completo) ao formulário
- [x] 9.4 Criar view `RegisterView` em `core/views.py` como `CreateView`
- [x] 9.5 Criar template `core/templates/register.html` com layout de card centralizado
- [x] 9.6 Aplicar classes do design system nos inputs e botão
- [x] 9.7 Implementar redirecionamento para dashboard após cadastro bem-sucedido
- [x] 9.8 Exibir mensagens de validação em português
- [x] 9.9 Configurar rota `/cadastro/` em `config/urls.py`

#### 10. Login de usuário
- [x] 10.1 Criar view `LoginView` customizada em `core/views.py` herdando de `auth.LoginView`
- [x] 10.2 Sobrescrever formulário para usar campo e-mail
- [x] 10.3 Criar template `core/templates/login.html` com card centralizado e glow
- [x] 10.4 Aplicar classes do design system no formulário
- [x] 10.5 Configurar `LOGIN_REDIRECT_URL = '/dashboard/'` no `settings.py`
- [x] 10.6 Configurar rota `/login/` em `config/urls.py`
- [x] 10.7 Exibir mensagem de erro clara para credenciais inválidas

#### 11. Logout
- [ ] 11.1 Usar `LogoutView` nativa do Django
- [ ] 11.2 Configurar `LOGOUT_REDIRECT_URL = '/'` no `settings.py`
- [ ] 11.3 Adicionar link de logout na topbar do `base.html`
- [ ] 11.4 Configurar rota `/logout/` em `config/urls.py`

#### 12. Dashboard principal
- [ ] 12.1 Criar view `DashboardView` em `core/views.py` como `LoginRequiredMixin` + `TemplateView`
- [ ] 12.2 Criar template `core/templates/dashboard.html` estendendo `base.html`
- [ ] 12.3 Implementar grid de 4 cards de métricas (assembleias, membros, etc.)
- [ ] 12.4 Aplicar classes do design system nos cards
- [ ] 12.5 Adicionar seção "Próximas assembleias" (placeholder vazio por ora)
- [ ] 12.6 Configurar rota `/dashboard/` em `config/urls.py`
- [ ] 12.7 Redirecionar `/` para `/dashboard/` se usuário já estiver logado

---

### Sprint 2 — Organizações e Membros
**Objetivo:** CRUD completo de organizações e membros funcionando.

#### 13. Model Organization
- [ ] 13.1 Criar `organizations/models.py` com classe `Organization` herdando de `BaseModel`
- [ ] 13.2 Adicionar campos: `name`, `type` (TextChoices), `cnpj`, `plan`
- [ ] 13.3 Definir `OrgType.choices`: condomínio, sindicato, associação
- [ ] 13.4 Adicionar `__str__`, `Meta`, docstring e type hints
- [ ] 13.5 Criar e aplicar migrations: `python manage.py makemigrations organizations`

#### 14. Model Member
- [ ] 14.1 Adicionar classe `Member` em `organizations/models.py` herdando de `TenantModel`
- [ ] 14.2 Adicionar campos: `user` (FK User opcional), `name`, `email`, `cpf`, `role`, `status`, `is_defaulter`
- [ ] 14.3 Definir `MemberRole.choices`: síndico/presidente, secretário, conselheiro, membro
- [ ] 14.4 Definir `MemberStatus.choices`: ativo, inativo, inadimplente
- [ ] 14.5 Adicionar `__str__`, `Meta`, docstring e type hints
- [ ] 14.6 Criar e aplicar migrations

#### 15. CRUD de Organization
- [ ] 15.1 Criar `organizations/forms.py` com `OrganizationForm`
- [ ] 15.2 Criar `organizations/views.py` com:
  - [ ] 15.2.1 `OrganizationListView` (`LoginRequiredMixin` + `ListView`)
  - [ ] 15.2.2 `OrganizationCreateView` (`LoginRequiredMixin` + `CreateView`)
  - [ ] 15.2.3 `OrganizationDetailView` (`LoginRequiredMixin` + `DetailView`)
  - [ ] 15.2.4 `OrganizationUpdateView` (`LoginRequiredMixin` + `UpdateView`)
- [ ] 15.3 Criar templates em `organizations/templates/organizations/`:
  - [ ] 15.3.1 `list.html` — tabela com organizações cadastradas
  - [ ] 15.3.2 `form.html` — formulário de criação/edição com design system
  - [ ] 15.3.3 `detail.html` — visão detalhada da organização
- [ ] 15.4 Criar `organizations/urls.py` e registrar em `config/urls.py`
- [ ] 15.5 Adicionar link "Organizações" na sidebar do `base.html`

#### 16. CRUD de Member
- [ ] 16.1 Criar `MemberForm` em `organizations/forms.py`
- [ ] 16.2 Adicionar views em `organizations/views.py`:
  - [ ] 16.2.1 `MemberListView`
  - [ ] 16.2.2 `MemberCreateView`
  - [ ] 16.2.3 `MemberUpdateView`
- [ ] 16.3 Criar templates:
  - [ ] 16.3.1 `members/list.html` — tabela com badges de status e papel
  - [ ] 16.3.2 `members/form.html` — formulário com design system
- [ ] 16.4 Adicionar rotas de membros em `organizations/urls.py`
- [ ] 16.5 Adicionar link "Membros" na sidebar

#### 17. Atualizar Dashboard com dados reais
- [ ] 17.1 Injetar contexto com total de organizações e membros na `DashboardView`
- [ ] 17.2 Exibir contagens nos cards do dashboard

---

### Sprint 3 — Assembleias e Convocações
**Objetivo:** CRUD de assembleias, fluxo de estados e registro de convocações.

#### 18. Model Assembly
- [ ] 18.1 Criar `assemblies/models.py` com classe `Assembly` herdando de `TenantModel`
- [ ] 18.2 Implementar `Status.choices` e `Mode.choices` como `TextChoices`
- [ ] 18.3 Adicionar campos: `title`, `description`, `status`, `mode`, `scheduled_at`, `started_at`, `ended_at`, `quorum_required`, `location`, `meeting_url`
- [ ] 18.4 Implementar método `clean()` com validações de negócio
- [ ] 18.5 Implementar properties: `is_open`, `total_credentials`, `quorum_reached`
- [ ] 18.6 Adicionar docstring, type hints e `__str__`
- [ ] 18.7 Criar migrations

#### 19. Model Convocation
- [ ] 19.1 Adicionar classe `Convocation` em `assemblies/models.py`
- [ ] 19.2 Implementar `Channel.choices`
- [ ] 19.3 Adicionar campos: `assembly`, `channel`, `sent_at`, `is_second_call`, `delivery_status`, `notes`
- [ ] 19.4 Adicionar docstring, type hints e `__str__`
- [ ] 19.5 Criar migrations

#### 20. Model Proxy
- [ ] 20.1 Adicionar classe `Proxy` em `assemblies/models.py`
- [ ] 20.2 Adicionar campos e FKs com `related_name` corretos
- [ ] 20.3 Implementar `clean()`: grantor ≠ proxy_member
- [ ] 20.4 Adicionar `UniqueConstraint`: um grantor por assembleia
- [ ] 20.5 Criar migrations

#### 21. Model Credential
- [ ] 21.1 Adicionar classe `Credential` em `assemblies/models.py`
- [ ] 21.2 Adicionar campos: `assembly`, `member`, `channel`, `checked_in_at`, `ip_address`, `device_info`, `access_token`, `token_used_at`
- [ ] 21.3 Implementar `clean()`: bloquear inadimplente
- [ ] 21.4 Adicionar `UniqueConstraint`: um check-in por membro por assembleia
- [ ] 21.5 Criar migrations

#### 22. CRUD de Assembly
- [ ] 22.1 Criar `assemblies/forms.py` com `AssemblyForm`
- [ ] 22.2 Criar `assemblies/views.py` com:
  - [ ] 22.2.1 `AssemblyListView` com filtro por status
  - [ ] 22.2.2 `AssemblyCreateView`
  - [ ] 22.2.3 `AssemblyDetailView`
  - [ ] 22.2.4 `AssemblyUpdateView`
- [ ] 22.3 Criar templates:
  - [ ] 22.3.1 `assemblies/list.html` — tabela com badges de status
  - [ ] 22.3.2 `assemblies/form.html`
  - [ ] 22.3.3 `assemblies/detail.html` — visão completa com abas (pauta, credenciados, convocações)
- [ ] 22.4 Criar `assemblies/urls.py` e registrar em `config/urls.py`

#### 23. Fluxo de estados da Assembly
- [ ] 23.1 Criar view `AssemblyStartView` (muda status para `open`)
- [ ] 23.2 Criar view `AssemblyCloseView` (muda status para `closed`)
- [ ] 23.3 Adicionar validações: só inicia com status `convoked`, só fecha com status `open`
- [ ] 23.4 Adicionar botões de ação contextuais no `detail.html` (conforme status atual)

#### 24. Convocações
- [ ] 24.1 Criar `ConvocationForm` em `assemblies/forms.py`
- [ ] 24.2 Criar `ConvocationCreateView` em `assemblies/views.py`
- [ ] 24.3 Template inline no `detail.html` da assembleia (lista + formulário de adição)
- [ ] 24.4 Registrar rotas em `assemblies/urls.py`

#### 25. Procurações
- [ ] 25.1 Criar `ProxyForm`
- [ ] 25.2 Criar `ProxyCreateView`
- [ ] 25.3 Template inline na aba de procurações do `detail.html`

#### 26. Credenciamento
- [ ] 26.1 Criar `CredentialForm`
- [ ] 26.2 Criar `CredentialCreateView` com validação de inadimplência
- [ ] 26.3 Exibir contador de credenciados e indicador de quórum no `detail.html`
- [ ] 26.4 Registrar rotas em `assemblies/urls.py`

---

### Sprint 4 — Votação
**Objetivo:** Sistema de votação completo com integridade e suporte a votação secreta.

#### 27. Model AgendaItem
- [ ] 27.1 Criar `voting/models.py` com classe `AgendaItem`
- [ ] 27.2 Implementar `QuorumType`, `VoteMode` e `Status` como `TextChoices`
- [ ] 27.3 Adicionar campos e `UniqueConstraint` de `order_index`
- [ ] 27.4 Implementar `clean()` para proteger ordem durante assembleia aberta
- [ ] 27.5 Implementar `is_secret`, `total_votes`, `get_result()`, `check_quorum_reached()`
- [ ] 27.6 Adicionar docstring, type hints, `__str__` e migrations

#### 28. Model Vote
- [ ] 28.1 Adicionar classe `Vote` em `voting/models.py`
- [ ] 28.2 Adicionar campos: `agenda_item`, `label`, `total_count`
- [ ] 28.3 Implementar método `increment()` com `F()` expression (atômico)
- [ ] 28.4 Adicionar `UniqueConstraint` de label por item
- [ ] 28.5 Criar migrations

#### 29. Model VoteRecord
- [ ] 29.1 Adicionar classe `VoteRecord` em `voting/models.py`
- [ ] 29.2 Adicionar todos os campos com FKs e campos de hash
- [ ] 29.3 Implementar `_compute_integrity_hash()`, `_compute_member_hash()`, `_compute_vote_hash()`
- [ ] 29.4 Implementar `clean()` com todas as validações de negócio
- [ ] 29.5 Implementar `save()` com lógica de voto secreto e integridade
- [ ] 29.6 Implementar `delete()` bloqueado
- [ ] 29.7 Implementar `verify_integrity()` para auditoria
- [ ] 29.8 Adicionar `UniqueConstraints` para duplo voto (aberto e secreto)
- [ ] 29.9 Criar migrations

#### 30. CRUD de AgendaItem
- [ ] 30.1 Criar `voting/forms.py` com `AgendaItemForm` e `VoteOptionFormSet`
- [ ] 30.2 Criar `voting/views.py` com:
  - [ ] 30.2.1 `AgendaItemCreateView`
  - [ ] 30.2.2 `AgendaItemUpdateView`
  - [ ] 30.2.3 `AgendaItemOpenView` (muda status para `open`)
  - [ ] 30.2.4 `AgendaItemCloseView` (muda status para `closed`)
- [ ] 30.3 Templates inline na aba de pauta do `detail.html` da assembleia
- [ ] 30.4 Exibir resultado em tempo real ao fechar o item

#### 31. Registro de Voto
- [ ] 31.1 Criar `VoteForm` em `voting/forms.py`
- [ ] 31.2 Criar `CastVoteView` em `voting/views.py`
- [ ] 31.3 Chamar `full_clean()` antes do `save()` para acionar `clean()`
- [ ] 31.4 Template de votação com opções renderizadas como botões/radio
- [ ] 31.5 Exibir confirmação de voto registrado
- [ ] 31.6 Exibir placar parcial (apenas contagens) durante votação aberta

---

### Sprint 5 — Ata
**Objetivo:** Geração automática de ata e sistema de assinaturas.

#### 32. Model Minutes
- [ ] 32.1 Criar `minutes/models.py` com classe `Minutes` herdando de `TenantModel`
- [ ] 32.2 Adicionar campos: `assembly`, `content`, `status`, `document_url`, `generated_at`, `approved_at`
- [ ] 32.3 Implementar `save()` bloqueado para edição após aprovação
- [ ] 32.4 Adicionar docstring, type hints e migrations

#### 33. Model MinuteSignature
- [ ] 33.1 Adicionar classe `MinuteSignature` em `minutes/models.py`
- [ ] 33.2 Adicionar campos: `minutes`, `member`, `role`, `signature_token`, `signed_at`
- [ ] 33.3 Gerar `signature_token` automaticamente no `save()`
- [ ] 33.4 Criar migrations

#### 34. Geração automática da ata
- [ ] 34.1 Criar função `generate_minutes_content(assembly)` em `minutes/utils.py`
- [ ] 34.2 Montar texto da ata com: cabeçalho, quórum, itens votados, resultados e deliberações
- [ ] 34.3 Chamar a função automaticamente ao executar `AssemblyCloseView`
- [ ] 34.4 Adicionar type hints e docstring na função

#### 35. Views de Ata
- [ ] 35.1 Criar `minutes/views.py` com:
  - [ ] 35.1.1 `MinutesDetailView` — exibe o conteúdo da ata
  - [ ] 35.1.2 `MinutesApproveView` — muda status para `approved`
  - [ ] 35.1.3 `MinutesSignView` — registra assinatura de um membro
- [ ] 35.2 Criar templates:
  - [ ] 35.2.1 `minutes/detail.html` — texto da ata + lista de assinaturas + botão de assinar
  - [ ] 35.2.2 Indicação visual de ata aprovada (badge + bloqueio de edição)
- [ ] 35.3 Criar `minutes/urls.py` e registrar em `config/urls.py`

---

### Sprint 6 — Auditoria e Finalização do MVP
**Objetivo:** Logs de auditoria funcionando, dashboard completo e projeto pronto para uso.

#### 36. Model AuditLog
- [ ] 36.1 Criar `audit/models.py` com classe `AuditLog` herdando de `BaseModel`
- [ ] 36.2 Adicionar campos: `assembly`, `actor`, `action`, `payload`, `ip_address`, `occurred_at`
- [ ] 36.3 Implementar `save()` bloqueado para edição
- [ ] 36.4 Implementar `delete()` bloqueado
- [ ] 36.5 Criar migrations

#### 37. Signals de auditoria
- [ ] 37.1 Criar `audit/signals.py`
- [ ] 37.2 Criar signal `post_save` para `VoteRecord` → registra voto no log
- [ ] 37.3 Criar signal `post_save` para `Credential` → registra check-in no log
- [ ] 37.4 Criar signal `post_save` para `Assembly` (mudança de status) → registra no log
- [ ] 37.5 Criar signal `post_save` para `Minutes` (mudança de status) → registra no log
- [ ] 37.6 Criar `audit/apps.py` e registrar signals no método `ready()`

#### 38. View de auditoria
- [ ] 38.1 Criar `audit/views.py` com `AuditLogListView` filtrada por assembleia
- [ ] 38.2 Criar template `audit/templates/audit/list.html` com tabela cronológica
- [ ] 38.3 Criar `audit/urls.py` e registrar em `config/urls.py`
- [ ] 38.4 Adicionar link de auditoria no `detail.html` da assembleia

#### 39. Dashboard final
- [ ] 39.1 Atualizar `DashboardView` com contagens reais de todas as entidades
- [ ] 39.2 Implementar seção "Próximas assembleias" com dados reais
- [ ] 39.3 Implementar seção "Assembleias em andamento" com link direto
- [ ] 39.4 Verificar responsividade do dashboard em mobile

#### 40. Revisão final do MVP
- [ ] 40.1 Revisar todas as rotas e verificar proteção com `LoginRequiredMixin`
- [ ] 40.2 Verificar se todas as queries filtram por `org_id` (isolamento de tenant)
- [ ] 40.3 Verificar se todos os formulários têm token CSRF
- [ ] 40.4 Revisar mensagens de erro e sucesso em português em todos os templates
- [ ] 40.5 Executar `ruff check .` e corrigir todos os avisos
- [ ] 40.6 Verificar se todos os models têm `created_at` e `updated_at`
- [ ] 40.7 Verificar se todas as funções e classes têm docstring e type hints
- [ ] 40.8 Testar fluxo completo: cadastro → organização → membros → assembleia → votação → ata
- [ ] 40.9 Criar `README.md` com instruções de instalação e uso

---

### Sprint 7 — Backlog (pós-MVP)
> Itens não implementados no MVP. Priorizar conforme feedback dos primeiros usuários.

- [ ] 41.1 Docker e docker-compose
- [ ] 41.2 Testes automatizados (pytest-django)
- [ ] 41.3 Envio real de e-mail de convocação (SMTP)
- [ ] 41.4 Download da ata em PDF
- [ ] 41.5 Filtros e buscas avançadas em listagens
- [ ] 41.6 Paginação nas listagens
- [ ] 41.7 Troca de organização ativa (multi-org por usuário)
- [ ] 41.8 Exportação de resultados de votação em CSV
- [ ] 41.9 Notificações in-app
- [ ] 41.10 Migração para PostgreSQL

---

*Documento gerado em 2026-04-30. Versão 1.0.*