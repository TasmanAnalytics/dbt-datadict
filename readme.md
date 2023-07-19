Create the venv

`make init`

Activate the venv

`. .venv/bin/activate`

Building locally

`python setup.py develop`

Building for distribution

`python setup.py sdist bdist_wheel`

Pushing the distribution to the test server (changes require upversioning)

`twine upload --repository testpypi --skip-existing dist/*`

Pulling the distribution for use in another project

`pip install --extra-index-url https://test.pypi.org/simple/ dbt-datadictionary==<version>`