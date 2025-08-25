# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Useful types for integration tests."""

from typing import NamedTuple


class App(NamedTuple):
    """Holds deployed application information for app_fixture."""

    name: str
