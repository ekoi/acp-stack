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

## Load testing with Locust

The stack includes a [Locust](https://locust.io/) container for load/stress testing all three core services (ACA, MTS, ACP).

### Locustfile

`docker/locustfile.py` defines three user classes, one per service:

| User class | Target service | Simulated endpoints |
|---|---|---|
| `ACAUser` | `aca` (`http://aca:2810`) | `GET /info`, `GET /repositories`, `GET /metrics` |
| `MTSUser` | `mts` (`http://mts:1745`) | `GET /info`, `GET /saved-xsl-list-only`, `GET /saved-xsl-list?xslt_name`, `GET /metrics` |
| `ACPUser` | `acp` (`http://acp:10124`) | `GET /`, `GET /available-plugins`, `GET /metrics` |

Each class uses a random wait time between **0.5 – 2 s** between requests, and individual endpoints are weighted with Locust `@task` weights.

> **Why absolute URLs?**  
> Locust's web UI has a single *Host* field that, when filled in, overrides the `host` attribute of **all** user classes — causing only the matching service to receive traffic. To avoid this, every task uses a fully-qualified URL built from module-level constants (`ACA`, `MTS`, `ACP`) resolved from environment variables at startup. Locust's HTTP client passes absolute URLs through as-is, so all three services are tested simultaneously and the web UI *Host* field is ignored.

### Locust container

The `locust` service in `docker-compose-full-stack.yaml` starts automatically **after** `acp`, `aca`, and `mts` are healthy. Key settings:

```yaml
locust:
  image: locustio/locust:latest
  container_name: acp_locust
  ports:
    - "8089:8089"   # Locust web UI
  volumes:
    - ./locustfile.py:/mnt/locust/locustfile.py:ro
  command: -f /mnt/locust/locustfile.py --users 3 --spawn-rate 1 --autostart
  environment:
    ACA_HOST: "http://aca:2810"
    MTS_HOST: "http://mts:1745"
    ACP_HOST: "http://acp:10124"
```

> The `restart` directive is intentionally commented out so Locust does not keep restarting after a test run finishes.

### Running a load test

#### Option A — Locust web UI (recommended)

1. Start the full stack (Locust starts together with it):
   ```bash
   cd /Users/akmi/dev/work/dans/acp-stack/docker
   docker compose -f docker-compose-full-stack.yaml up -d --build
   ```
2. Open the Locust web UI at **`http://localhost:8089`**.
3. Swarming starts automatically with defaults from compose (`--users 3 --spawn-rate 1 --autostart`).
4. The *Host* field can be ignored; requests still go to `aca`, `mts`, and `acp` via absolute URLs in `docker/locustfile.py`.
5. If you stop the run in the UI, use **Start** to begin again with your preferred values.

#### Option B — Headless / CI mode

Run Locust without the web UI by overriding the command:

```bash
cd /Users/akmi/dev/work/dans/acp-stack/docker
docker compose -f docker-compose-full-stack.yaml run --rm locust \
  -f /mnt/locust/locustfile.py \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --host http://acp:10124
```

#### Option C — Run locally against the live stack

You can run Locust directly on your machine against the already-running stack:

```bash
# Install locust if needed
pip install locust

# Run from the repo root
locust -f docker/locustfile.py \
  --headless \
  --users 20 \
  --spawn-rate 2 \
  --run-time 1m
```

The environment variables `ACA_HOST`, `MTS_HOST`, and `ACP_HOST` default to the local ports (`http://localhost:2810`, `http://localhost:1745`, `http://localhost:10124`) when not set.

---

## Notes

- The stack uses `docker/scripts/bootstrap-secrets.sh` to ensure `conf/.secrets.toml` exists (copied from `.secrets.toml.example` when missing).
- `keycloak` can be used in combination with `dans-frontend-framework` for local authentication integration:
  - https://github.com/DANS-KNAW/dans-frontend-framework
- After first startup, open Grafana at `http://localhost:3000`.

## GitHub Actions runner setup on the Mac mini

To let GitHub Actions pick up the `CI` and `Deploy` jobs for this repo, register a **self-hosted runner** on the Mac mini with these labels:

- `self-hosted`
- `macOS`
- `X64`
- `acp-stack`

### 1) Create a runner directory

```bash
mkdir -p /Users/akmi/actions-runner
cd /Users/akmi/actions-runner
```

### 2) Download the runner

Choose the archive that matches the Mac mini CPU:

```bash
# Intel / x64
curl -o actions-runner-osx-x64.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-osx-x64-2.323.0.tar.gz
```

Extract the archive you downloaded:

```bash
tar xzf actions-runner-*.tar.gz
```

### 3) Configure the runner

Create a GitHub repository registration token from:

- `https://github.com/ekoi/acp-stack/settings/actions/runners/new`

Then configure the runner:

```bash
cd /Users/akmi/actions-runner
./config.sh \
  --url https://github.com/ekoi/acp-stack \
  --token YOUR_REGISTRATION_TOKEN \
  --name mac-mini-acp-stack \
  --labels self-hosted,macOS,X64,acp-stack \
  --unattended
```


### 4) Install and start the runner as a service

```bash
cd /Users/akmi/actions-runner
sudo ./svc.sh install
sudo ./svc.sh start
```

### 5) Verify the runner

You should see the runner appear online in GitHub under:

```text
https://github.com/ekoi/acp-stack/settings/actions/runners
```

If the runner is online with the labels above, it can pick up:

- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`

## Grafana dashboard links

Use these links after the full stack is running:

- Grafana home: `http://localhost:3000`
- Provisioned ACP dashboard (UID `acp-observability`):
  - `http://localhost:3000/d/acp-observability/acp-monitoring`
  - `http://localhost:3000/d/acp-observability/acp-monitoring?orgId=1&refresh=5s`

Default Grafana credentials (from compose):
- username: `admin`
- password: `admin1`
