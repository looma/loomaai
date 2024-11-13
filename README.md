# Looma AI

## User Guide

### Setup
1. Create and/or activate your python [virtual environment](https://docs.python.org/3/library/venv.html)
   (On mac/linux run `source <venv>/bin/activate`)

```
pip3 install -r requirements.txt
```

### Run Containers (Required 1st step)
This will run a docker-compose with Streamlit and Qdrant. Streamlit is a web interface for testing Looma AI features. Qdrant is a vector database for storing and querying embeddings.
```bash
make
docker-compose up
```

Streamlit: [http://localhost:47000/loomaai](http://localhost:47000/loomaai)
Qdrant web UI: [http://localhost:46333/dashboard](http://localhost:46333/dashboard)

### Embed All Activities
This requires the docker-compose to be running (see "Run Containers")
```bash
python3 -m appai.cli.embed 
```
* This process will generate embeddings for all activities in the MongoDB `activities` collection and add the vectors to the Qdrant `activities` collection.
* IMPORTANT: This process will DELETE all existing entries from qdrant and rebuild the entire vector database.
* The [Looma-II](https://github.com/looma/Looma-II) semantic search feature requires these embeddings to be generated first and the docker-compose to be running

### Populate "Related Resources"
* Follow the steps in "Run Containers" and "Embed All Activities" first

```bash
python3 -m appai.cli.populate_mongo
```
* This process will populate the "related resources" for every chapter in [Looma-II](https://github.com/looma/Looma-II)
* This process is additive and will not overwrite any existing related resources in MongoDB, it will also not add duplicate relations


## Developers

### To install and run the LoomaAI container (in Terminal):

```bash
% cd loomaai/
% git pull
% git branch -a
```
The defailt branch is `main` but we can pick other branches used during development. 
Now let's pick a branch in the list and checkout the branch. In the example below we are
using a branch called `na_ctr`. 

```bash
% git checkout na_ctr
% ls
Dockerfile  Makefile    README.md
appai       bootup.sh   config.json     dotstreamlit
npttf2utf   pull.sh     requirements.txt
setup.sh

```

### To build & run the container
```bash
% make
% make run
```
Now the container is running

### To view it in your browser at localhost:4700

Point the browser to [http://localhost:4700](http://localhost:4700)

### To get a terminal session in the container
```bash
% make shell
% docker exec -ti loomaai /bin/bash
```
Now you are in the terminal in the container

If you'd like to see the logs of the running container 
```bash
% make logs
```

When importing a common library from CLI: `from ..common.generate import generate_vectors`
* To run a script in CLI, run it like this from the root directory: `python3 -m appai.cli.generate`
  * The -m flag is important, do not use the filename
* When importing a common library from pages: `from common.query_faiss import query`

### Chapter Splitting
* In CLI
  * Make sure you are in the root directory  
  * Use the follow command in the terminal: 
    `python3 -m appai.cli.split data/files/chapters (prefix of what textbook to split, such as 5M, or 'all' for splitting all the textbooks into chapters)`
* In Streamlit
  * Create the data/files/chapters folder in the loomaai repo if it is not already there.
  * In the textbox of the streamlit app, type in the prefix of what textbook to split, such as 5M, or 'all' for splitting all textbooks into chapters. 
  * Click the "Split Chapters" button
The chapters should be in the "data/files/chapters" folder in the loomaai repo