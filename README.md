# Looma AI

## User Guide

### Embed all activities
```bash
python3 -m appai.cli.embed 
```
* This process will generate embeddings for all activities in the MongoDB `activities` collection and add the vectors to the Qdrant `activities` collection.
* IMPORTANT: This process will DELETE all existing entries from qdrant and rebuild the entire vector database.

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

## Developers

When importing a common library from CLI: `from ..common.generate import generate_vectors`
* To run a script in CLI, run it like this from the root directory: `python3 -m appai.cli.generate`
  * The -m flag is important, do not use the filename
* When importing a common library from pages: `from common.query_faiss import query`
