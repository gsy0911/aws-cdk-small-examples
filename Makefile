

.PHONY: help
help:
	@printf "\033[36m%-30s\033[0m %-50s %s\n" "[Sub command]" "[Description]" "[Example]"
	@grep -E '^[/a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | perl -pe 's%^([/a-zA-Z_-]+):.*?(##)%$$1 $$2%' | awk -F " *?## *?" '{printf "\033[36m%-30s\033[0m %-50s %s\n", $$1, $$2, $$3}'


.PHONY: ls
ls: ## execute `cdk ls` in all directories ## make ls
	$(eval target_dirs = $(shell ls python))
	@for dir in $(target_dirs); do \
		echo python/$$dir; \
		cd python/$$dir && cdk ls; \
		echo ""; \
		cd -; \
	done
