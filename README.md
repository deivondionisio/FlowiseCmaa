# Langflow CMAA

Langflow 1.13.4 com componentes da CMAA:

- **Maria (Copilot CMAA)**: conversa com o agente Maria do Copilot Studio pelo Direct Line
  e funciona como modelo de linguagem dentro dos fluxos.
- **SAP Datasphere SQL**: executa `SELECT`/`WITH` no Datasphere e devolve tabela ou texto.

Os componentes aparecem na barra lateral do Langflow, na categoria **cmaa**.

## 1. Rodar localmente (Windows)

Pré-requisito: Python 3.13 (`py -3.13 --version`).

1. Crie um arquivo `.env` na raiz do projeto (ele é ignorado pelo Git e nunca vai para o GitHub):
   ```
   MARIA_DIRECTLINE_SECRET='cole-aqui-o-segredo-1'
   DS_HOST=
   DS_PORT=443
   DS_USER=
   DS_PASSWORD=
   ```
   O segredo fica no Copilot Studio: agente Maria > Configurações > Segurança > Segurança de canal Web > Segredo 1 > Copiar.
2. Rode `.\run.bat` (a primeira vez instala o Langflow e demora alguns minutos).
3. Abra http://127.0.0.1:7860

### Testar a Maria
1. Crie um fluxo em branco (*New Flow > Blank Flow*).
2. Adicione **Chat Input**, **Maria (Copilot CMAA)** (categoria *cmaa*) e **Chat Output**.
3. Ligue *Chat Input → Input* da Maria e *Model Response* da Maria → *Chat Output*.
4. Abra o **Playground** e pergunte algo.

## 2. Deploy no Coolify (depois de testar localmente)
1. *New Resource* → este repositório → **Build Pack: Docker Compose**.
2. No serviço `langflow`, defina o domínio. Não publique portas.
3. Em *Environment Variables*, preencha `MARIA_DIRECTLINE_SECRET` (sem aspas) e, quando for usar, `DS_*`.
   As senhas `SERVICE_PASSWORD_*` e `SERVICE_BASE64_64_LANGFLOWSECRET` são geradas pelo Coolify.
4. **Deploy**. Login: usuário `admin` e a senha em `SERVICE_PASSWORD_LANGFLOW`.

## Datasphere
- Crie um usuário de banco no Space (*Space Management → Database Access*), com leitura SQL.
- Libere o IP público (da sua rede ou do servidor) em *System → Configuration → IP Allowlist*.
- Use aspas duplas em schema/view: `SELECT TOP 10 * FROM "ESPACO"."VIEW"`.
