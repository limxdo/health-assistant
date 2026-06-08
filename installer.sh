#!/bin/bash

set -e

LIBEXEC_DIR="/usr/local/libexec/health_assistant"
PYTHON_VENV="$LIBEXEC_DIR/python-venv"
CONFIG_DIR="/etc/health_assistant"
SYSTEMD="/etc/systemd/system"

# if not root
if [ "$(id -u)" -ne 0 ]; then
    echo "this script must be run as root." >&2
    exit 1
fi

case "$1" in
    install)
        mkdir -p "$LIBEXEC_DIR"
        mkdir -p "$CONFIG_DIR"

        cp -f api-assistant/agent.py "$LIBEXEC_DIR"/
        cp -f systemd/* "$SYSTEMD"/

        # check if config file already exists to avoid loss API keys
        if [ ! -f "$CONFIG_DIR/config.json" ]; then
            cp -f api-assistant/config.json "$CONFIG_DIR"/
        else
            echo "Config file already exists, preserving your API keys"
        fi

        [ ! -d "$PYTHON_VENV" ] && python3 -m venv "$PYTHON_VENV"
        "$PYTHON_VENV"/bin/pip install -r api-assistant/requirements.txt

        systemctl daemon-reload
        for service in "$SYSTEMD"/health-*.service; do
            systemctl enable --now "$(basename $service)"
        done
        ;;

    uninstall)
        rm -rf "$LIBEXEC_DIR"
        rm -rf "$CONFIG_DIR"
        rm -rf "$PYTHON_VENV"

        for service in "$SYSTEMD"/health-*.service; do
            systemctl disable --now "$(basename $service)"
        done

        rm -rf "$SYSTEMD"/health-*
        ;;

    *)
        echo "$0 [install|uninstall]" >&2
        exit 1
esac
