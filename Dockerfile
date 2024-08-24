FROM python:3.12-slim

RUN mkdir -p /app/data
RUN chmod 777 /app/data
WORKDIR /app

# need base updated and gcc installed because 
# some python3 packages need it
RUN apt update && apt upgrade -y
RUN apt install gcc make -y

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# remove the gcc we used for package install 
# and we do not need it in the final image
RUN apt remove gcc make -y

COPY bootup.sh /app/bootup.sh

RUN mkdir -p /app/appai
COPY appai/ /app/appai/

# Revise
COPY .env /app/appai/.env

#
RUN mkdir -p /root/.streamlit
COPY dotstreamlit/config.toml /root/.streamlit


# Now let's create a local models
#RUN curl https://ollama.ai/install.sh | sh
#COPY setup.sh /app/setup.sh
#COPY pull.sh /app/pull.sh


# loomaai specific configuration 
RUN mkdir -p /root/.config/loomaai/
COPY config.json /root/.config/loomaai/config.json

# laiapp port
EXPOSE 4700

WORKDIR /app/appai

CMD [ "/app/bootup.sh" ]

