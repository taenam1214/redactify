FROM python:3.12-slim

LABEL maintainer="taenam1214"
LABEL description="Redactify — Privacy-preserving document redaction tool"

WORKDIR /app

# Install redactify and spaCy model
COPY . .
RUN pip install --no-cache-dir ".[all]" \
    && python -m spacy download en_core_web_sm

ENTRYPOINT ["redactify"]
CMD ["--help"]
