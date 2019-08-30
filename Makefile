clear:
	rm -rf dist/
	rm -rf *.egg-info

format:
	black --target-version=py37 --skip-string-normalization --line-length=120 .
lint:
	pre-commit run -a -v

test:
	pip install -e .
	pytest

test-release: clear
	python setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: clear
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	python setup.py sdist bdist_wheel upload -r pypi

setup:
	pip install -U -r requirements-dev.txt