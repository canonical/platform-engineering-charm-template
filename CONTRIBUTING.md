<!-- Remember to update this file for your charm -- replace <charm-name> with the appropriate name. -->

# Contributing

This document explains the processes and practices recommended for contributing enhancements to the <charm-name> charm.

## Overview

- Generally, before developing enhancements to this charm, you should consider [opening an issue
  ](link to issues page) explaining your use case.
- If you would like to chat with us about your use-cases or proposed implementation, you can reach
  us at [Canonical Matrix public channel](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)
  or [Discourse](https://discourse.charmhub.io/).
- Familiarizing yourself with the [Juju documentation](https://canonical-juju.readthedocs-hosted.com/en/latest/user/howto/manage-charms/)
  will help you a lot when working on new features or bug fixes.
- All enhancements require review before being merged. Code review typically examines
  - code quality
  - test coverage
  - user experience for Juju operators of this charm.
- Once your pull request is approved, we squash and merge your pull request branch onto
  the `main` branch. This creates a linear Git commit history.
- For further information on contributing, please refer to our
  [Contributing Guide](https://github.com/canonical/is-charms-contributing-guide).

## Code of conduct

When contributing, you must abide by the
[Ubuntu Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct).

## Releases and versions

This project uses [semantic versioning](https://semver.org/).

Please ensure that any new feature, fix, or significant change is documented by
adding an entry to the [CHANGELOG.md](link-to-changelog) file.

To learn more about changelog best practices, visit [Keep a Changelog](https://keepachangelog.com/).

## Submissions

If you want to address an issue or a bug in this project,
notify in advance the people involved to avoid confusion;
also, reference the issue or bug number when you submit the changes.

- [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks)
  our [GitHub repository](link-to-github-repo)
  and add the changes to your fork, properly structuring your commits,
  providing detailed commit messages and signing your commits.
- Make sure the updated project builds and runs without warnings or errors;
  this includes linting, documentation, code and tests.
- Submit the changes as a
  [pull request (PR)](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

Your changes will be reviewed in due time; if approved, they will be eventually merged.

### Describing pull requests

To be properly considered, reviewed and merged,
your pull request must provide the following details:

- **Title**: Summarize the change in a short, descriptive title.

- **Overview**: Describe the problem that your pull request solves.
  Mention any new features, bug fixes or refactoring.

- **Rationale**: Explain why the change is needed.

- **Juju Events Changes**: Describe any changes made to Juju events, or
  "None" if the pull request does not change any Juju events.

- **Module Changes**: Describe any changes made to the module, or "None"
  if your pull request does not change the module.

- **Library Changes**: Describe any changes made to the library,
  or "None" is the library is not affected.

- **Checklist**: Complete the following items:

  - The [charm style guide](https://documentation.ubuntu.com/juju/3.6/reference/charm/charm-development-best-practices/) was applied
  - The [contributing guide](https://github.com/canonical/is-charms-contributing-guide) was applied
  - The changes are compliant with [ISD054 - Managing Charm Complexity](https://discourse.charmhub.io/t/specification-isd014-managing-charm-complexity/11619)
  - The documentation is updated
  - The PR is tagged with appropriate label (trivial, senior-review-required)
  - The changelog has been updated

### Signing commits

To improve contribution tracking,
we use the [Canonical contributor license agreement](https://assets.ubuntu.com/v1/ff2478d1-Canonical-HA-CLA-ANY-I_v1.2.pdf)
(CLA) as a legal sign-off, and we require all commits to have verified signatures.

#### Canonical contributor agreement

Canonical welcomes contributions to the Discourse charm. Please check out our
[contributor agreement](https://ubuntu.com/legal/contributors) if you're interested in contributing to the solution.

The CLA sign-off is simple line at the
end of the commit message certifying that you wrote it
or have the right to commit it as an open-source contribution.

#### Verified signatures on commits

All commits in a pull request must have cryptographic (verified) signatures.
To add signatures on your commits, follow the
[GitHub documentation](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

## Develop

To make contributions to this charm, you'll need a working
[development setup](https://documentation.ubuntu.com/juju/latest/user/howto/manage-your-deployment/manage-your-deployment-environment/).

The code for this charm can be downloaded as follows:

```
git clone https://github.com/canonical/<charm-name>
```

You can create an environment for development with `python3-venv`.
We will also install `tox` inside the virtual environment for testing:

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install tox
```

### Test

This project uses `tox` for managing test environments. There are some pre-configured environments
that can be used for linting and formatting code when you're preparing contributions to the charm:

* ``tox``: Executes all of the basic checks and tests (``lint``, ``unit``, ``static``, and ``coverage-report``).
* ``tox -e fmt``: Runs formatting using ``black`` and ``isort``.
* ``tox -e lint``: Runs a range of static code analysis to check the code.
* ``tox -e static``: Runs other checks such as ``bandit`` for security issues.

### Build the rock and charm

Use [Rockcraft](https://documentation.ubuntu.com/rockcraft/en/latest/) to create an
OCI image for the <charm-name> app, and then upload the image to a MicroK8s registry,
which stores OCI archives so they can be downloaded and deployed.

Enable the MicroK8s registry:

```bash
microk8s enable registry
```

The following commands pack the OCI image and push it into
the MicroK8s registry:

```bash
cd <project_dir>
rockcraft pack
skopeo --insecure-policy copy --dest-tls-verify=false oci-archive:<rock-name>.rock docker://localhost:32000/<app-name>:latest
```

Build the charm in this git repository using:

```shell
charmcraft pack
```

### Deploy

```bash
# Create a model
juju add-model charm-dev
# Enable DEBUG logging
juju model-config logging-config="<root>=INFO;unit=DEBUG"
# Deploy the charm
juju deploy ./<charm-name>.charm 
```


