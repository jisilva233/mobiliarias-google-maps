# Squad Creator - Installed Commands

**Version**: 3.0.0
**Installed**: 2026-03-12

## Available Agents

- `@squadCreator:squad-chief` - 🎨 Squad Architect (entry point, triage & routing)
- `@squadCreator:oalanicolas` - 🧠 Alan Nicolas — Knowledge Architect & DNA Extraction
- `@squadCreator:pedro-valerio` - ⚙️ Pedro Valério — Process Design & Workflow Validation

## Usage

### Ativar um agente:
```
@squadCreator:squad-chief
```

### Fluxo recomendado:
1. `@squadCreator:squad-chief` — triage e routing para criar squads
2. `@squadCreator:oalanicolas` — pesquisa e extração de DNA de experts
3. `@squadCreator:pedro-valerio` — design de processos e validação

### Comandos principais:
- `*create-squad` — Criar um novo squad de agentes
- `*create-agent` — Criar agente individual
- `*clone-mind` — Clonar mente de um expert
- `*help` — Ver todos os comandos disponíveis

## Estrutura

- **agents/**: Definições dos agentes (3 agentes)
- **tasks/**: Workflows executáveis (42 tasks)
- **workflows/**: Pipelines YAML (9 workflows)

## Squad Source

Arquivos fonte em: `squads/squad-creator/`

## Desinstalar

```bash
rm -rf .claude/commands/squadCreator
```
