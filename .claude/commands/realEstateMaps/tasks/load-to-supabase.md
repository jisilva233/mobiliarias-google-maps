---
task: Load Agencies to Supabase
responsavel: "@pipeline-agent"
atomic_layer: task
elicit: false
---

# load-to-supabase

Persiste os dados de imobiliárias no Supabase com upsert idempotente.

## Inputs
- Lista de objetos `Agency` validados
- `city`: nome da cidade (para filtro e atualização)

## Outputs
- Relatório: inseridos / atualizados / erros

## Schema da Tabela

```sql
CREATE TABLE IF NOT EXISTS real_estate_agencies (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome        TEXT NOT NULL,
  endereco    TEXT,
  telefone    TEXT,
  website     TEXT,
  rating      FLOAT,
  reviews     INTEGER,
  cidade      TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(nome, cidade)
);
```

## Upsert Strategy
- Chave de conflito: `(nome, cidade)`
- Em conflito: atualizar todos os campos exceto `id` e `created_at`

```python
supabase.table("real_estate_agencies").upsert(
    data,
    on_conflict="nome,cidade"
).execute()
```

## Batch Processing
- Inserir em lotes de 50 para evitar timeout
- Log de progresso: `Inserindo lote 1/3...`

## Tratamento de Erros
- Erro de conexão → retry 3x com backoff exponencial
- Erro de validação → log e continuar
- Erro crítico → raise exception com contexto
