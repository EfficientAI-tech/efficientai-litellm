#!/bin/sh
# exit when any command fails
set -e

echo "Running prisma migrate"
prisma migrate deploy
