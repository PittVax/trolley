.PHONY: up down stop prune ps shell jython trolley

ifneq (,$(findstring WINDOWS,$(PATH)))
	SHELL := C:/Windows/System32/cmd.exe
endif

default: up

up:
	@echo "All aboard! Trolley is leaving the station..."
	docker-compose pull --parallel
#	docker-compose up -d --remove-orphans
	./utils/trolley_aliases.sh

down: stop

stop:
	@echo "Trolley is entering the station. Mind the gap..."
	@docker-compose stop

prune:
	@echo "Removing Trolley..."
	@docker-compose down -v

ps:
	@docker ps -a --filter name='Trolley*'

shell:
	docker-compose run --rm trolley

jython:
	docker-compose run --rm trolley jython

trolley:
	docker-compose run --rm trolley jython taoi/trolley.py $(filter-out $@,$(MAKECMDGOALS))
%:
	@: