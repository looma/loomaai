DOCKER=docker

LAIC_IMAGE=loomaai
LAIC_VERSION=latest
LAIC_CTR=loomaai

LOOMA_HOME=$(shell pwd)
DATAVOL=$(LOOMA_HOME)/data/files
SRCDIR=$(LOOMA_HOME)

all: $(LAIC_IMAGE)

.PHONY: all

$(LAIC_IMAGE):
	$(DOCKER) build -t $(LAIC_IMAGE) -f Dockerfile .

run: $(DATAVOL)
	$(DOCKER) run -tid -p 4700:4700 \
		-v $(DATAVOL):/app/data/files \
		-v ./appai:/app/appai --name $(LAIC_CTR) $(LAIC_IMAGE)
$(DATAVOL):
	mkdir -p $(DATAVOL)
	mkdir -p $(DATAVOL)/models

stop:
	$(DOCKER) stop $(LAIC_CTR)
	$(DOCKER) rm $(LAIC_CTR)

shell:
	$(DOCKER) exec -ti $(LAIC_CTR) /bin/bash

logs:
	$(DOCKER) logs $(LAIC_CTR) -f

rmi:
	$(DOCKER) rmi $(LAIC_IMAGE):$(LAIC_VERSION)

clean:
	rm -rf $(DATAVOL)

# TODO: this needs to chenge for dockerhub
publish:
	@docker tag $(LAIC_IMAGE):$(LAIC_VERSION) ghcr.io/looma/$(LAIC_IMAGE):$(LAIC_VERSION)
	@docker push ghcr.io/looma/$(LAIC_IMAGE):$(LAIC_VERSION)

