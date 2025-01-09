# Looma AI

## Setup

1. The Docker containers "loomaweb" and "loomadb" must be running when using "loomaai". Clone [Looma-II](https://github.com/looma/Looma-II) and follow the setup instructions in README for Looma-II repository
2. Ensure the Looma-II docker-compose is running
3. Clone this repo to your computer `git clone https://github.com/looma/loomaai`
4. (If you plan to use ChatGPT-enabled features) Obtain an OpenAI API key and add it to both `config.json` and `config-external.json` in the root directory
   `"openai_api_key" : "sk-<your key>"`

5. Run `make` (build the streamlit image) - this could take a few minutes 
6. Run `docker-compose up -d` - (start qdrant and streamlit containers)
7. Navigate to [http://localhost:47000/loomaai](http://localhost:47000/loomaai) to access the dashboard
8. Create the `data/files/textbooks` folder within this folder, if it does not already exist

## Setup for Developers
**YOU MUST USE PYTHON 3.12, NOT PYTHON 3.13**.
This is because pytorch does not support python3.13

#### 1.create a python virtual environment

```bash
	python3.12 -m venv env
	source env/bin/activate
```

#### 2. install required python libraries

```bash
	pip3 install -r requirements.txt
```

## User Guide

#### Chapter Splitting

* In Streamlit
  * In Streamlit, click `Textbook` in the sidebar and select the textbooks you want.
  * Click the "Split Into Chapters" button. 
  * A file location will be shown on-screen. That location is synced to the host machine, so the chapters will also be in `data/files/chapters` within this folder.

#### Chapter Summaries

* In Streamlit
  * Navigate to "Chapter" in the sidebar
  * Select the chapter to be summarized from your file explorer.
  * Make sure the language selected in the options is the language the chapter is in.
  * Click the Summarize button.

#### Embed All Activities

This requires  docker-compose to be running (see "Setup")

```bash
python3 -m appai.cli.embed
```
* This process will generate embeddings for all activities in the MongoDB `activities` collection and add the vectors to the Qdrant `activities` collection.
* IMPORTANT: This process will DELETE all existing entries from qdrant and rebuild the entire vector database.
* The [Looma-II](https://github.com/looma/Looma-II) semantic search feature requires these embeddings to be generated first and the docker-compose to be running

```bash
python3 -m appai.cli.embed --missing-only
```
* The `-missing-only` flag will prevent the program from deleting existing entries. It will check each entry in mongodb and only create embeddings for the ones that are not in qdrant. 
* You have to run the first version without the flag at least once to initialize the qdrant collection (or create the collection some other way, for example through the qdrant dashboard http://localhost:46333/dashboard. 


#### Populate Chapters with Related Resources

* Follow the steps in "Run Containers" and "Embed All Activities" first

```bash
python3 -m appai.cli.populate_mongo
```
* This process will populate the "related resources" for every chapter in [Looma-II](https://github.com/looma/Looma-II)
* This process is additive and will not overwrite any existing related resources in MongoDB, it will also not add duplicate relations


## More Developer Notes

When importing a `common` library from `cli`, use a relative import: `from ..common.generate import generate_vectors`
* To run a script in CLI, run it like this from the root directory: `python3 -m appai.cli.generate`
  * The -m flag is important, do not use the filename
* When importing a common library from pages: `from common.query_faiss import query`

### To get a terminal session in the container
```bash
% make shell
% docker exec -ti looma-streamlit /bin/bash
```
Now you are in the terminal in the container

If you'd like to see the logs of the running container
```bash
% make logs
```
