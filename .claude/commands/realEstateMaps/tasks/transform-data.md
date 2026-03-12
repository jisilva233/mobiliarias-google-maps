---
task: Transform & Validate Agency Data
responsavel: "@pipeline-agent"
atomic_layer: task
elicit: false
---

# transform-data

Limpa, normaliza e valida os dados brutos extraídos pelo scraper.

## Inputs
- Lista bruta de dicts com dados do Google Maps

## Outputs
- Lista de objetos `Agency` válidos e normalizados

## Transformações

### Nome
- Strip whitespace
- Title case: `"IMOBILIÁRIA ALFA"` → `"Imobiliária Alfa"`
- Obrigatório — descartar registro se None/vazio

### Endereço
- Strip whitespace
- Manter formato original do Google Maps
- Opcional (None se não disponível)

### Telefone
- Remover caracteres não numéricos
- Normalizar: `"41999990000"` → `"(41) 99999-0000"`
- Opcional (None se não disponível)

### Website
- Validar formato URL (deve começar com http/https)
- Opcional (None se inválido)

### Rating
- Converter para float: `"4,5"` → `4.5`
- Intervalo válido: 0.0 a 5.0
- None se não disponível

### Reviews
- Converter para int: `"(123)"` → `123`
- None se não disponível

## Validação Final
- Descartar registros sem `nome`
- Log de registros descartados com motivo
- Retornar apenas registros válidos
