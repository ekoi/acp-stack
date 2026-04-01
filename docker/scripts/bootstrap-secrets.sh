#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: bootstrap-secrets.sh <service_name> <conf_dir>" >&2
  exit 2
fi

service_name="$1"
conf_dir="$2"
secrets_file="$conf_dir/.secrets.toml"
example_file="$conf_dir/.secrets.toml.example"

if [ -f "$secrets_file" ]; then
  echo "[$service_name] using existing conf/.secrets.toml"
elif [ -f "$example_file" ]; then
  echo "[$service_name] creating conf/.secrets.toml from .secrets.toml.example"
  cp "$example_file" "$secrets_file"
else
  echo "[$service_name] missing conf/.secrets.toml and conf/.secrets.toml.example" >&2
  exit 1
fi

