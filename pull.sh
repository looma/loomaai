#!/bin/bash

if [ ! -d /app/data/models/ollama/models/manifests/registry.ollama.ai/library/llama3 ]; then
    ollama pull llama3:latest
fi
