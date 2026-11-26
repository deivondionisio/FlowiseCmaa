FROM langflowai/langflow:1.13.4

# Dependências extras: driver do SAP HANA / Datasphere
USER root
RUN (command -v uv >/dev/null && uv pip install --python "$(command -v python)" --no-cache hdbcli sqlalchemy-hana) \
    || (python -m ensurepip && python -m pip install --no-cache-dir hdbcli sqlalchemy-hana)

# Componentes customizados da CMAA (Maria / Datasphere)
COPY --chown=1000:0 components /app/components
RUN mkdir -p /app/langflow && chown -R 1000:0 /app/langflow

USER 1000
ENV LANGFLOW_COMPONENTS_PATH=/app/components \
    LANGFLOW_CONFIG_DIR=/app/langflow \
    LANGFLOW_HOST=0.0.0.0 \
    LANGFLOW_PORT=7860

EXPOSE 7860
CMD ["python", "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
