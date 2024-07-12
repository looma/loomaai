#!/bin/bash

# setup ollama locations to store models
echo "Setup ollama"
if [ -d ~/.ollama ]; then
    rm -rf ~/.ollama
fi

if [ ! -d /app/data/ollama ]; then
    mkdir -p /app/data/models/ollama
fi

if [ ! -L ~/.ollama ]; then
    ln -s /app/data/models/ollama ~/.ollama
fi

# setup location for file uploads 
if [ ! -d /app/data/files ]; then
    mkdir -p /app/data/files
fi
