# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "Reference to the k8s Juju model to deploy application to."
  type        = string
}

variable "db_model" {
  description = "Reference to the VM Juju model to deploy database charm to."
  type        = string
}

variable "model_user" {
  description = "Juju user used for deploying the application."
  type        = string
}

variable "db_model_user" {
  description = "Juju user used for deploying database charms."
  type        = string
}

variable "charm_name" {
  type = object({
    app_name    = optional(string, "<charm-name>")
    channel     = optional(string, "latest/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    revision    = optional(number)
    base        = optional(string, "ubuntu@24.04")
    units       = optional(number, 1)
  })
}

variable "postgresql" {
  type = object({
    app_name    = optional(string, "postgresql")
    channel     = optional(string, "14/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    revision    = optional(number)
    base        = optional(string, "ubuntu@22.04")
    units       = optional(number, 1)
  })
}
