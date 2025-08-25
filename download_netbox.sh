#!/bin/bash
# This script downloads and extracts the NetBox source code.
NETBOX_VERSION="4.3.6"
wget https://github.com/netbox-community/netbox/archive/refs/tags/v${NETBOX_VERSION}.tar.gz
if [ -d "netbox" ]; then
    rm -rf netbox
fi
mkdir netbox
tar -xzvf v${NETBOX_VERSION}.tar.gz --strip-components=1 -C netbox
patch -p1 <patches/settings.patch
patch -p1 <patches/requirements.patch

# Initiate Rockcraft 
cp rockcraft.yaml netbox/rockcraft.yaml
# Update the rockcraft.yaml with the correct version
sed -i "s/^version: \".*\"/version: \"${NETBOX_VERSION}\"/" netbox/rockcraft.yaml

# Set up the cron job
cp -r cron.d netbox/

cp configuration.py netbox/netbox/netbox/configuration.py

mv netbox/upgrade.sh netbox/migrate.sh