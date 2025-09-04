#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Netbox Charm entrypoint."""

import logging
import typing

import ops
import paas_charm.django

logger = logging.getLogger(__name__)

# Pylint does not like the way we use super() here.
# pylint: disable=useless-parent-delegation


class NetboxCharm(paas_charm.django.Charm):
    """Netbox Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)


if __name__ == "__main__":
    ops.main(NetboxCharm)
