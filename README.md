# Looma AI




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

