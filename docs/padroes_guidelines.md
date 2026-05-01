# Padrões e Guidelines

- **Autenticação:** Email e senha (Django padrão).
- **Multi-tenant:** Todas as entidades possuem `org_id`.
- **Papéis:** síndico/presidente, secretário, conselheiro, membro.
- **Status de membros:** ativo, inativo, inadimplente.
- **Fluxo de assembleia:** Rascunho → Convocada → Em andamento → Encerrada → Arquivada.
- **Votações:** abertas ou secretas, com integridade auditável.
- **Atas:** geradas automaticamente, com assinaturas digitais.
- **Logs:** auditoria imutável de todas as ações.
