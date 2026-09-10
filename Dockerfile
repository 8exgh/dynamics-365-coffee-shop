FROM node:22-bookworm-slim AS web
WORKDIR /build
COPY web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

FROM python:3.12-slim-bookworm AS runtime
ARG GIT_COMMIT=local
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 COFFEE_DATABASE=/app/data/coffee.db COFFEE_STATIC=/app/web/dist GIT_COMMIT=${GIT_COMMIT}
WORKDIR /app
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock && groupadd --gid 1000 coffee && useradd --uid 1000 --gid coffee --no-create-home coffee && mkdir /app/data && chown coffee:coffee /app/data
COPY --chown=coffee:coffee app/ ./app/
COPY --from=web --chown=coffee:coffee /build/dist ./web/dist
USER coffee
EXPOSE 3000
HEALTHCHECK --interval=20s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/api/health', timeout=3)"
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "3000", "--no-proxy-headers"]
