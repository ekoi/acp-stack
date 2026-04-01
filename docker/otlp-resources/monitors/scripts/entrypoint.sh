#!/bin/sh

# Create the aca.log file if it doesn't exist
if [ ! -f /home/akmi/aca/logs/aca.log ]; then
  touch /home/akmi/aca/logs/aca.log
  echo "Created aca.log file."
else
  echo "aca.log file already exists."
fi

# Execute the original command
exec "$@"