#!/bin/bash

# Update the package list
sudo apt-get update

# Install necessary packages
sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 pulseaudio-utils

# Install pip if not already installed
sudo apt-get install -y python3-pip

# Upgrade pip to the latest version
pip3 install --upgrade --user pip

# Install Python packages
pip3 install --user PyGObject

# Ensure the script is executable
chmod +x "$0"

echo "All dependencies have been installed."