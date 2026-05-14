FROM mcr.microsoft.com/playwright:v1.58.2-noble

RUN apt-get update && apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-cli

WORKDIR /app
COPY . .
RUN npm ci && chmod +x scripts/pnkln-test.sh scripts/judge6.sh scripts/cleanup-cinematic-videos.sh
ENTRYPOINT ["./scripts/pnkln-test.sh"]
