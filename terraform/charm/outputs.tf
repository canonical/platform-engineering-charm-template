# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.charm_name.name
}

output "requires" {
  value = {
    ingress       = "ingress"
    logging       = "logging"
    postgresql    = "postgresql"
    traefik_route = "traefik-route"
  }
}

output "provides" {
  value = {
    grafana_dashboard = "grafana-dashboard"
    metrics_endpoint  = "metrics-endpoint"
  }
}
