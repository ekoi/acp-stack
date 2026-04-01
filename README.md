# ACP Stack

`acp-stack` is a mono-repo that contains the services needed to run the Automated Curation Platform stack locally with Docker Compose.

## Services in this stack

Core services:
- `acp` (`automated_curation_platform`) - main API and orchestration service (`http://localhost:10124`)
- `aca` (`acp_config_assistant`) - config assistant service (`http://localhost:2810`)
- `mts` (`metadata_transformation_service`) - metadata transformer service (`http://localhost:1745`)
- `keycloak` (`acp_keycloak`) - local identity provider for auth flows (`http://localhost:8080`)
- `acp_postgres` - PostgreSQL for ACP (`localhost:5432`)
- `maildev` - local SMTP + UI (`http://localhost:1080`, SMTP `localhost:1025`)

Observability services:
- `grafana` (`http://localhost:3000`)
- `prometheus` (`http://localhost:9191`)
- `loki` (`http://localhost:3100`)
- `promtail`
- `tempo` (`http://localhost:3200`)

## Docker Compose (full stack)

Use `docker/docker-compose-full-stack.yaml` to run all services.

### 1) Start full stack

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml up -d --build
```

### 2) Check running services

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml ps
```

### 3) Follow logs

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml logs -f
```

Single service logs example:

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml logs -f acp
```

### 4) Restart a service

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml restart acp
```

### 5) Stop full stack

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml down
```

### 6) Stop full stack and remove volumes (clean reset)

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml down -v
```

## Notes

- The stack uses `docker/scripts/bootstrap-secrets.sh` to ensure `conf/.secrets.toml` exists (copied from `.secrets.toml.example` when missing).
- `keycloak` can be used in combination with `dans-frontend-framework` for local authentication integration:
  - https://github.com/DANS-KNAW/dans-frontend-framework
- After first startup, open Grafana at `http://localhost:3000`.

## Grafana dashboard links

Use these links after the full stack is running:

- Grafana home: `http://localhost:3000`
- Provisioned ACP dashboard (UID `acp-observability`):
  - `http://localhost:3000/d/acp-observability/acp-monitoring`
  - `http://localhost:3000/d/acp-observability/acp-monitoring?orgId=1&refresh=5s`

Default Grafana credentials (from compose):
- username: `admin`
- password: `admin1`

