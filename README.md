<!-- vale Canonical.007-Headings-sentence-case = NO -->
# netbox-k8s-operator

[![CharmHub Badge](https://charmhub.io/netbox-k8s/badge.svg)](https://charmhub.io/netbox-k8s)
[![Publish to edge](https://github.com/canonical/netbox-k8s/actions/workflows/publish_charm.yaml/badge.svg)](https://github.com/canonical/netbox-k8s/actions/workflows/publish_charm.yaml)
[![Promote charm](https://github.com/canonical/netbox-k8s/actions/workflows/promote_charm.yaml/badge.svg)](https://github.com/canonical/netbox-k8s/actions/workflows/promote_charm.yaml)
[![Discourse Status](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.charmhub.io&style=flat&label=CharmHub%20Discourse)](https://discourse.charmhub.io)


A Juju charm deploying and managing NetBox on Kubernetes.

NetBox is the go-to solution for modeling and documenting network
infrastructure for thousands of organizations worldwide. As a
successor to legacy IPAM and DCIM applications, NetBox provides a
cohesive, extensive, and accessible data model for all things
networked.

Like any Juju charm, this charm supports one-line deployment, configuration, integration, scaling, and more. For Charmed NetBox, this includes:
- S3 integration
- Redis integration
- PostgreSQL integration
- SAML integration

It allows for deployment on many
different Kubernetes platforms, from MicroK8s to Charmed Kubernetes to
public cloud Kubernetes offerings.

<!-- I will add the link once the documentation posts on Discourse are ready -->
For information about how to deploy, integrate, and manage this charm, see the Official [platform-engineering-charm-template Documentation](external link). 


## Get started

To begin, refer to the [tutorial](https://charmhub.io/netbox-k8s/docs/tutorial-getting-started) for step-by-step instructions.

### Basic operations

The following actions are available for this charm:

* **create-superuser**: Create a new Django superuser account.
* **rotate-secret-key**: Rotate the secret key. Users will be forced to log in again. This might be useful if a security breach occurs.

You can obtain more information on the actions [here](https://charmhub.io/netbox-k8s/actions).

## Learn more

- [Read more](https://charmhub.io/netbox-k8s/docs)
- [Official Webpage](https://netboxlabs.com/)
- [Troubleshooting](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)

## Project and community

The netbox-k8s-operator is a member of the Ubuntu family. It's an open source project that warmly welcomes community projects, contributions, suggestions, fixes and constructive feedback.

* [Issues](https://github.com/canonical/netbox-k8s-operator/issues)
* [Contributing](https://github.com/canonical/netbox-k8s-operator/blob/main/CONTRIBUTING.md)
* [Matrix](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)
