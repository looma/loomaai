FROM python:3.12-slim

RUN mkdir -p /app/data
RUN chmod 777 /app/data
WORKDIR /app

RUN apt update && apt upgrade -y
RUN apt install -y vim bash git net-tools curl
# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY requirements.txt /app/requirements.txt
RUN uv venv --python=python3.12 /app/.venv
RUN . /app/.venv/bin/activate
RUN uv pip install --no-cache-dir -r /app/requirements.txt

COPY bootup.sh /app/bootup.sh

RUN mkdir -p /app/appai
COPY appai/ /app/appai/
RUN . /app/.venv/bin/activate && \
    python3 appai/load_models.py

# Revise
COPY .env /app/appai/.env

#
RUN mkdir -p /root/.streamlit
COPY dotstreamlit/config.toml /root/.streamlit

# laiapp port
EXPOSE 4700

WORKDIR /app

CMD [ "/app/bootup.sh" ]

