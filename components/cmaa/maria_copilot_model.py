"""Componente Langflow: Maria (agente do Copilot Studio - CMAA) via Direct Line."""
import os
import time
from typing import Any, List, Optional

import requests
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.io import FloatInput, SecretStrInput, StrInput

DIRECTLINE_URL = "https://directline.botframework.com/v3/directline"


class MariaCMAAChatModel(BaseChatModel):
    """Chat model LangChain que conversa com o agente Maria do Copilot Studio pelo Direct Line.

    As instruções da Maria ficam no próprio Copilot Studio. Aqui enviamos apenas a pergunta
    (e, se houver, o histórico da conversa e instruções extras do Langflow).
    """

    secret: str
    base_url: str = DIRECTLINE_URL
    user_id: str = "langflow"
    timeout: float = 120
    poll_interval: float = 1.0
    quiet_period: float = 2.0  # espera por mensagens extras depois da primeira resposta

    # ---------------------------------------------------------------- helpers
    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _montar_texto(self, messages: List[BaseMessage]) -> str:
        instrucoes, historico, pergunta = [], [], ""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                if str(msg.content).strip():
                    instrucoes.append(str(msg.content))
            elif isinstance(msg, HumanMessage):
                if pergunta:
                    historico.append(f"Usuário: {pergunta}")
                pergunta = str(msg.content)
            elif isinstance(msg, AIMessage):
                if pergunta:  # mantém a ordem pergunta -> resposta
                    historico.append(f"Usuário: {pergunta}")
                    pergunta = ""
                historico.append(f"Maria: {msg.content}")

        partes = []
        if instrucoes:
            partes.append("Instruções adicionais:\n" + "\n".join(instrucoes))
        if historico:
            partes.append("Histórico da conversa:\n" + "\n".join(historico))
        if partes:
            partes.append("Pergunta atual: " + pergunta)
            return "\n\n".join(partes)
        return pergunta

    def _perguntar(self, texto: str) -> str:
        base = self.base_url.rstrip("/")
        # 1. Inicia a conversa (o segredo é usado só aqui, no servidor)
        r = requests.post(f"{base}/conversations", headers=self._headers(self.secret), timeout=30)
        r.raise_for_status()
        conv = r.json()
        conv_id, token = conv["conversationId"], conv.get("token") or self.secret
        h = self._headers(token)

        # 2. Envia a pergunta
        r = requests.post(
            f"{base}/conversations/{conv_id}/activities",
            headers=h,
            json={"type": "message", "from": {"id": self.user_id}, "text": texto, "locale": "pt-BR"},
            timeout=30,
        )
        r.raise_for_status()
        msg_id = r.json().get("id")

        # 3. Aguarda as respostas do agente a essa pergunta
        watermark, respostas, ultima = None, [], None
        limite = time.monotonic() + self.timeout
        while time.monotonic() < limite:
            params = {"watermark": watermark} if watermark else {}
            r = requests.get(f"{base}/conversations/{conv_id}/activities", headers=h, params=params, timeout=30)
            r.raise_for_status()
            dados = r.json()
            watermark = dados.get("watermark", watermark)
            for act in dados.get("activities", []):
                if act.get("from", {}).get("id") == self.user_id or act.get("type") != "message":
                    continue
                if msg_id and act.get("replyToId") not in (None, msg_id):
                    continue
                if act.get("replyToId") is None and not respostas and msg_id:
                    continue  # ignora a saudação inicial do agente
                if act.get("text"):
                    respostas.append(act["text"])
                    ultima = time.monotonic()
            if respostas and ultima and time.monotonic() - ultima >= self.quiet_period:
                break
            time.sleep(self.poll_interval)

        if not respostas:
            msg = f"A Maria não respondeu em {self.timeout:.0f}s."
            raise TimeoutError(msg)
        return "\n\n".join(respostas)

    # ---------------------------------------------------------------- LangChain
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        texto = self._perguntar(self._montar_texto(messages))
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=texto))])

    @property
    def _llm_type(self) -> str:
        return "maria-cmaa-directline"


class MariaCopilotModelComponent(LCModelComponent):
    display_name = "Maria (Copilot CMAA)"
    description = "Conversa com o agente Maria do Copilot Studio pelo Direct Line."
    icon = "Bot"
    name = "MariaCopilotModel"

    inputs = [
        *LCModelComponent._base_inputs,
        SecretStrInput(
            name="secret",
            display_name="Segredo Direct Line",
            info="Copilot Studio > Configurações > Segurança > Segurança de canal Web. "
            "Se vazio, usa a variável MARIA_DIRECTLINE_SECRET.",
            required=False,
        ),
        StrInput(
            name="base_url",
            display_name="URL Direct Line",
            value="",
            info="Deixe vazio para o padrão. Se vazio, usa MARIA_DIRECTLINE_URL ou " + DIRECTLINE_URL,
            advanced=True,
        ),
        FloatInput(name="timeout", display_name="Timeout (s)", value=120, advanced=True),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        secret = self.secret or os.getenv("MARIA_DIRECTLINE_SECRET", "")
        if not secret:
            msg = "Informe o segredo Direct Line (campo do componente ou variável MARIA_DIRECTLINE_SECRET)."
            raise ValueError(msg)
        return MariaCMAAChatModel(
            secret=secret,
            base_url=self.base_url or os.getenv("MARIA_DIRECTLINE_URL") or DIRECTLINE_URL,
            timeout=float(self.timeout or 120),
        )
