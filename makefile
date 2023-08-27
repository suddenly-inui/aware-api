install:
	poetry install

setup-database:
	poetry run python aware_api/db.py

api:
	poetry run uvicorn aware_api.api.main:app --reload

