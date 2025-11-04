#!/bin/bash

curl -X POST http://localhost:8080/process \
    -H "Content-Type: application/json" \
    -d '{"client_id":"client_A"}'
