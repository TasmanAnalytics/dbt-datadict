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