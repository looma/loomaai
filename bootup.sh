#!/bin/bash

echo "Starting "

# setting up ollama here at boot
# because we want to use the volume mounted for /app/data 
# given to the container at boot time
if [ -f /app/setup.sh ]; then
    /app/setup.sh
fi

cd /app/appai
streamlit run main.py --server.port 4700 \
    --server.baseUrlPath /loomaai 2> st-llms.log

tail -f /dev/null
