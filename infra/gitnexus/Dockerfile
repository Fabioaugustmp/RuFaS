# GitNexus CLI pinado. Requer Node >= 22.18 (ou >= 24.11).
FROM node:24-bookworm-slim

# git e toolchain nativa para pacotes com addons (tree-sitter, banco de grafo).
RUN apt-get update \
 && apt-get install -y --no-install-recommends git python3 make g++ ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN npm install -g gitnexus@1.6.12

# O índice fica em $HOME/.gitnexus; HOME aponta para o volume compartilhado.
ENV HOME=/data
WORKDIR /data

ENTRYPOINT ["gitnexus"]
