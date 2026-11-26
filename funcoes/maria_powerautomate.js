/*
 * Maria (Copilot Studio - CMAA) via fluxo do Power Automate
 * (o mesmo endpoint usado pelo app Mendix)
 * Nó: Agentflow > Custom Function
 *
 * Input Variables do nó:
 *   pergunta  = {{ question }}
 *   historico = {{ chat_history }}
 * Variáveis do Flowise (Variables, tipo Runtime):
 *   MARIA_FLOW_URL    -> URL completa do gatilho HTTP do fluxo (inclui a assinatura sig=...)
 *   MARIA_FLOW_TOKEN  -> opcional: só se o fluxo exigir header Authorization
 */
const fetch = require('node-fetch');

const URL_FLUXO = $vars.MARIA_FLOW_URL;
const TOKEN = $vars.MARIA_FLOW_TOKEN;
const MODELO = 'Opus';
const INSTRUCAO = 'Não use Markdown nem Tabelas!';

if (!URL_FLUXO) {
  return 'Erro: variável MARIA_FLOW_URL não configurada no Flowise.';
}

const headers = { 'Content-Type': 'application/json' };
if (TOKEN) headers.Authorization = `Bearer ${TOKEN}`;

const corpo = {
  message: String($pergunta || '').trim(),
  modelo: MODELO,
  instruction: INSTRUCAO,
  contexto: String($historico || '').trim()
};

try {
  const r = await fetch(URL_FLUXO, { method: 'POST', headers, body: JSON.stringify(corpo), timeout: 300000 });
  const texto = await r.text();
  if (!r.ok) return `Erro ao chamar a Maria: HTTP ${r.status} - ${texto.slice(0, 300)}`;
  let dados;
  try { dados = JSON.parse(texto); } catch { return texto; }
  return dados.resposta || dados.response || dados.answer || dados.message || JSON.stringify(dados);
} catch (e) {
  return `Erro ao falar com a Maria: ${e.message}`;
}
