AWS_ACCOUNT_NUMBER := 000000000000
ECR_REPOSITORY_NAME := gsy0911/sample
REGION := ap-northeast-1

.PHONY: help
help:
	@echo " == push docker image to ECR == "
	@echo ""
	@printf "\033[36m%-30s\033[0m %-50s %s\n" "[Sub command]" "[Description]" "[Example]"
	@grep -E '^[/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | perl -pe 's%^([/a-zA-Z_-]+):.*?(##)%$$1 $$2%' | awk -F " *?## *?" '{printf "\033[36m%-30s\033[0m %-50s %s\n", $$1, $$2, $$3}'

.PHONY: login
login: ## login to ECR ## make login
	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(REGION).amazonaws.com

.PHONY: build
build: ## build docker ## make build
	docker build -t $(ECR_REPOSITORY_NAME) .

.PHONY: start
start: ## run local docker image ## make start
	docker run -itd $(ECR_REPOSITORY_NAME) /bin/bash

.PHONY: tag
tag: build ## add tag to ECR ## make tag
	docker tag $(ECR_REPOSITORY_NAME):latest $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(REGION).amazonaws.com/$(ECR_REPOSITORY_NAME):latest

.PHONY: push
push: tag ## push image to ECR ## make push
	docker push $(AWS_ACCOUNT_NUMBER).dkr.ecr.$(REGION).amazonaws.com/$(ECR_REPOSITORY_NAME):latest
