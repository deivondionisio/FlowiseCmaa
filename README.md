# Langflow CMAA

Langflow com componentes da CMAA, pronto para o Coolify:

- **Maria (Copilot CMAA)**: usa a API do Copilot como modelo de linguagem
  (envia `instruction`, `message`, `context` e `modelo`; autenticação Bearer).
- **SAP Datasphere SQL**: executa `SELECT`/`WITH` no Datasphere e devolve tabela ou texto.

## Deploy no Coolify
1. *New Resource* → este repositório → **Build Pack: Docker Compose**.
2. No serviço `langflow`, defina o domínio (ex.: `https://langflow.seudominio.com`). Não publique portas.
3. Em *Environment Variables*, preencha `MARIA_API_URL`, `MARIA_API_KEY` e, quando for usar, `DS_*`.
   As senhas `SERVICE_PASSWORD_*` e a chave `SERVICE_BASE64_64_LANGFLOWSECRET` são geradas pelo Coolify.
4. **Deploy**. Login: usuário `admin` e a senha em `SERVICE_PASSWORD_LANGFLOW`.

Os componentes aparecem na barra lateral do Langflow, na categoria **cmaa**.

## Rodar localmente
Crie um arquivo `.env` na raiz (ele é ignorado pelo Git e nunca vai para o GitHub):
```
SERVICE_PASSWORD_POSTGRES=uma-senha
SERVICE_PASSWORD_LANGFLOW=uma-senha
SERVICE_BASE64_64_LANGFLOWSECRET=uma-chave-aleatoria-longa
LANGFLOW_SUPERUSER=admin
MARIA_API_URL=https://url-da-api-do-copilot
MARIA_API_KEY=
DS_HOST=
DS_PORT=443
DS_USER=
DS_PASSWORD=
```
Depois rode `docker compose up --build`.
Acesse http://localhost:7860 (adicione `ports: ["7860:7860"]` ao serviço `langflow` para uso local).

## Datasphere
- Crie um usuário de banco no Space (*Space Management → Database Access*), com leitura SQL.
- Libere o IP público do servidor em *System → Configuration → IP Allowlist*.
- Use aspas duplas em schema/view: `SELECT TOP 10 * FROM "ESPACO"."VIEW"`.
