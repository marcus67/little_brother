#! /bin/bash

echo "Create users and groups..."
for user in jennifer, seth; do
    adduser --disabled-login --gecos "${user}, ACME, 123, 123, 123" ${user}
done
