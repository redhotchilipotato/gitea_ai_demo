#!/bin/bash
# Hook script to set up network connectivity for Action containers
# This script runs inside each Action container to ensure Gitea connectivity

# Get the Gitea container IP address
GITEA_IP=$(getent hosts gitea | awk '{ print $1 }' | head -n 1)

if [ -n "$GITEA_IP" ]; then
    echo "Adding Gitea host entry: $GITEA_IP gitea"
    echo "$GITEA_IP gitea" >> /etc/hosts
else
    # Fallback: try to resolve from Docker network
    GITEA_IP=$(nslookup gitea | grep -A 1 "Name:" | grep "Address:" | awk '{print $2}' | head -n 1)
    if [ -n "$GITEA_IP" ]; then
        echo "Adding Gitea host entry (fallback): $GITEA_IP gitea"
        echo "$GITEA_IP gitea" >> /etc/hosts
    else
        echo "Warning: Could not resolve Gitea IP address"
    fi
fi

# Set up git configuration to use the internal Gitea instance
git config --global url."http://gitea:3000/".insteadOf "https://github.com/" || true