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
