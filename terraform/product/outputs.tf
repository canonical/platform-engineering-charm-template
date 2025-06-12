# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = module.charm_name.app_name
}

output "requires" {
  value = {
    logging = "logging"
  }
}

output "provides" {
  value = {
    grafana_dashboard = "grafana-dashboard"
    metrics_endpoint  = "metrics-endpoint"
  }
}
