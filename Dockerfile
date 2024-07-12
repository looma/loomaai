FROM python:3.12


RUN apt update && apt upgrade -y
RUN apt install -y vim bash git net-tools

RUN mkdir -p /app/data
RUN chmod 777 /app/data
WORKDIR /app


COPY bootup.sh /app/bootup.sh

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /app/appai
COPY appai/ /app/appai/

# Revise
COPY .env /app/appai/.env

#
RUN mkdir -p /root/.streamlit
COPY dotstreamlit/secrets.toml /root/.streamlit
COPY dotstreamlit/credentials.toml /root/.streamlit
COPY dotstreamlit/config.toml /root/.streamlit


# Now let's create a local models
RUN curl https://ollama.ai/install.sh | sh
COPY setup.sh /app/setup.sh 
COPY pull.sh /app/pull.sh


# loomaai specific configuration 
RUN mkdir -p /root/.config/loomaai/
COPY config.json /root/.config/loomaai/config.json

# laiapp port
EXPOSE 4700

WORKDIR /app/appai

CMD [ "/app/bootup.sh" ]

