"""Locust load profile for the full ACP stack (ACA + MTS + ACP).

Usage:
  locust -f docker/locustfile.py

Optional host overrides:
  ACA_HOST=http://localhost:2810
  MTS_HOST=http://localhost:1745
  ACP_HOST=http://localhost:10124
"""

import os

from locust import HttpUser, between, task


def env_host(name: str, default: str) -> str:
    return os.getenv(name, default).rstrip("/")


class ACAUser(HttpUser):
    host = env_host("ACA_HOST", "http://localhost:2810")
    wait_time = between(0.5, 2.0)

    @task(2)
    def info(self):
        self.client.get("/info", name="aca:/info")

    @task(4)
    def repositories(self):
        self.client.get("/repositories", name="aca:/repositories")

    @task(1)
    def metrics(self):
        self.client.get("/metrics", name="aca:/metrics")


class MTSUser(HttpUser):
    host = env_host("MTS_HOST", "http://localhost:1745")
    wait_time = between(0.5, 2.0)

    @task(2)
    def info(self):
        self.client.get("/info", name="mts:/info")

    @task(3)
    def xsl_list(self):
        self.client.get("/saved-xsl-list-only", name="mts:/saved-xsl-list-only")

    @task(2)
    def xsl_by_name(self):
        self.client.get(
            "/saved-xsl-list?xslt_name=rda-form-metadata-to-zenodo-dataset-v5.xsl",
            name="mts:/saved-xsl-list?xslt_name",
        )

    @task(1)
    def metrics(self):
        self.client.get("/metrics", name="mts:/metrics")


class ACPUser(HttpUser):
    host = env_host("ACP_HOST", "http://localhost:10124")
    wait_time = between(0.5, 2.0)

    @task(2)
    def root(self):
        self.client.get("/", name="acp:/")

    @task(3)
    def available_plugins(self):
        self.client.get("/available-plugins", name="acp:/available-plugins")

    @task(1)
    def metrics(self):
        self.client.get("/metrics", name="acp:/metrics")

