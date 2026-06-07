"""
Utility functions for the ``minutes`` application.

This module provides helpers for automatically generating the official minutes
(ata) of a general assembly, including quorum data, agenda items, voting results,
and deliberations.
"""

from __future__ import annotations

from django.utils import timezone

from assemblies.models import Assembly


def generate_minutes_content(assembly: Assembly) -> str:
    """
    Build and return the full text content of the minutes for a closed assembly.

    The generated document is structured as follows:

    1. **Cabeçalho (Header)** — Assembly title, organisation name, date/time,
       location or meeting URL, and mode.
    2. **Quórum** — Number of credentialed members, total active members in the
       organisation, and whether the required quorum percentage was reached.
    3. **Itens de Pauta (Agenda Items)** — For each item: its order, title,
       description (if any), vote mode (open/secret), quorum check result,
       voting results (label + count + percentage), and deliberation outcome
       (approved / rejected / abstained).
    4. **Encerramento (Closing)** — Timestamp when the assembly ended.

    Args:
        assembly: The :class:`assemblies.models.Assembly` instance whose minutes
            are being generated.  The assembly should already be in ``closed``
            status and have its ``ended_at`` field populated, but this function
            does not enforce that constraint — callers are responsible for
            ensuring the assembly is in the correct state before invoking this
            helper.

    Returns:
        str: Fully formatted plain-text content suitable for storage in
            :attr:`minutes.models.Minutes.content`.

    Example::

        from assemblies.models import Assembly
        from minutes.utils import generate_minutes_content

        assembly = Assembly.objects.get(pk=some_pk)
        content = generate_minutes_content(assembly)
        # persist to Minutes.content
    """
    from organizations.models import MemberStatus  # avoid circular imports

    lines: list[str] = []

    # ── 1. Cabeçalho ──────────────────────────────────────────────────────────
    lines.append('=' * 70)
    lines.append('ATA DE ASSEMBLEIA')
    lines.append('=' * 70)
    lines.append('')
    lines.append(f'Título: {assembly.title}')
    lines.append(f'Organização: {assembly.organization.name}')

    scheduled_str: str = (
        assembly.scheduled_at.strftime('%d/%m/%Y às %H:%M')
        if assembly.scheduled_at
        else 'Não informado'
    )
    lines.append(f'Data/Hora agendada: {scheduled_str}')

    if assembly.started_at:
        lines.append(f'Início: {assembly.started_at.strftime("%d/%m/%Y às %H:%M")}')

    if assembly.ended_at:
        lines.append(f'Encerramento: {assembly.ended_at.strftime("%d/%m/%Y às %H:%M")}')

    lines.append(f'Modalidade: {assembly.get_mode_display()}')

    if assembly.location:
        lines.append(f'Local: {assembly.location}')

    if assembly.meeting_url:
        lines.append(f'URL da reunião: {assembly.meeting_url}')

    if assembly.description:
        lines.append('')
        lines.append(f'Descrição: {assembly.description}')

    lines.append('')

    # ── 2. Quórum ─────────────────────────────────────────────────────────────
    lines.append('-' * 70)
    lines.append('QUÓRUM')
    lines.append('-' * 70)

    total_credentials: int = assembly.total_credentials
    total_active_members: int = (
        assembly.organization.organizations_member_set  # type: ignore[attr-defined]
        .filter(status=MemberStatus.ATIVO)
        .count()
    )
    quorum_reached: bool = assembly.quorum_reached
    quorum_pct: float = (
        round(total_credentials / total_active_members * 100, 2)
        if total_active_members
        else 0.0
    )

    lines.append(f'Membros credenciados: {total_credentials}')
    lines.append(f'Total de membros ativos: {total_active_members}')
    lines.append(f'Quórum exigido: {assembly.quorum_required}%')
    lines.append(f'Quórum atingido: {quorum_pct}%')
    lines.append(f'Status do quórum: {"✔ Atingido" if quorum_reached else "✘ Não atingido"}')
    lines.append('')

    # ── 3. Itens de Pauta ─────────────────────────────────────────────────────
    lines.append('-' * 70)
    lines.append('ITENS DE PAUTA E RESULTADOS DE VOTAÇÃO')
    lines.append('-' * 70)
    lines.append('')

    agenda_items = (
        assembly.agenda_items  # type: ignore[attr-defined]
        .prefetch_related('vote_options')
        .order_by('order_index')
    )

    if not agenda_items.exists():
        lines.append('Nenhum item de pauta registrado.')
        lines.append('')
    else:
        for item in agenda_items:
            lines.append(f'  {item.order_index}. {item.title}')
            lines.append(f'     Status: {item.get_status_display()}')
            lines.append(f'     Modo de votação: {item.get_vote_mode_display()}')

            if item.description:
                lines.append(f'     Descrição: {item.description}')

            # Voting results
            results: list[dict] = item.get_result()
            total_votes: int = item.total_votes

            if results:
                item_quorum_ok: bool = item.check_quorum_reached()
                lines.append(f'     Total de votos: {total_votes}')
                lines.append(
                    f'     Quórum do item ({item.quorum_required}% — '
                    f'{item.get_quorum_type_display()}): '
                    f'{"✔ Atingido" if item_quorum_ok else "✘ Não atingido"}'
                )
                lines.append('     Resultado:')
                for option in results:
                    lines.append(
                        f'       - {option["label"]}: '
                        f'{option["count"]} voto{"s" if option["count"] != 1 else ""} '
                        f'({option["percentage"]}%)'
                    )

                # Deliberation: winner is the option with the highest count
                winner: dict = results[0]
                lines.append(f'     Deliberação: {winner["label"]} ({winner["percentage"]}%)')
            else:
                lines.append('     Sem votos registrados.')

            lines.append('')

    # ── 4. Encerramento ───────────────────────────────────────────────────────
    lines.append('-' * 70)
    lines.append('ENCERRAMENTO')
    lines.append('-' * 70)

    ended_str: str = (
        assembly.ended_at.strftime('%d/%m/%Y às %H:%M')
        if assembly.ended_at
        else timezone.now().strftime('%d/%m/%Y às %H:%M')
    )
    lines.append(
        f'Nada mais havendo a tratar, a assembleia foi encerrada em {ended_str}.'
    )
    lines.append('')
    lines.append(
        'Esta ata foi gerada automaticamente pelo sistema MaticVotes e '
        'está sujeita à revisão e aprovação pelos responsáveis da organização.'
    )
    lines.append('=' * 70)

    return '\n'.join(lines)
