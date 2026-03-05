servicesUp:
	docker-compose -f infra/compose.yaml up -d

servicesDown:
	docker-compose -f infra/compose.yaml down