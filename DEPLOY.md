# Guia de Deployment - Mapa de Imobiliárias

## Opção 1: Streamlit Cloud (RECOMENDADO - Mais fácil)

### Passo 1: Preparar Repositório GitHub
```bash
# 1. Criar repositório no GitHub (se não tiver)
# 2. Fazer push do projeto
git add .
git commit -m "Pronto para deploy"
git push origin main
```

### Passo 2: Deploy no Streamlit Cloud
1. Acesse https://streamlit.io/cloud
2. Clique em "New app"
3. Selecione seu repositório e branch (`main`)
4. Defina caminho do arquivo: `dashboard.py`
5. Clique "Deploy"

### Passo 3: Configurar Variáveis de Ambiente
1. No painel do Streamlit Cloud, vá para "Settings" → "Secrets"
2. Adicione:
```
SUPABASE_URL = "sua_url_aqui"
SUPABASE_KEY = "sua_chave_aqui"
```

### ✅ Pronto!
- URL pública gerada automaticamente
- Deploy automático a cada push
- Sem custo (plano free)

**Tempo de setup:** 5 minutos

---

## Opção 2: Vercel (Mais robusto)

### Passo 1: Preparar Repositório
```bash
git add .
git commit -m "Pronto para Vercel"
git push origin main
```

### Passo 2: Deploy no Vercel
1. Acesse https://vercel.com
2. Clique "New Project"
3. Importe seu repositório GitHub
4. Deixe padrões e clique "Deploy"

### Passo 3: Variáveis de Ambiente
1. No dashboard Vercel, vá para "Settings" → "Environment Variables"
2. Adicione:
   - `SUPABASE_URL` = sua URL
   - `SUPABASE_KEY` = sua chave

### ✅ Deploy Ativo!
- Acesse a URL fornecida pelo Vercel
- Atualizações automáticas a cada push

---

## Obter Credenciais Supabase

### No Dashboard Supabase:
1. Projeto → Settings → API
2. Copie:
   - `Project URL` → SUPABASE_URL
   - `anon public` → SUPABASE_KEY

### Exemplo:
```
SUPABASE_URL=https://mtigxpjsuawtxmdcqamj.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Testar Localmente Antes de Deploy

```bash
# Instalar dependências
pip install -r requirements.txt
playwright install

# Rodar dashboard
streamlit run dashboard.py

# Acesso local
# http://localhost:8501
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "SUPABASE_URL not found"
- Verifique se variáveis de ambiente estão definidas
- Streamlit Cloud: Settings → Secrets
- Vercel: Settings → Environment Variables

### Playwright não funciona no deploy
- Streamlit Cloud: suporta nativamente
- Vercel: pode precisar de configuração extra

---

## Compartilhar o App

Após deploy, você terá uma URL pública como:
- **Streamlit Cloud:** `https://seu-app.streamlit.app`
- **Vercel:** `https://seu-app.vercel.app`

Compartilhe esta URL com qualquer pessoa!

---

## Próximos Passos

1. Deploy no Streamlit Cloud (mais simples)
2. Testar escanear cidades adicionais pelo dashboard
3. Compartilhar URL com o time
