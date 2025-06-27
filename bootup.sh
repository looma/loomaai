#!/bin/bash

# Start the streamlit app
source /app/.venv/bin/activate
cd /app/appai
streamlit run main.py --server.port 4700 \
    --server.baseUrlPath /loomaai 2> st-llms.log

tail -f /dev/null
