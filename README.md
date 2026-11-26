# Flowise CMAA

Flowise 3.1.4 com a Maria (agente do Copilot Studio da CMAA) conectada via Direct Line.

## 1. Rodar localmente (Windows)

Pré-requisito: **Node.js 24** (https://nodejs.org). Confira com `node -v`.

1. Crie um arquivo `.env` na raiz do projeto (ele é ignorado pelo Git e nunca vai para o GitHub):
   ```
   MARIA_DIRECTLINE_SECRET='cole-aqui-o-segredo-1'
   PORT=3000
   ```
   O segredo fica no Copilot Studio: agente Maria > Configurações > Segurança > Segurança de canal Web > Segredo 1 > Copiar.
2. Rode `.\run.bat` (a primeira vez instala o Flowise e demora alguns minutos).
3. Abra http://localhost:3000 e crie a conta de administrador.

## 2. Configurar a Maria no Flowise

### 2.1 Variável com o segredo
*Variables* (menu lateral) > **Add Variable**:
- Name: `MARIA_DIRECTLINE_SECRET`
- Type: **Runtime** (o Flowise lê o valor do `.env`, o segredo não fica salvo no banco)

### 2.2 Agentflow
1. *Agentflows* > **Add New**.
2. Ligue: **Start** → **Custom Function** → **Direct Reply**.
3. No **Custom Function**:
   - *Input Variables* > Add Item:
     - `pergunta` = `{{ question }}`
     - `historico` = `{{ chat_history }}`
   - *Javascript Function*: cole o conteúdo de `funcoes/maria_directline.js`.
4. No **Direct Reply**, em *Message*, selecione a saída do Custom Function (`{{ customFunctionAgentflow_0 }}`).
5. Salve e teste no chat (ícone de balão no canto superior direito).

## 3. Deploy no Coolify
Depois de testar localmente.
