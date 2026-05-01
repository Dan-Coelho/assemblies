# PRD — Sistema de Gestão de Assembleias
**Versão:** 1.0  
**Data:** 2026-04-30  
**Status:** Em elaboração  

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Sobre o Produto](#2-sobre-o-produto)
3. [Propósito](#3-propósito)
4. [Público-alvo](#4-público-alvo)
5. [Objetivos](#5-objetivos)
6. [Requisitos Funcionais](#6-requisitos-funcionais)
7. [Requisitos Não-Funcionais](#7-requisitos-não-funcionais)
8. [Arquitetura Técnica](#8-arquitetura-técnica)
9. [Design System](#9-design-system)
10. [User Stories](#10-user-stories)
11. [Métricas de Sucesso](#11-métricas-de-sucesso)
12. [Riscos e Mitigações](#12-riscos-e-mitigações)
13. [Lista de Tarefas por Sprint](#13-lista-de-tarefas-por-sprint)

---

## 1. Visão Geral

O **AssembleiaApp** é uma plataforma web SaaS de gestão de assembleias voltada para condomínios, sindicatos e associações. O sistema digitaliza e centraliza todo o ciclo de vida de uma assembleia: da convocação ao arquivamento da ata, passando pelo credenciamento de membros, votações (presenciais, remotas ou híbridas) e geração automática de ata com assinaturas digitais.

O produto resolve um problema crônico dessas organizações: a gestão de assembleias é feita hoje em papel, planilhas e grupos de WhatsApp, gerando risco jurídico, falta de rastreabilidade e retrabalho administrativo.

---

## 2. Sobre o Produto

| Atributo | Detalhe |
|---|---|
| **Nome** | AssembleiaApp |
| **Tipo** | Aplicação web SaaS multi-tenant |
| **Acesso** | Navegador (desktop e mobile) |
| **Stack principal** | Python 3.12+, Django 5.x, TailwindCSS, SQLite |
| **Autenticação** | Email + senha (sistema nativo Django) |
| **Modelo de dados** | Multi-tenant por organização (`org_id` em todas as entidades) |
| **Fase inicial** | MVP sem Docker e sem testes automatizados |

---

## 3. Propósito

Oferecer uma ferramenta simples, segura e juridicamente aderente para que administradores de condomínios, sindicatos e associações possam:

- Convocar assembleias com rastreabilidade de entrega
- Conduzir votações com integridade auditável
- Gerar atas padronizadas e com assinaturas digitais
- Manter histórico completo de todas as deliberações

O sistema deve eliminar o risco de assembleias inválidas por falha de quórum, erro de convocação ou ausência de documentação adequada.

---

## 4. Público-alvo

| Perfil | Descrição |
|---|---|
| **Síndico / Presidente** | Administrador da organização. Cria e conduz assembleias. Usuário primário. |
| **Secretário / Operador** | Auxilia no credenciamento e registro durante a assembleia. |
| **Condômino / Associado / Filiado** | Participa das assembleias, vota e assina atas. Usuário secundário. |
| **Conselheiro / Fiscal** | Acompanha as deliberações, sem permissão de gestão. |

---

## 5. Objetivos

### Objetivos de Negócio
- Reduzir o tempo de preparação de uma assembleia em pelo menos 60%
- Eliminar assembleias inválidas por falha documental
- Garantir rastreabilidade completa de convocações e votos

### Objetivos de Produto (MVP)
- Permitir cadastro de organizações e membros
- Criar e publicar assembleias com pauta definida
- Realizar credenciamento híbrido (presencial + online)
- Conduzir votações abertas e secretas com integridade
- Gerar ata automaticamente ao final da assembleia
- Manter log de auditoria imutável de todas as ações

---

## 6. Requisitos Funcionais

### RF-01 — Autenticação e Usuários
- RF-01.1: Login via e-mail e senha (não por username)
- RF-01.2: Logout com encerramento de sessão
- RF-01.3: Cadastro de novo usuário via página pública
- RF-01.4: Redirecionamento para dashboard após login
- RF-01.5: Página pública de apresentação do sistema com opções de cadastro e login

### RF-02 — Organizações
- RF-02.1: Cadastro de organização (nome, tipo, CNPJ)
- RF-02.2: Tipos suportados: condomínio, sindicato, associação
- RF-02.3: Um usuário pode pertencer a múltiplas organizações
- RF-02.4: Cada organização tem membros com papéis distintos

### RF-03 — Membros
- RF-03.1: Cadastro de membros vinculados a uma organização
- RF-03.2: Papéis: síndico/presidente, secretário, conselheiro, membro
- RF-03.3: Status: ativo, inativo, inadimplente
- RF-03.4: Inadimplente pode ser credenciado mas não pode votar
- RF-03.5: Listagem, edição e inativação de membros

### RF-04 — Assembleias
- RF-04.1: Criar assembleia com título, descrição, data, modo e quórum mínimo
- RF-04.2: Modos: presencial, remota, híbrida
- RF-04.3: Fluxo de estados: Rascunho → Convocada → Em andamento → Encerrada → Arquivada
- RF-04.4: Listagem de assembleias com filtro por status
- RF-04.5: Visualização detalhada de cada assembleia

### RF-05 — Convocações
- RF-05.1: Registrar convocação com canal (e-mail, WhatsApp, SMS, correio, edital)
- RF-05.2: Registrar se é primeira ou segunda convocação
- RF-05.3: Registrar data de envio e status de entrega (JSON)

### RF-06 — Procurações
- RF-06.1: Registrar procuração manualmente (outorgante → procurador)
- RF-06.2: Upload opcional do documento PDF
- RF-06.3: Um membro pode outorgar apenas uma procuração por assembleia
- RF-06.4: Procurador precisa estar credenciado para votar em nome do outorgante

### RF-07 — Credenciamento
- RF-07.1: Registrar check-in de membros (presencial ou online)
- RF-07.2: Impedir duplo credenciamento do mesmo membro
- RF-07.3: Impedir credenciamento de inadimplente
- RF-07.4: Exibir contagem de credenciados em tempo real
- RF-07.5: Verificar automaticamente se quórum mínimo foi atingido

### RF-08 — Pauta e Votação
- RF-08.1: Adicionar itens de pauta com ordem, título e descrição
- RF-08.2: Cada item define tipo de quórum (simples, absoluto, 2/3, unanimidade) e modo (aberto, secreto)
- RF-08.3: Itens votados em ordem sequencial
- RF-08.4: Abertura e encerramento de cada item pelo administrador
- RF-08.5: Registro de voto por membro credenciado
- RF-08.6: Votação aberta: member_id visível no registro
- RF-08.7: Votação secreta: member_id substituído por hash SHA-256
- RF-08.8: Contador de votos atualizado de forma atômica (sem race condition)
- RF-08.9: Impedimento de duplo voto por constraint de banco
- RF-08.10: Cálculo automático de resultado conforme tipo de quórum

### RF-09 — Ata
- RF-09.1: Geração automática da ata ao encerrar a assembleia
- RF-09.2: Ata contém: dados da assembleia, quórum, itens votados, resultados e deliberações
- RF-09.3: Ata pode ser revisada antes da aprovação
- RF-09.4: Registro de assinaturas (síndico, secretário, ao menos um membro)
- RF-09.5: Ata aprovada torna-se imutável
- RF-09.6: Download da ata em formato legível

### RF-10 — Auditoria
- RF-10.1: Log imutável de todas as ações relevantes do sistema
- RF-10.2: Cada log contém: ator, ação, payload JSON, IP, timestamp
- RF-10.3: Logs nunca podem ser editados ou deletados
- RF-10.4: Visualização de logs por assembleia (apenas para administradores)

### RF-11 — Dashboard
- RF-11.1: Exibir resumo das assembleias (total, em andamento, encerradas)
- RF-11.2: Exibir atalhos para ações rápidas
- RF-11.3: Exibir próximas assembleias agendadas

---

### Fluxos de UX — Mermaid

#### Fluxo principal do sistema

```mermaid
flowchart TD
    A([Usuário acessa o site]) --> B{Tem conta?}
    B -- Não --> C[Página de cadastro]
    C --> D[Cria conta com e-mail e senha]
    D --> E[Dashboard]
    B -- Sim --> F[Página de login]
    F --> G{Credenciais válidas?}
    G -- Não --> F
    G -- Sim --> E

    E --> H{Ação desejada}
    H --> I[Gerenciar Organização]
    H --> J[Gerenciar Membros]
    H --> K[Gerenciar Assembleias]

    K --> L{Nova ou existente?}
    L -- Nova --> M[Criar assembleia]
    M --> N[Adicionar itens de pauta]
    N --> O[Registrar convocação]
    O --> P[Assembleia: Convocada]

    L -- Existente --> Q{Status atual?}
    Q -- Convocada --> R[Iniciar assembleia]
    R --> S[Credenciar membros]
    S --> T{Quórum atingido?}
    T -- Não --> S
    T -- Sim --> U[Abrir votação do item]
    U --> V[Membros votam]
    V --> W[Encerrar item]
    W --> X{Mais itens?}
    X -- Sim --> U
    X -- Não --> Y[Encerrar assembleia]
    Y --> Z[Gerar ata automaticamente]
    Z --> AA[Coletar assinaturas]
    AA --> AB([Ata aprovada e arquivada])
```

#### Fluxo de votação

```mermaid
flowchart TD
    A([Item de pauta aberto]) --> B[Membro acessa votação]
    B --> C{Está credenciado?}
    C -- Não --> D([Bloqueado — sem credencial])
    C -- Sim --> E{Está inadimplente?}
    E -- Sim --> F([Bloqueado — inadimplente])
    E -- Não --> G{Já votou neste item?}
    G -- Sim --> H([Bloqueado — duplo voto])
    G -- Não --> I{Tipo de votação?}
    I -- Aberta --> J[Registra voto com member_id visível]
    I -- Secreta --> K[Registra voto com hash SHA-256]
    J --> L[Incrementa contador atomicamente]
    K --> L
    L --> M[Gera integrity_hash]
    M --> N[Registra no AuditLog]
    N --> O([Voto confirmado])
```

---

## 7. Requisitos Não-Funcionais

### RNF-01 — Desempenho
- Páginas devem carregar em menos de 2 segundos em conexão padrão
- Operações de votação devem ser atômicas e sem race condition

### RNF-02 — Segurança
- Autenticação obrigatória em todas as rotas internas
- Isolamento de dados por organização em todas as queries
- Hashing SHA-256 para dados sensíveis de votação secreta
- Logs de auditoria imutáveis (sem UPDATE/DELETE permitido)
- Proteção CSRF nativa do Django em todos os formulários

### RNF-03 — Usabilidade
- Interface responsiva (mobile-first)
- Design dark com gradientes e identidade visual consistente
- Todas as mensagens de interface em português brasileiro
- Feedback visual claro para ações (sucesso, erro, aviso)

### RNF-04 — Manutenibilidade
- Código em inglês, com type hints e docstrings em todas as funções e classes
- Linting com ruff
- Logging estruturado no terminal para todas as operações relevantes
- Separação de responsabilidades por app Django
- Código simples, sem over-engineering

### RNF-05 — Compatibilidade
- Suporte aos navegadores modernos: Chrome, Firefox, Safari, Edge
- Layout responsivo para telas a partir de 320px

### RNF-06 — Banco de Dados
- SQLite como banco padrão (fase inicial)
- Todos os models com `created_at` e `updated_at`
- UUIDs como chaves primárias
- Constraints de unicidade definidas no nível do banco

---

## 8. Arquitetura Técnica

### Stack

| Camada | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.13+ |
| Framework web | Django | 6.x |
| Frontend | Django Template Language + TailwindCSS | 3.x |
| Banco de dados | SQLite | Nativo Django |
| Gerenciador de dependências | uv | latest |
| Linter / Formatter | ruff | latest |
| Logging | logging (stdlib Python) | nativo |

### Estrutura de Pastas

```
projeto/
├── core/
│   ├── models.py          # BaseModel, TenantModel (abstratos)
│   ├── middleware.py       # TenantMiddleware e outros
│   ├── permissions.py      # Permissões customizadas
│   ├── context_processors.py
│   ├── templates/
│   │   ├── base.html       # Layout base do sistema
│   │   ├── landing.html    # Página pública
│   │   └── dashboard.html  # Dashboard principal
│   └── static/
│       └── css/output.css  # TailwindCSS compilado
├── config/                 # settings.py, urls.py, wsgi.py
├── organizations/
│   ├── models.py           # Organization, Member
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templates/organizations/
├── assemblies/
│   ├── models.py           # Assembly, Convocation, Credential, Proxy
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── signals.py
│   └── templates/assemblies/
├── voting/
│   ├── models.py           # AgendaItem, Vote, VoteRecord
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── signals.py
│   └── templates/voting/
├── minutes/
│   ├── models.py           # Minutes, MinuteSignature
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── templates/minutes/
├── audit/
│   ├── models.py           # AuditLog
│   ├── views.py
│   ├── urls.py
│   └── templates/audit/
├── .gitignore
├── .python-version
├── manage.py
├── pyproject.toml
├── README.md
├── uv.lock
└── erd_assembleia_mermaid.html
```

### Schema de Dados (ERD)

```mermaid
erDiagram
  ORGANIZATIONS ||--o{ MEMBERS : "possui"
  ORGANIZATIONS ||--o{ ASSEMBLIES : "realiza"
  ASSEMBLIES ||--o{ CONVOCATIONS : "emite"
  ASSEMBLIES ||--o{ CREDENTIALS : "credencia"
  ASSEMBLIES ||--o{ AGENDA_ITEMS : "contém"
  ASSEMBLIES ||--o{ MINUTES : "gera"
  ASSEMBLIES ||--o{ AUDIT_LOGS : "rastreia"
  MEMBERS ||--o{ CREDENTIALS : "check-in"
  MEMBERS ||--o{ PROXIES : "outorga"
  MEMBERS ||--o{ PROXIES : "recebe"
  MEMBERS ||--o{ VOTE_RECORDS : "emite"
  MEMBERS ||--o{ MINUTE_SIGNATURES : "assina"
  AGENDA_ITEMS ||--o{ VOTES : "registra"
  AGENDA_ITEMS ||--o{ VOTE_RECORDS : "acumula"
  VOTES ||--o{ VOTE_RECORDS : "referencia"
  MINUTES ||--o{ MINUTE_SIGNATURES : "exige"
  PROXIES ||--o{ VOTE_RECORDS : "autoriza"

  ORGANIZATIONS {
    uuid id PK
    string name
    string type
    string cnpj
    string plan
    timestamp created_at
    timestamp updated_at
  }

  MEMBERS {
    uuid id PK
    uuid org_id FK
    string name
    string email
    string cpf
    string role
    string status
    boolean is_defaulter
    timestamp created_at
    timestamp updated_at
  }

  ASSEMBLIES {
    uuid id PK
    uuid org_id FK
    uuid created_by FK
    string title
    string status
    string mode
    timestamp scheduled_at
    timestamp started_at
    timestamp ended_at
    int quorum_required
    timestamp created_at
    timestamp updated_at
  }

  CONVOCATIONS {
    uuid id PK
    uuid assembly_id FK
    string channel
    timestamp sent_at
    json delivery_status
    timestamp created_at
    timestamp updated_at
  }

  CREDENTIALS {
    uuid id PK
    uuid assembly_id FK
    uuid member_id FK
    string channel
    timestamp checked_in_at
    string ip_address
    string device_info
    timestamp created_at
    timestamp updated_at
  }

  PROXIES {
    uuid id PK
    uuid assembly_id FK
    uuid grantor_id FK
    uuid proxy_id FK
    string document_url
    boolean is_active
    timestamp created_at
    timestamp updated_at
  }

  AGENDA_ITEMS {
    uuid id PK
    uuid assembly_id FK
    int order_index
    string title
    string quorum_type
    string vote_mode
    string status
    timestamp created_at
    timestamp updated_at
  }

  VOTES {
    uuid id PK
    uuid agenda_item_id FK
    string label
    int total_count
    timestamp created_at
    timestamp updated_at
  }

  VOTE_RECORDS {
    uuid id PK
    uuid agenda_item_id FK
    uuid member_id FK
    uuid vote_id FK
    uuid proxy_id FK
    string channel
    string ip_address
    string member_id_hash
    string vote_label_hash
    string integrity_hash
    timestamp voted_at
    timestamp created_at
    timestamp updated_at
  }

  MINUTES {
    uuid id PK
    uuid assembly_id FK
    text content
    string status
    string document_url
    timestamp generated_at
    timestamp approved_at
    timestamp created_at
    timestamp updated_at
  }

  MINUTE_SIGNATURES {
    uuid id PK
    uuid minutes_id FK
    uuid member_id FK
    string role
    string signature_token
    timestamp signed_at
    timestamp created_at
    timestamp updated_at
  }

  AUDIT_LOGS {
    uuid id PK
    uuid assembly_id FK
    uuid actor_id FK
    string action
    jsonb payload
    string ip_address
    timestamp occurred_at
    timestamp created_at
  }
```

---

## 9. Design System

### Filosofia Visual

Interface inspirada em dashboards SaaS modernos: fundo escuro profundo com superfícies em tons de cinza-azulado, gradientes vibrantes em roxo e azul elétrico como cor de destaque, e tipografia limpa sem serifa. O resultado é uma interface que transmite confiança e profissionalismo — adequada ao contexto jurídico-administrativo das assembleias.

---

### Paleta de Cores

```
/* Fundos */
--bg-base:       #0F0F1A   /* Fundo da página */
--bg-surface:    #1A1A2E   /* Cards e painéis */
--bg-elevated:   #16213E   /* Modais, dropdowns */
--bg-border:     #2A2A45   /* Bordas e divisores */

/* Gradiente de destaque */
--grad-primary:  linear-gradient(135deg, #7C3AED, #2563EB)
--grad-subtle:   linear-gradient(135deg, #7C3AED22, #2563EB22)
--grad-hover:    linear-gradient(135deg, #6D28D9, #1D4ED8)

/* Cores sólidas */
--accent-purple: #7C3AED   /* Ações primárias */
--accent-blue:   #2563EB   /* Links e destaques */
--accent-teal:   #0D9488   /* Sucesso e confirmação */
--accent-amber:  #D97706   /* Avisos */
--accent-red:    #DC2626   /* Erros e perigos */

/* Texto */
--text-primary:  #F1F5F9   /* Títulos e rótulos */
--text-secondary:#94A3B8   /* Textos de apoio */
--text-muted:    #475569   /* Placeholders */
```

### Tipografia

```
/* Fonte principal */
font-family: 'Inter', system-ui, sans-serif;

/* Escala */
--text-xs:   0.75rem   / 12px  — labels, badges
--text-sm:   0.875rem  / 14px  — texto de apoio, inputs
--text-base: 1rem      / 16px  — corpo padrão
--text-lg:   1.125rem  / 18px  — subtítulos de card
--text-xl:   1.25rem   / 20px  — títulos de seção
--text-2xl:  1.5rem    / 24px  — títulos de página
--text-4xl:  2.25rem   / 36px  — hero da landing

/* Pesos */
font-weight: 400   — corpo
font-weight: 500   — subtítulos, labels
font-weight: 600   — títulos e botões
font-weight: 700   — hero e headings principais
```

### Classes TailwindCSS — Componentes Base

#### Layout Base
```html
<!-- Fundo da página -->
<body class="bg-[#0F0F1A] text-slate-100 font-sans antialiased min-h-screen">

<!-- Container padrão -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

<!-- Card / Painel -->
<div class="bg-[#1A1A2E] border border-[#2A2A45] rounded-xl p-6 shadow-lg">

<!-- Card com gradiente sutil -->
<div class="bg-gradient-to-br from-[#7C3AED11] to-[#2563EB11]
            border border-[#7C3AED33] rounded-xl p-6">
```

#### Botões
```html
<!-- Botão primário (gradiente) -->
<button class="bg-gradient-to-r from-violet-600 to-blue-600
               hover:from-violet-700 hover:to-blue-700
               text-white font-semibold px-6 py-2.5 rounded-lg
               transition-all duration-200 shadow-lg
               shadow-violet-500/25 focus:outline-none
               focus:ring-2 focus:ring-violet-500 focus:ring-offset-2
               focus:ring-offset-[#0F0F1A]">
  Ação Primária
</button>

<!-- Botão secundário (outline) -->
<button class="border border-[#2A2A45] hover:border-violet-500
               text-slate-300 hover:text-white font-medium
               px-6 py-2.5 rounded-lg transition-all duration-200
               hover:bg-violet-500/10">
  Ação Secundária
</button>

<!-- Botão de perigo -->
<button class="bg-red-600/20 hover:bg-red-600/30 border border-red-500/50
               text-red-400 hover:text-red-300 font-medium
               px-6 py-2.5 rounded-lg transition-all duration-200">
  Excluir
</button>

<!-- Botão pequeno / badge-action -->
<button class="text-xs font-medium px-3 py-1 rounded-md
               bg-violet-500/20 text-violet-300
               hover:bg-violet-500/30 transition-colors">
  Ver detalhes
</button>
```

#### Inputs e Formulários
```html
<!-- Label -->
<label class="block text-sm font-medium text-slate-300 mb-1.5">
  Nome do campo
</label>

<!-- Input padrão -->
<input type="text"
       class="w-full bg-[#0F0F1A] border border-[#2A2A45]
              focus:border-violet-500 focus:ring-1 focus:ring-violet-500
              text-slate-100 placeholder-slate-500 rounded-lg
              px-4 py-2.5 text-sm transition-colors outline-none">

<!-- Select -->
<select class="w-full bg-[#0F0F1A] border border-[#2A2A45]
               focus:border-violet-500 focus:ring-1 focus:ring-violet-500
               text-slate-100 rounded-lg px-4 py-2.5 text-sm
               transition-colors outline-none">

<!-- Textarea -->
<textarea class="w-full bg-[#0F0F1A] border border-[#2A2A45]
                 focus:border-violet-500 focus:ring-1 focus:ring-violet-500
                 text-slate-100 placeholder-slate-500 rounded-lg
                 px-4 py-2.5 text-sm transition-colors outline-none resize-none">

<!-- Fieldset / grupo de campos -->
<div class="space-y-4 bg-[#1A1A2E] border border-[#2A2A45]
            rounded-xl p-6">
  <!-- campos aqui -->
</div>

<!-- Mensagem de erro -->
<p class="mt-1.5 text-xs text-red-400 flex items-center gap-1">
  <span>⚠</span> Mensagem de erro aqui
</p>
```

#### Badges de Status
```html
<!-- Status: Rascunho -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full
             text-xs font-medium bg-slate-500/20 text-slate-400
             border border-slate-500/30">
  Rascunho
</span>

<!-- Status: Convocada -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full
             text-xs font-medium bg-blue-500/20 text-blue-400
             border border-blue-500/30">
  Convocada
</span>

<!-- Status: Em andamento -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full
             text-xs font-medium bg-violet-500/20 text-violet-400
             border border-violet-500/30">
  Em andamento
</span>

<!-- Status: Encerrada -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full
             text-xs font-medium bg-teal-500/20 text-teal-400
             border border-teal-500/30">
  Encerrada
</span>

<!-- Status: Arquivada -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full
             text-xs font-medium bg-amber-500/20 text-amber-400
             border border-amber-500/30">
  Arquivada
</span>
```

#### Navegação (Sidebar)
```html
<aside class="w-64 bg-[#1A1A2E] border-r border-[#2A2A45]
              min-h-screen flex flex-col">

  <!-- Logo -->
  <div class="p-6 border-b border-[#2A2A45]">
    <span class="text-xl font-bold bg-gradient-to-r from-violet-400
                 to-blue-400 bg-clip-text text-transparent">
      AssembleiaApp
    </span>
  </div>

  <!-- Menu item ativo -->
  <a href="#" class="flex items-center gap-3 px-4 py-3 mx-2 rounded-lg
                     bg-gradient-to-r from-violet-600/20 to-blue-600/20
                     border border-violet-500/30 text-violet-300
                     font-medium text-sm">
    <svg><!-- ícone --></svg>
    Assembleias
  </a>

  <!-- Menu item inativo -->
  <a href="#" class="flex items-center gap-3 px-4 py-3 mx-2 rounded-lg
                     text-slate-400 hover:text-slate-200
                     hover:bg-white/5 font-medium text-sm
                     transition-colors">
    <svg><!-- ícone --></svg>
    Membros
  </a>
</aside>
```

#### Grid de Cards para Dashboard
```html
<!-- Grid de métricas (4 colunas) -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

  <!-- Card de métrica -->
  <div class="bg-[#1A1A2E] border border-[#2A2A45] rounded-xl p-5
              hover:border-violet-500/50 transition-colors group">
    <p class="text-sm text-slate-400 font-medium">Assembleias ativas</p>
    <p class="text-3xl font-bold text-slate-100 mt-2">12</p>
    <p class="text-xs text-teal-400 mt-1">↑ 3 este mês</p>
  </div>
</div>

<!-- Grid de conteúdo (lista + detalhe) -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <div class="lg:col-span-2"> <!-- lista --> </div>
  <div class="lg:col-span-1"> <!-- detalhe / ações --> </div>
</div>
```

#### Tabela
```html
<div class="bg-[#1A1A2E] border border-[#2A2A45] rounded-xl overflow-hidden">
  <table class="w-full text-sm">
    <thead>
      <tr class="border-b border-[#2A2A45] bg-[#0F0F1A]/50">
        <th class="px-6 py-3 text-left text-xs font-semibold
                   text-slate-400 uppercase tracking-wider">
          Nome
        </th>
      </tr>
    </thead>
    <tbody class="divide-y divide-[#2A2A45]">
      <tr class="hover:bg-white/[0.02] transition-colors">
        <td class="px-6 py-4 text-slate-200">Assembleia Geral</td>
      </tr>
    </tbody>
  </table>
</div>
```

#### Alertas e Notificações
```html
<!-- Sucesso -->
<div class="flex items-start gap-3 p-4 rounded-lg
            bg-teal-500/10 border border-teal-500/30 text-teal-300">
  <span class="text-teal-400 mt-0.5">✓</span>
  <p class="text-sm">Operação realizada com sucesso.</p>
</div>

<!-- Erro -->
<div class="flex items-start gap-3 p-4 rounded-lg
            bg-red-500/10 border border-red-500/30 text-red-300">
  <span class="text-red-400 mt-0.5">✕</span>
  <p class="text-sm">Ocorreu um erro. Tente novamente.</p>
</div>

<!-- Aviso -->
<div class="flex items-start gap-3 p-4 rounded-lg
            bg-amber-500/10 border border-amber-500/30 text-amber-300">
  <span class="text-amber-400 mt-0.5">⚠</span>
  <p class="text-sm">Atenção: quórum mínimo não atingido.</p>
</div>
```

### Página de Login (estrutura)

```html
<!-- Página de login: fundo com gradiente radial sutil -->
<div class="min-h-screen bg-[#0F0F1A] flex items-center justify-center
            relative overflow-hidden">

  <!-- Glow decorativo de fundo -->
  <div class="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2
              w-96 h-96 bg-violet-600/20 rounded-full blur-3xl pointer-events-none">
  </div>

  <!-- Card central -->
  <div class="relative z-10 w-full max-w-md bg-[#1A1A2E]
              border border-[#2A2A45] rounded-2xl p-8 shadow-2xl">

    <!-- Logo + título -->
    <div class="text-center mb-8">
      <h1 class="text-2xl font-bold bg-gradient-to-r from-violet-400
                 to-blue-400 bg-clip-text text-transparent">
        AssembleiaApp
      </h1>
      <p class="text-slate-400 text-sm mt-2">
        Acesse sua conta para continuar
      </p>
    </div>

    <!-- Formulário -->
    <form method="post" class="space-y-5">
      <!-- campos -->
      <button type="submit"
              class="w-full bg-gradient-to-r from-violet-600 to-blue-600
                     hover:from-violet-700 hover:to-blue-700 text-white
                     font-semibold py-2.5 rounded-lg transition-all
                     duration-200 shadow-lg shadow-violet-500/25">
        Entrar
      </button>
    </form>
  </div>
</div>
```

---

## 10. User Stories

### Épico 1 — Autenticação e Acesso

**US-01** — Como visitante, quero me cadastrar com e-mail e senha para acessar o sistema.
- **Critérios de aceite:**
  - [ ] Formulário solicita nome, e-mail e senha
  - [ ] E-mail deve ser único no sistema
  - [ ] Senha com no mínimo 8 caracteres
  - [ ] Após cadastro, usuário é redirecionado ao dashboard
  - [ ] Mensagens de erro em português

**US-02** — Como usuário, quero fazer login com meu e-mail para acessar minha conta.
- **Critérios de aceite:**
  - [ ] Campo de login aceita e-mail (não username)
  - [ ] Mensagem clara para credenciais inválidas
  - [ ] Redirecionamento ao dashboard após login bem-sucedido
  - [ ] Sessão mantida entre navegações

---

### Épico 2 — Organizações e Membros

**US-03** — Como administrador, quero cadastrar minha organização para centralizar a gestão.
- **Critérios de aceite:**
  - [ ] Formulário com nome, tipo (condomínio/sindicato/associação) e CNPJ
  - [ ] Organização aparece no dashboard após criação
  - [ ] Campos obrigatórios validados no backend

**US-04** — Como administrador, quero cadastrar membros da organização com seus papéis e status.
- **Critérios de aceite:**
  - [ ] Formulário com nome, e-mail, CPF, papel e status
  - [ ] Listagem de membros com filtro por status
  - [ ] Possibilidade de marcar membro como inadimplente
  - [ ] Edição e inativação de membro

---

### Épico 3 — Assembleias

**US-05** — Como síndico, quero criar uma assembleia com pauta definida para convocar os membros.
- **Critérios de aceite:**
  - [ ] Formulário com título, descrição, data, modo e quórum mínimo
  - [ ] Após criação, status inicia como "Rascunho"
  - [ ] Possibilidade de adicionar itens de pauta com ordem e tipo de votação
  - [ ] Registro de convocação com canal e data de envio

**US-06** — Como síndico, quero iniciar a assembleia e credenciar os membros presentes.
- **Critérios de aceite:**
  - [ ] Botão "Iniciar" disponível apenas para assembleias Convocadas
  - [ ] Check-in individual por membro com canal (presencial/online)
  - [ ] Contador de credenciados atualizado em tempo real
  - [ ] Indicador visual quando quórum mínimo é atingido
  - [ ] Inadimplentes bloqueados no check-in

**US-07** — Como síndico, quero conduzir as votações dos itens de pauta em ordem.
- **Critérios de aceite:**
  - [ ] Itens listados na ordem definida
  - [ ] Cada item abre e fecha individualmente
  - [ ] Resultado calculado automaticamente conforme tipo de quórum
  - [ ] Votação secreta não expõe membro ao voto
  - [ ] Impossibilidade de votar sem estar credenciado

---

### Épico 4 — Ata

**US-08** — Como síndico, quero gerar a ata automaticamente ao encerrar a assembleia.
- **Critérios de aceite:**
  - [ ] Ata gerada com todos os dados da assembleia
  - [ ] Inclui quórum, itens votados e resultados
  - [ ] Status inicial da ata: "Em revisão"
  - [ ] Possibilidade de aprovar a ata
  - [ ] Após aprovação, ata torna-se imutável

**US-09** — Como membro, quero assinar digitalmente a ata para validá-la.
- **Critérios de aceite:**
  - [ ] Registro de assinatura com token único e timestamp
  - [ ] Identificação do papel do assinante (síndico, secretário, membro)
  - [ ] Ata só é aprovada após assinaturas mínimas

---

### Épico 5 — Auditoria

**US-10** — Como administrador, quero visualizar o log de auditoria de uma assembleia.
- **Critérios de aceite:**
  - [ ] Lista cronológica de todas as ações
  - [ ] Exibe ator, ação, IP e timestamp
  - [ ] Filtro por tipo de ação
  - [ ] Logs não editáveis nem deletáveis

---

## 11. Métricas de Sucesso

### KPIs de Produto
| Métrica | Meta (3 meses) |
|---|---|
| Assembleias criadas por organização/mês | ≥ 2 |
| Taxa de conclusão de assembleia (até ata aprovada) | ≥ 70% |
| Tempo médio de preparação de assembleia | < 30 min |
| Taxa de erro em votações (duplo voto, etc.) | 0% |

### KPIs de Usuário
| Métrica | Meta |
|---|---|
| Tempo médio para aprender a criar uma assembleia | < 15 min |
| Satisfação do administrador (NPS implícito) | Positivo |
| Taxa de abandono no credenciamento | < 10% |

### KPIs Técnicos
| Métrica | Meta |
|---|---|
| Tempo de resposta das páginas | < 2s |
| Erros 500 em produção | 0 por semana |
| Integridade dos VoteRecords (hash válido) | 100% |

---

## 12. Riscos e Mitigações

| # | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| R01 | Duplo voto por race condition | Média | Alto | `F()` expressions + `UniqueConstraint` no banco |
| R02 | Dados de um tenant visíveis a outro | Baixa | Crítico | `TenantModel` com `org_id` obrigatório em todas as queries |
| R03 | Ata editada após aprovação | Baixa | Alto | `save()` bloqueado após status `approved` |
| R04 | Log de auditoria deletado | Muito baixa | Alto | `delete()` e `save()` bloqueados em `AuditLog` |
| R05 | Assembleia inválida por quórum não verificado | Média | Médio | Verificação de quórum antes de abrir votação |
| R06 | Votação secreta exposta por bug | Baixa | Alto | Hash SHA-256 do member_id, FK nula em VoteRecord secreto |
| R07 | Escopo crescente sem entregas | Alta | Médio | MVP bem definido, sprints com escopo fixo |

---

## 13. Lista de Tarefas por Sprint

---

### Sprint 0 — Fundação do Projeto
**Objetivo:** Ambiente configurado, estrutura de pastas criada e projeto Django rodando.

#### 1. Configuração do ambiente
- [x] 1.1 Criar pasta raiz do projeto
- [x] 1.2 Criar arquivo `.python-version` com `3.13`
- [x] 1.3 Inicializar projeto com `uv init`
- [x] 1.4 Instalar Django com `uv add django`
- [x] 1.5 Instalar ruff com `uv add --dev ruff`
- [ ] 1.6 Criar `pyproject.toml` com configurações de ruff (aspas simples, linha 100, PEP8)
- [ ] 1.7 Criar `.gitignore` com entradas para Python, Django, SQLite e uv

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
- [ ] 2.5 Configurar `BASE_DIR`, `TEMPLATES`, `STATICFILES_DIRS` no `settings.py`

#### 3. Configuração do TailwindCSS
- [ ] 3.1 Instalar Node.js localmente (apenas para build do Tailwind)
- [ ] 3.2 Instalar TailwindCSS via `npm install -D tailwindcss`
- [ ] 3.3 Criar `tailwind.config.js` apontando para templates Django
- [ ] 3.4 Criar arquivo `static/css/input.css` com diretivas Tailwind
- [ ] 3.5 Configurar script de build no `package.json`
- [ ] 3.6 Configurar `STATICFILES_DIRS` no Django para servir o CSS compilado
- [ ] 3.7 Testar build com `npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css`

#### 4. Configuração de logging
- [ ] 4.1 Adicionar configuração `LOGGING` no `settings.py`
- [ ] 4.2 Configurar handler de console com formatação: `[LEVEL] app.module: mensagem`
- [ ] 4.3 Definir level `DEBUG` para desenvolvimento e `INFO` para produção
- [ ] 4.4 Testar log simples em uma view temporária

#### 5. BaseModel e TenantModel
- [ ] 5.1 Criar arquivo `core/models.py`
- [ ] 5.2 Implementar `BaseModel` abstrato com `id` (UUID), `created_at`, `updated_at`
- [ ] 5.3 Implementar `TenantModel` abstrato herdando de `BaseModel` com FK para `Organization`
- [ ] 5.4 Adicionar docstrings explicativas em ambas as classes
- [ ] 5.5 Adicionar type hints em todos os campos e métodos

#### 6. Autenticação com e-mail
- [ ] 6.1 Criar arquivo `core/backends.py` com `EmailAuthBackend`
- [ ] 6.2 Implementar `authenticate()` usando e-mail ao invés de username
- [ ] 6.3 Adicionar `AUTHENTICATION_BACKENDS` no `settings.py` apontando para o backend
- [ ] 6.4 Adicionar docstring e type hints no backend

#### 7. Templates base
- [ ] 7.1 Criar pasta `core/templates/`
- [ ] 7.2 Criar `base.html` com estrutura HTML5, importação do CSS Tailwind e bloco `content`
- [ ] 7.3 Criar estrutura de sidebar e topbar no `base.html`
- [ ] 7.4 Aplicar paleta de cores definida no design system (fundo escuro, gradientes)
- [ ] 7.5 Criar `base_auth.html` para páginas de login/cadastro (layout centralizado)
- [ ] 7.6 Verificar responsividade do layout base em mobile e desktop

---

### Sprint 1 — Autenticação e Landing Page
**Objetivo:** Usuário consegue se cadastrar, fazer login, ver dashboard básico e a landing page pública.

#### 8. Landing page pública
- [ ] 8.1 Criar view `LandingView` em `core/views.py` como `TemplateView`
- [ ] 8.2 Criar template `core/templates/landing.html` estendendo `base_auth.html`
- [ ] 8.3 Implementar seção hero com título, subtítulo e botões "Cadastre-se" e "Login"
- [ ] 8.4 Aplicar gradiente de fundo e glow decorativo no hero
- [ ] 8.5 Implementar seção de features (3 cards com ícones SVG e textos)
- [ ] 8.6 Adicionar rodapé com nome do produto e ano
- [ ] 8.7 Configurar rota `/` apontando para `LandingView` em `config/urls.py`
- [ ] 8.8 Verificar responsividade da landing em mobile

#### 9. Cadastro de usuário
- [ ] 9.1 Criar `core/forms.py` com `UserRegistrationForm` herdando de `UserCreationForm`
- [ ] 9.2 Substituir campo `username` por `email` no formulário
- [ ] 9.3 Adicionar campo `name` (nome completo) ao formulário
- [ ] 9.4 Criar view `RegisterView` em `core/views.py` como `CreateView`
- [ ] 9.5 Criar template `core/templates/register.html` com layout de card centralizado
- [ ] 9.6 Aplicar classes do design system nos inputs e botão
- [ ] 9.7 Implementar redirecionamento para dashboard após cadastro bem-sucedido
- [ ] 9.8 Exibir mensagens de validação em português
- [ ] 9.9 Configurar rota `/cadastro/` em `config/urls.py`

#### 10. Login de usuário
- [ ] 10.1 Criar view `LoginView` customizada em `core/views.py` herdando de `auth.LoginView`
- [ ] 10.2 Sobrescrever formulário para usar campo e-mail
- [ ] 10.3 Criar template `core/templates/login.html` com card centralizado e glow
- [ ] 10.4 Aplicar classes do design system no formulário
- [ ] 10.5 Configurar `LOGIN_REDIRECT_URL = '/dashboard/'` no `settings.py`
- [ ] 10.6 Configurar rota `/login/` em `config/urls.py`
- [ ] 10.7 Exibir mensagem de erro clara para credenciais inválidas

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