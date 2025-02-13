#!/bin/bash
echo "Restoring static data..."
mongorestore --drop /docker-entrypoint-initdb.d/static_data