# run the unittests with branch coverage
python -m poetry run python -m pytest --cov=./expressive --cov-report=xml --cov-report=term-missing tests/