#!/bin/bash
echo "Restoring Atlas backup data..."
mongorestore --drop /docker-entrypoint-initdb.d/atlas_backup