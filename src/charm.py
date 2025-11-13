#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more at: https://documentation.ubuntu.com/juju/3.6/howto/manage-charms/#build-a-charm

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

https://discourse.charmhub.io/t/4208
"""

import logging
import typing

import ops

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)

VALID_LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]


class Charm(ops.CharmBase):
    """Charm implementing holistic reconciliation pattern.

    The holistic pattern centralizes all state reconciliation logic into a single
    reconcile method that is called from all event handlers. This ensures consistency
    and reduces code duplication.
    """

    def __init__(self, *args: typing.Any):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)

    def reconcile(self) -> None:
        """Holistic reconciliation method.

        This method contains all the logic needed to reconcile the charm state.
        It is idempotent and can be called from any event handler.
        """
        # Validate configuration
        log_level = str(self.model.config["log-level"]).lower()
        if log_level not in VALID_LOG_LEVELS:
            self.unit.status = ops.BlockedStatus(f"invalid log level: '{log_level}'")
            return

        # Configure logging based on charm config
        numeric_level = getattr(logging, log_level.upper(), None)
        if numeric_level is not None:
            logger.setLevel(numeric_level)

        logger.info("Charm reconciliation started with log level: %s", log_level)

        # Add your charm logic here:
        # For Kubernetes charms: interact with Pebble to manage containers
        # For machine charms: manage systemd services, install packages, configure files
        # For charms with relations: process relation data and configure integrations

        logger.debug("Charm reconciliation completed successfully")

        # Learn more about statuses in the SDK docs:
        # https://documentation.ubuntu.com/juju/latest/reference/status/index.html
        self.unit.status = ops.ActiveStatus()

    def _on_install(self, _: ops.InstallEvent) -> None:
        """Handle install event."""
        self.reconcile()

    def _on_start(self, _: ops.StartEvent) -> None:
        """Handle start event."""
        self.reconcile()

    def _on_config_changed(self, _: ops.ConfigChangedEvent) -> None:
        """Handle changed configuration."""
        self.reconcile()


if __name__ == "__main__":  # pragma: nocover
    ops.main(Charm)
