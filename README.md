# Looma AI

## Setup

1. The Docker containers "loomaweb" and "loomadb" must be running when using "loomaai". Clone [Looma-II](https://github.com/looma/Looma-II) and follow the setup instructions in README for Looma-II repository
2. Ensure the Looma-II docker-compose is running
3. Clone this repo to your computer `git clone https://github.com/looma/loomaai`
4. Obtain an OpenAI API key and add it to a new file in this directory called `.env` with the following contents:
```shell
export OPENAI_API_KEY=[your-api-key-here]
```

5. Run `make` (build the streamlit image) - this could take a few minutes 
6. Run `make run` - (start qdrant and streamlit containers)
7. Navigate to [http://localhost:47000/loomaai](http://localhost:47000/loomaai) to access the dashboard
8. Create the `data/files/textbooks` folder within this folder, if it does not already exist


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

## Developer Guide

### **YOU MUST USE PYTHON 3.12, NOT PYTHON 3.13**.
This is because pytorch does not support python3.13

Set up your virtual environment:
```bash
	python3.12 -m venv env
	source env/bin/activate
```

#### 2. install required python libraries

```bash
	pip3 install -r requirements.txt
```

### Features:

#### Embed All Activities

This requires  docker-compose to be running (see "Setup")

```bash
make embed-all
```
* This process will generate embeddings for all activities in the MongoDB `activities` collection and add the vectors to the Qdrant `activities` collection.
* IMPORTANT: This process will DELETE all existing entries from qdrant and rebuild the entire vector database.
* The [Looma-II](https://github.com/looma/Looma-II) semantic search feature requires these embeddings to be generated first and the docker-compose to be running

```bash
make embed-missing
```
* This will prevent the program from deleting existing entries. It will check each entry in mongodb and only create embeddings for the activities that are not in qdrant.
* Before running this, you have to first run `make embed-all` without the flag at least once to initialize the qdrant collection (or create the collection some other way, for example through the qdrant dashboard http://localhost:46333/dashboard) .


#### Populate Chapters with Related Resources

* Follow the steps in "Run Containers" and "Embed All Activities" first

```bash
make populate-mongo
```
* This process will populate the "related resources" for every chapter in [Looma-II](https://github.com/looma/Looma-II)
* This process is additive and will not overwrite any existing related resources in MongoDB, it will also not add duplicate relations

#### Translate Lessons
* Requires an OpenAI key (see step 4 of Setup)

```bash
make translate-lessons
```

This process will update all lessons in MongoDB with a new field `data_np` containing translated lesson data. It will overwrite the existing `data_np` field if present.


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
