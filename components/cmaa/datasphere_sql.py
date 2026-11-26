"""Componente Langflow: executa um SELECT no SAP Datasphere (HANA Cloud)."""
import os

from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, MultilineInput, Output, SecretStrInput, StrInput
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message


class DatasphereSQLComponent(Component):
    display_name = "SAP Datasphere SQL"
    description = "Executa uma consulta SELECT no SAP Datasphere e retorna o resultado."
    icon = "Database"
    name = "DatasphereSQL"

    inputs = [
        StrInput(name="host", display_name="Host", info="Se vazio, usa DS_HOST."),
        IntInput(name="port", display_name="Porta", value=443, advanced=True),
        StrInput(name="user", display_name="Usuário", info="Formato ESPACO#USUARIO. Se vazio, usa DS_USER."),
        SecretStrInput(name="password", display_name="Senha", info="Se vazio, usa DS_PASSWORD.", required=False),
        MultilineInput(
            name="query",
            display_name="SQL",
            info="Apenas SELECT/WITH. Use aspas duplas em schema/view: \"ESPACO\".\"VIEW\"",
            tool_mode=True,
        ),
        IntInput(name="max_rows", display_name="Máx. linhas", value=500, advanced=True),
    ]

    outputs = [
        Output(display_name="Tabela", name="dataframe", method="run_dataframe"),
        Output(display_name="Texto", name="text", method="run_text"),
    ]

    def _run(self):
        from hdbcli import dbapi

        sql = (self.query or "").strip().rstrip(";")
        if not sql.upper().startswith(("SELECT", "WITH")):
            msg = "Apenas consultas SELECT/WITH são permitidas."
            raise ValueError(msg)

        conn = dbapi.connect(
            address=self.host or os.getenv("DS_HOST", ""),
            port=int(self.port or os.getenv("DS_PORT", "443")),
            user=self.user or os.getenv("DS_USER", ""),
            password=self.password or os.getenv("DS_PASSWORD", ""),
            encrypt=True,
            sslValidateCertificate=True,
        )
        try:
            cur = conn.cursor()
            cur.execute(sql)
            cols = [c[0] for c in cur.description]
            rows = cur.fetchmany(int(self.max_rows or 500))
        finally:
            conn.close()
        return cols, rows

    def run_dataframe(self) -> DataFrame:
        cols, rows = self._run()
        df = DataFrame([dict(zip(cols, r)) for r in rows])
        self.status = f"{len(rows)} linha(s)"
        return df

    def run_text(self) -> Message:
        cols, rows = self._run()
        if not rows:
            return Message(text="A consulta não retornou linhas.")
        linhas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        linhas += ["| " + " | ".join("" if v is None else str(v) for v in r) + " |" for r in rows]
        self.status = f"{len(rows)} linha(s)"
        return Message(text="\n".join(linhas))
