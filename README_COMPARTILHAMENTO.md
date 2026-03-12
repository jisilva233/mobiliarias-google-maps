# 🏠 Mapa de Imobiliárias - Guia de Compartilhamento

## 🚀 Deploy em 5 Minutos

### **Opção A: Streamlit Cloud (RECOMENDADO)**

Mais fácil para Streamlit. Deploy automático.

```bash
# 1. Push para GitHub
git add .
git commit -m "Pronto para deploy"
git push origin main

# 2. Acesse https://streamlit.io/cloud
# 3. "New app" → Selecione repositório e dashboard.py
# 4. Clique "Deploy"
# 5. Configure Secrets em Settings:
#    SUPABASE_URL = sua_url
#    SUPABASE_KEY = sua_chave
```

**URL Final:** `https://seu-username-seu-app.streamlit.app`

---

### **Opção B: Vercel (Se preferir)**

Mais controle, interface familiar.

```bash
# 1. Push para GitHub
git add .
git commit -m "Deploy Vercel"
git push origin main

# 2. Acesse https://vercel.com
# 3. Import Project → GitHub
# 4. Configure Environment Variables:
#    SUPABASE_URL = sua_url
#    SUPABASE_KEY = sua_chave
# 5. Deploy
```

**URL Final:** `https://seu-app.vercel.app`

---

## 📋 Checklist Pré-Deploy

- [ ] Código atualizado: `git push`
- [ ] `.env` NÃO foi commitado (verificar `.gitignore`)
- [ ] `requirements.txt` criado ✅
- [ ] `dashboard.py` funciona localmente
- [ ] Credenciais Supabase confirmadas

---

## 🔑 Credenciais Supabase

### Onde Encontrar:

1. Dashboard Supabase → Seu Projeto
2. Settings → API
3. Copie:
   - **Project URL** → SUPABASE_URL
   - **anon public key** → SUPABASE_KEY

### Exemplo:
```
SUPABASE_URL=https://seu-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🧪 Testar Antes de Deploy

```bash
# Instalar dependências
pip install -r requirements.txt
playwright install

# Rodar localmente
streamlit run dashboard.py

# Acesso
# http://localhost:8501
```

---

## 📊 Funcionalidades Disponíveis

- ✅ **Escanear Cidades** - Campo de input novo para adicionar cidades
- ✅ **Geocoding** - Busca automática de coordenadas (mapa)
- ✅ **Filtros** - Por cidade, rating mínimo
- ✅ **Abas:**
  - 📋 Lista - Todas as imobiliárias
  - 🗺️ Mapa - Visualização geográfica
  - 🏆 Ranking - Top 20 melhor avaliadas

---

## 🔄 Workflow Após Deploy

1. App rodando públicamente
2. Qualquer pessoa acessa via URL
3. Digita nova cidade e clica "Escanear"
4. Sistema coleta dados automaticamente
5. Dashboard atualiza em tempo real

---

## ⚙️ Configuração Vercel (Detalhada)

Se for usar Vercel, o arquivo `vercel.json` já está configurado:

```json
{
  "buildCommand": "pip install -r requirements.txt && playwright install",
  "devCommand": "streamlit run dashboard.py",
  "functions": {
    "dashboard.py": {
      "memory": 1024,
      "maxDuration": 300
    }
  }
}
```

---

## 🛠️ Troubleshooting

| Erro | Solução |
|------|---------|
| "Module not found" | Verifique `requirements.txt` |
| "SUPABASE_KEY not found" | Configure em Secrets/Env Vars |
| "Timeout ao escanear" | Aumentar timeout ou reduzir max-results |
| Mapa vazio | Executar `--geocode` na CLI antes |

---

## 📱 Compartilhar com Amigos

Após deploy, compartilhe a URL:
- Copie URL do Streamlit Cloud/Vercel
- Envie por WhatsApp, email, Slack, etc.
- Ninguém precisa instalar nada!

**Exemplo:**
```
Veja as imobiliárias da sua cidade!
https://seu-app.streamlit.app
```

---

## 🎯 Próximos Passos

1. Escolha Streamlit Cloud (mais simples) ou Vercel
2. Siga os passos de deploy acima
3. Configure credenciais Supabase
4. Teste escanear uma cidade
5. Compartilhe URL com o time!

**Tempo total:** ~10 minutos

