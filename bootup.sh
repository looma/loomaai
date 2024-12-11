#!/bin/bash

echo "Starting "

# Here we setup the data directories, ollama etc 
# needed for the app
if [ -f /app/setup.sh ]; then
    /app/setup.sh
fi

# Load the environment variables
source /app/appai/.env 

# Start the streamlit app
cd /app/appai
streamlit run main.py --server.port 4700 \
    --server.baseUrlPath /loomaai 2> st-llms.log

tail -f /dev/null
