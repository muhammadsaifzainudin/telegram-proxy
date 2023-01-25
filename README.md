# Docker build
docker build -t saif/telegram-proxy .

# Docker run
docker run -d \
-e BOT_TOKEN=<BOT_TOKEN> \
-e CHAT_ID=<CHAT_ID> \
-p 0.0.0.0:8000:8000 \
saif/telegram-proxy