#!/bin/bash
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# This script downloads and extracts the NetBox source code.
NETBOX_VERSION="4.3.6"
wget https://github.com/netbox-community/netbox/archive/refs/tags/v${NETBOX_VERSION}.tar.gz

# Clean up any previous download and keep the rockcraft.yaml file
find netbox -mindepth 1 ! -name 'rockcraft.yaml' -exec rm -rf {} +

tar -xzvf v${NETBOX_VERSION}.tar.gz --strip-components=1 -C netbox
patch -p1 <patches/settings.patch
patch -p1 <patches/requirements.patch

# Update the rockcraft.yaml with the correct version
sed -i "s/^version: \".*\"/version: \"${NETBOX_VERSION}\"/" netbox/rockcraft.yaml

# Set up the cron job
cp -r cron.d netbox/

cp configuration.py netbox/netbox/netbox/configuration.py

mv netbox/upgrade.sh netbox/migrate.sh
