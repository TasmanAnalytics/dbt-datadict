from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'dbt-datadict',
    version = '0.0.1',
    author = 'Tom Shelley',
    author_email = 'tom@tasman.ai',
    license = 'GNU GENERAL PUBLIC LICENSE',
    description = 'A Python application for automating the application of consistent field definitions to large multi-layered dbt projects',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/TasmanAnalytics/dbt-datadictionary',
    py_modules = ['dbt-datadict', 'app'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 3 - Alpha",  
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        datadict=datadict:cli
    '''
)