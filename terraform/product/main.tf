# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

data "juju_model" "charm" {
  name = var.model
}

data "juju_model" "charm_db" {
  name = var.db_model

  provider = juju.charm_db
}

module "charm_name" {
  source      = "../charm"
  app_name    = var.charm_name.app_name
  channel     = var.charm_name.channel
  config      = var.charm_name.config
  model       = data.juju_model.charm_name.name
  constraints = var.charm_name.constraints
  revision    = var.charm_name.revision
  base        = var.charm_name.base
  units       = var.charm_name.units
}

module "postgresql" {
  source          = "git::https://github.com/canonical/postgresql-operator//terraform"
  app_name        = var.postgresql.app_name
  channel         = var.postgresql.channel
  config          = var.postgresql.config
  constraints     = var.postgresql.constraints
  juju_model_name = data.juju_model.charm_db.name
  revision        = var.postgresql.revision
  base            = var.postgresql.base
  units           = var.postgresql.units

  providers = {
    juju = juju.charm_db
  }
}

resource "juju_offer" "postgresql" {
  model            = data.juju_model.charm_db.name
  application_name = module.postgresql.application_name
  endpoint         = module.postgresql.provides.database

  provider = juju.charm_db
}

resource "juju_access_offer" "postgresql" {
  offer_url = juju_offer.postgresql.url
  admin     = [var.db_model_user]
  consume   = [var.model_user]

  provider = juju.charm_db
}

resource "juju_integration" "charm_name_postgresql_database" {
  model = data.juju_model.charm_name.name

  application {
    name     = module.charm_name.app_name
    endpoint = module.charm_name.requires.postgresql
  }

  application {
    offer_url = juju_offer.postgresql.url
  }
}
