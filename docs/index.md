A Juju charm deploying and managing
[NetBox](https://github.com/netbox-community/netbox/) on
Kubernetes. NetBox is the go-to solution for modeling and documenting network
infrastructure for thousands of organizations worldwide.

This charm simplifies initial deployment and "day N" operations of
NetBox on Kubernetes, such as integration with SSO, access to S3 for
file storage and more. It allows for deployment on many
different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
to [Charmed Kubernetes](https://ubuntu.com/kubernetes) to public cloud
Kubernetes offerings.

As such, the charm makes it easy for those looking to take control of
their own NetBox server whilst keeping operations simple, and gives them
the freedom to deploy on the Kubernetes platform of their choice.

For DevOps or SRE teams this charm will make operating NetBox simple
and straightforward through Juju's clean interface. It will allow easy
deployment into multiple environments for testing of changes.

## Limitations

The NetBox charm is designed for a high availability (HA) deployment. 
This implies that it can be scaled to more than one units.

This implies that File Upload cannot be used for scripts and reports,
as the file will be uploaded to only one of the units. Besides, if the
pod gets rescheduled, those files will be lost.

Giving the limitations of NetBox for scripts and reports, the alternative
is using a Data Source, and creating the scripts and reports from
the Data Source, using the "Auto sync enabled" checkbox. Using this checkbox,
the scripts and reports will be synchronized every five minutes in all
units. See [Configure Scripts and Reports for HA](how-to/configure-scripts-reports.md)
for more information.

## Other resources

* [NetBox upstream repository](https://github.com/netbox-community/netbox)
* [Get support](https://discourse.charmhub.io/)
* [Join our online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com)
* [Contribute](https://charmhub.io/netbox-k8s/docs/contributing)
* [Getting Started](https://charmhub.io/netbox-k8s/docs/getting-started)
* [Juju SDK documentation](https://juju.is/docs/sdk) for more information about developing and improving charms.

## Contributing to this documentation

Documentation is an important part of this project, and we take the
same open-source approach to the documentation as the code. As such,
we welcome community contributions, suggestions and constructive
feedback on our documentation. Our documentation is hosted on the
[Charmhub forum](https://discourse.charmhub.io/) to enable easy
collaboration. Please use the “Help us improve this documentation”
links on each documentation page to either directly change something
you see that’s wrong, or ask a question, or make a suggestion about a
potential change via the comments section.

If there’s a particular area of documentation that you’d like to see that’s
missing, please [file a bug](https://github.com/canonical/netbox-k8s-operator/issues).

# Contents

1. [Tutorial](tutorial)
  1. [Getting Started](tutorial/getting-started.md)
  1. [Testing NetBox](tutorial/testing-netbox.md)
1. [How To](how-to)
  1. [Contribute](how-to/contribute.md)
  2. [Configure SAML](how-to/configure-saml.md)
  3. [Configure Scripts and Reports for HA](how-to/configure-scripts-reports.md)
1. [Reference](reference)
  1. [Actions](reference/actions.md)
  2. [Integrations](reference/integrations.md)
1. [Explanation](explanation)
  1. [Charm Architecture](explanation/charm-architecture.md)
