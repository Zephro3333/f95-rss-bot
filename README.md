# 🚀 F95 Discord Bot (Auto RSS Monitor)

Este projeto é um bot automatizado que monitoriza atualizações no F95Zone e envia notificações em tempo real para um canal do Discord via Webhook.

O sistema corre automaticamente através do GitHub Actions, sem necessidade de servidor dedicado.

---

# ⚙️ Como funciona

O bot executa a cada 5 minutos via GitHub Actions:

1. Consulta a API do F95Zone
2. Compara os posts com o estado guardado (`state/last_seen.json`)
3. Detecta novos conteúdos
4. Envia automaticamente para o Discord
5. Atualiza o estado local no repositório

---

# 🧠 Arquitetura

- **GitHub Actions** → scheduler (execução automática)
- **Python bot** → lógica principal
- **JSON state file** → memória persistente
- **Discord Webhook** → envio de notificações

---

# 📁 Estrutura do projeto

f95-bot
├── .github/workflows/rss.yml # Automação GitHub Actions
├── f95_bot/
│ ├── main.py # Entry point
│ ├── client.py # API + Discord sender
│ ├── state.py # Persistência de estado
│ ├── monitor.py # Spike + failure detection
│ └── config.py # Config futura (opcional)
├── state/
│ └── last_seen.json # Estado dos posts já enviados
├── requirements.txt
└── README.md


---

# 🔑 Configuração

## 1. Criar Discord Webhook

No Discord:
- Canal → Settings → Integrations → Webhooks
- Criar webhook
- Copiar URL

---

## 2. Adicionar no GitHub Secrets

No repositório:
Settings → Secrets and variables → Actions → New secret

Adicionar:
DISCORD_WEBHOOK = https://discord.com/api/webhooks/XXXX

---

## 3. Ativar GitHub Actions

O bot já funciona automaticamente após push para `main`.

Também pode ser executado manualmente via:
Actions → Run workflow


---

# ⏱️ Frequência

- Executa a cada **5 minutos**
- Sem necessidade de servidor
- Totalmente serverless

---

# 🧠 Sistema de proteção

O bot inclui:

### ✔ Anti-duplicação
Evita enviar posts repetidos usando `state/last_seen.json`

### ✔ Auto-recovery
Se houver falhas temporárias, o próximo ciclo recupera automaticamente

### ✔ Spike handling
Detecta aumentos anormais de posts e ajusta comportamento

### ✔ Silent failure detection
Detecta se o bot ficou demasiado tempo sem atividade

---

# 📊 Estado do sistema

O ficheiro:
state/last_seen.json

guarda:

- posts já enviados
- timestamp do último run
- heartbeat interno
- histórico de atividade

---

# ⚠️ Limitações

- Depende de GitHub Actions (limite de execução)
- Delay mínimo: ~1–2 minutos
- Webhook do Discord pode ser rate-limited em spam extremo

---

# 🚀 Possíveis upgrades

- Dashboard web (monitorização real-time)
- Multi-feed support
- Redis database (substituir JSON state)
- Alertas de falha no Discord
- Sistema de prioridade de posts

---

# 📌 Autor

Bot desenvolvido como sistema automatizado de monitorização e notificação em tempo real para comunidades Discord.

---

# 🧩 Nota final

Este projeto foi desenhado para ser:

✔ leve  
✔ resiliente  
✔ auto-recuperável  
✔ 100% automatizado via GitHub Actions
