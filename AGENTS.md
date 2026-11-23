# Knowledge Base

IMPORTANT: Read the `.kb/agents.md` file.

- [.kb/agents.md](.kb/agents.md) - Structure and rules of the knowledge base. You MUST read this file.

# Agent guidelines

## Project overview

This project contains a [Juju](https://juju.is) charm.

## Build and test commands

- Build the charm with `charmcraft pack`
- Test the charm with `charmcraft test`

## Testing instructions

- Unit tests lives in `tests/unit`
- Unit tests must be implemented using [ops.testing](https://github.com/canonical/operator)
- Integration tests lives in `tests/integration`
- Integration tests should be implemented using [jubilant](https://github.com/canonical/jubilant)
