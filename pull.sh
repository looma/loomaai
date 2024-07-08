#!/bin/bash

if [ ! -d /data/aidata/ollama/models/manifests/registry.ollama.ai/library/llama3 ]; then
    ollama pull llama3:latest
fi
