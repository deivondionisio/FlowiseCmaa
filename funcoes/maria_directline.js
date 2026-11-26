/*
 * Maria (Copilot Studio - CMAA) via Direct Line
 * Nó: Agentflow > Custom Function
 *
 * Input Variables do nó:
 *   pergunta  = {{ question }}
 *   historico = {{ chat_history }}
 * Variável do Flowise (Variables, tipo Runtime):
 *   MARIA_DIRECTLINE_SECRET  -> lida do .env / ambiente
 */
const fetch = require('node-fetch');

const BASE = ($vars.MARIA_DIRECTLINE_URL || 'https://directline.botframework.com/v3/directline').replace(/\/$/, '');
const SECRET = $vars.MARIA_DIRECTLINE_SECRET;
const USER_ID = 'flowise';
const TIMEOUT_MS = 120000;  // tempo máximo esperando a Maria
const POLL_MS = 1000;       // intervalo entre consultas
const QUIET_MS = 2000;      // espera por mensagens extras após a primeira resposta

if (!SECRET) {
  return 'Erro: variável MARIA_DIRECTLINE_SECRET não configurada no Flowise.';
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const headers = (token) => ({ Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' });

// Monta o texto: com histórico, se houver
const pergunta = String($pergunta || '').trim();
const historico = String($historico || '').trim();
const texto = historico
  ? `Histórico da conversa:\n${historico}\n\nPergunta atual: ${pergunta}`
  : pergunta;

try {
  // 1. Inicia a conversa
  let r = await fetch(`${BASE}/conversations`, { method: 'POST', headers: headers(SECRET) });
  if (!r.ok) return `Erro ao iniciar conversa com a Maria: HTTP ${r.status}`;
  const conv = await r.json();
  const convId = conv.conversationId;
  const token = conv.token || SECRET;

  // 2. Envia a pergunta
  r = await fetch(`${BASE}/conversations/${convId}/activities`, {
    method: 'POST',
    headers: headers(token),
    body: JSON.stringify({ type: 'message', from: { id: USER_ID }, text: texto, locale: 'pt-BR' })
  });
  if (!r.ok) return `Erro ao enviar pergunta para a Maria: HTTP ${r.status}`;
  const msgId = (await r.json()).id;

  // 3. Aguarda as respostas a essa pergunta (ignora saudação inicial e "digitando...")
  let watermark = null;
  const respostas = [];
  let ultima = null;
  const limite = Date.now() + TIMEOUT_MS;
  while (Date.now() < limite) {
    const url = `${BASE}/conversations/${convId}/activities` + (watermark ? `?watermark=${watermark}` : '');
    r = await fetch(url, { headers: headers(token) });
    if (!r.ok) return `Erro ao ler resposta da Maria: HTTP ${r.status}`;
    const dados = await r.json();
    watermark = dados.watermark || watermark;
    for (const act of dados.activities || []) {
      if (act.type !== 'message' || (act.from && act.from.id === USER_ID)) continue;
      if (msgId && act.replyToId && act.replyToId !== msgId) continue;
      if (msgId && !act.replyToId && respostas.length === 0) continue;
      if (act.text) {
        respostas.push(act.text);
        ultima = Date.now();
      }
    }
    if (respostas.length && Date.now() - ultima >= QUIET_MS) break;
    await sleep(POLL_MS);
  }

  return respostas.length ? respostas.join('\n\n') : `A Maria não respondeu em ${TIMEOUT_MS / 1000}s.`;
} catch (e) {
  return `Erro ao falar com a Maria: ${e.message}`;
}
