#!/bin/bash

echo "Starting "

# setting up ollama here at boot
# because we want to use the volume mounted for /app/data 
# given to the container at boot time
if [ -f /app/setup.sh ]; then
    /app/setup.sh
fi

if [ -f /usr/local/bin/ollama ]; then
    export OLLAMA_HOST="0.0.0.0"
    /usr/local/bin/ollama serve &
fi

#echo "Pull Models"
#if [ -f /app/pull.sh ]; then
#    /app/pull.sh
#fi

echo "looma ai app"
if [ -f /app/appai/main.py ]; then
    cd /app/appai
    streamlit run main.py --server.port 4700 \
        --server.baseUrlPath /loomaai 2> st-llms.log
fi

tail -f /dev/null
