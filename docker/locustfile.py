"""Locust load profile for the full ACP stack (ACA + MTS + ACP).

Each user class targets its own service via absolute URLs, so all three
services are exercised in a single Locust session regardless of the "Host"
value entered in the web UI.

Usage (web UI):
  locust -f docker/locustfile.py          # open http://localhost:8089

Usage (headless):
  locust -f docker/locustfile.py --headless --users 30 --spawn-rate 5 --run-time 2m

Optional host overrides (env vars):
  ACA_HOST=http://localhost:2810
  MTS_HOST=http://localhost:1745
  ACP_HOST=http://localhost:10124
"""

import os

from locust import HttpUser, between, task


def env_host(name: str, default: str) -> str:
    return os.getenv(name, default).rstrip("/")


# Resolved once at startup so every task can use absolute URLs.
# Absolute URLs bypass the web-UI "Host" field, ensuring each class always
# hits the correct service.
ACA = env_host("ACA_HOST", "http://localhost:2810")
MTS = env_host("MTS_HOST", "http://localhost:1745")
ACP = env_host("ACP_HOST", "http://localhost:10124")

# Locust 2.x filters user classes by the host submitted from the web-UI form.
# If each class declares a different host, only the matching class is spawned.
# Using a single shared placeholder bypasses that filter while absolute URLs
# in every task still route each request to the correct service.
_PLACEHOLDER_HOST = "http://localhost"


class ACAUser(HttpUser):
    host = _PLACEHOLDER_HOST
    wait_time = between(0.5, 2.0)

    @task(2)
    def info(self):
        self.client.get(f"{ACA}/info", name="aca:/info")

    @task(4)
    def repositories(self):
        self.client.get(f"{ACA}/repositories", name="aca:/repositories")

    @task(1)
    def metrics(self):
        self.client.get(f"{ACA}/metrics", name="aca:/metrics")


class MTSUser(HttpUser):
    host = _PLACEHOLDER_HOST
    wait_time = between(0.5, 2.0)

    @task(2)
    def info(self):
        self.client.get(f"{MTS}/info", name="mts:/info")

    @task(3)
    def xsl_list(self):
        self.client.get(f"{MTS}/saved-xsl-list-only", name="mts:/saved-xsl-list-only")

    @task(2)
    def xsl_by_name(self):
        self.client.get(
            f"{MTS}/saved-xsl-list?xslt_name=rda-form-metadata-to-zenodo-dataset-v5.xsl",
            name="mts:/saved-xsl-list?xslt_name",
        )

    @task(1)
    def metrics(self):
        self.client.get(f"{MTS}/metrics", name="mts:/metrics")


class ACPUser(HttpUser):
    host = _PLACEHOLDER_HOST
    wait_time = between(0.5, 2.0)

    @task(2)
    def root(self):
        self.client.get(f"{ACP}/", name="acp:/")

    @task(3)
    def available_plugins(self):
        self.client.get(f"{ACP}/available-plugins", name="acp:/available-plugins")

    @task(1)
    def metrics(self):
        self.client.get(f"{ACP}/metrics", name="acp:/metrics")
