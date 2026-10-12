# Horizon condition cards - POC container for AWS App Runner.
FROM node:22-alpine

ENV NODE_ENV=production \
    PORT=8080 \
    SERVE_DEMO=true

WORKDIR /app

# Dependencies first, so editing a card does not invalidate the npm layer.
COPY server/package.json ./server/
RUN cd server && npm install --omit=dev --no-audit --no-fund

# The app, and the data it serves.
COPY server/ ./server/
COPY cards/ ./cards/
COPY data/ ./data/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1

WORKDIR /app/server
CMD ["node", "server.js"]
