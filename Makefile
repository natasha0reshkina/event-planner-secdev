build:
	docker build -t event-planner:local .

run:
	docker compose up --build

scan:
	trivy image event-planner:local

lint-docker:
	hadolint Dockerfile
