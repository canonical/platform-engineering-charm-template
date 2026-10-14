# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "application" {
  description = "The deployed application object."
  value       = juju_application.netbox-k8s
}

output "provides" {
  description = "Map of the provided integration endpoints."
  # Add one entry per `provides` endpoint declared in charmcraft.yaml, e.g.:
  # metrics = {
  #   kind       = "endpoint"
  #   name       = juju_application.netbox-k8s.name
  #   endpoint   = "metrics-endpoint"
  #   controller = null
  # }
  value = {}
}

output "requires" {
  description = "Map of the required integration endpoints."
  # Add one entry per `requires` endpoint declared in charmcraft.yaml, e.g.:
  # ingress = {
  #   kind       = "endpoint"
  #   name       = juju_application.netbox-k8s.name
  #   endpoint   = "ingress"
  #   controller = null
  # }
  value = {}
}
