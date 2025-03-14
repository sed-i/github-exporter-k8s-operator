#!/usr/bin/env python3
# Copyright 2025 Canonical
# See LICENSE file for licensing details.

"""Charmed github-exporter."""

import logging
import os
import socket

import ops
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from ops.pebble import Layer

logger = logging.getLogger(__name__)


def get_pebble_layer(config) -> Layer:
    """Construct the Pebble layer informataion."""
    return Layer(
        {
            "summary": "github-exporter",
            "description": "github-exporter",
            "services": {
                "github-exporter": {
                    "override": "replace",
                    "summary": "github-exporter service",
                    "command": "/bin/main",
                    "startup": "enabled",
                    "environment": {
                        "https_proxy": os.environ.get("JUJU_CHARM_HTTPS_PROXY", ""),
                        "http_proxy": os.environ.get("JUJU_CHARM_HTTP_PROXY", ""),
                        "no_proxy": os.environ.get("JUJU_CHARM_NO_PROXY", ""),
                        "ORGS": config.get("orgs", ""),
                        "REPOS": config.get("repos", ""),
                        "USERS": config.get("users", ""),
                        "GITHUB_TOKEN": config.get("github_token", ""),
                    },
                }
            },
        }
    )



class GithubExporterK8SCharm(ops.CharmBase):
    container_name = "github-exporter"

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.container = self.unit.get_container(self.container_name)

        if not self.container.can_connect():
            self.unit.status = ops.MaintenanceStatus("Waiting for container to start")
            return

        self.reconcile()

    def reconcile(self):
        self.unit.set_ports(9171)

        self.container.add_layer(self.container_name, get_pebble_layer(self.model.config), combine=True)
        self.container.replan()

        self.setup_scrape()

        self.unit.status = ops.ActiveStatus()

    def setup_scrape(self):
        scraping = MetricsEndpointProvider(
            self,
            relation_name="metrics-endpoint",
            jobs=[{
                "scheme": "http",
                "static_configs": [{"targets": ["*:9171"]}],
            }],
            external_url=socket.getfqdn(),
        )
        scraping.set_scrape_job_spec()


if __name__ == "__main__":  # pragma: nocover
    ops.main(GithubExporterK8SCharm)
