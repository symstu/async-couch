import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async-couch",
    version="0.1a6",
    author="Maksym Stukalo",
    author_email="stukalo.maksym@gmail.com",
    description="Asynchronous client for CouchDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symstu/async-couchdb",
    packages=['async_couch'],
    package_data={'async_couch': [
        'clients/*',
        'clients/*/*',
        'http_clients/*',
        'utils/*'
    ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
