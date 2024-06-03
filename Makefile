.PHONY: release

release:
	poetry version patch && git add pyproject.toml && git commit -m "v$$(poetry version -s)" && git tag "v$$(poetry version -s)"
