<!-- vale Canonical.007-Headings-sentence-case = NO -->
# Test NetBox
<!-- vale Canonical.007-Headings-sentence-case = YES -->

We recommend the [Getting Started Tutorial](./getting-started.md) to get familiarised with NetBox in a Juju deployment.

This tutorial will allow you to test NetBox locally in the easiest possible way (not recommended for a production environment).

## What you'll do

- Install [Multipass](https://multipass.run)
- [Launch NetBox with a Multipass VM](#Launch NetBox with a Multipass VM)

## Prerequisites

You need a machine where Multipass can be installed. You will need 4GB of RAM for the VM, so it is recommended that
your computer has at least 8GB of RAM. Also 20GB of free disk space are needed.

Multipass can be easily installed in Linux, Windows and macOS. You will need a machine with amd64 architecture or an amd64 emulator,
as the NetBox charm is only built for amd64.

## Install Multipass

Follow the instruction in [https://multipass.run/install](https://multipass.run/install).

<!-- vale Canonical.007-Headings-sentence-case = NO -->
## Launch NetBox with a Multipass VM
<!-- vale Canonical.007-Headings-sentence-case = YES -->

You will launch a VM named `netbox` with Multipass, using the
[cloud init configuration](https://raw.githubusercontent.com/canonical/netbox-k8s/main/charm/cloudinit-juju-3.6.yaml)
that will install NetBox. This process will take about 20 minutes, depending on your computer and internet connection.
Run the next command to provision the VM with NetBox:
```
multipass launch  -vvvv --cloud-init https://raw.githubusercontent.com/canonical/netbox-k8s/main/charm/cloudinit-juju-3.6.yaml --timeout 1800 --name netbox --memory 4G --cpus 3 --disk 20G 22.04
```

Congratulations, at this point your NetBox instance is installed and working. You can get the Netbox URL
with the following command:
```
multipass exec netbox -- juju run traefik-k8s/0 show-proxied-endpoints --format=yaml
```

The previous command will output a URL similar to `http://<your VM ip>/netbox-netbox-k8s`. Open it with
with your favourite internet browser. However, you will not be able to do much without a user.

You can create an admin user with the next command:
```
multipass exec netbox -- juju run netbox-k8s/leader create-superuser username=admin email=netbox@example.com
```

The output of the previous command will output a password. You can now log in into the NetBox
webpage with the user `admin` and the previous password. You have now full access to NetBox!.

Once you are finished, you can delete the netbox VM with the next command:
```
multipass delete netbox --purge
```

## Troubleshooting

You can see the output log in:
```
multipass exec netbox -- tail -f /var/log/cloud-init-output.log
```

And the commands executed with:
```
multipass exec netbox -- tail -f /var/log/cloud-init.log
```
