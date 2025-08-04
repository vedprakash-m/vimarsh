#!/bin/bash
# Deploy script - redirects to infrastructure deployment
set -e

echo "🚀 Vimarsh Deployment Script"
echo "Redirecting to infrastructure deployment..."

# Change to the infrastructure directory and run the deployment
cd "$(dirname "$0")/../infrastructure"
exec ./deploy.sh "$@"
