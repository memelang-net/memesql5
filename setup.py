# setup.py
from setuptools import setup, find_packages

setup(
	name="memesql",
	version="5.0.12",
	author="Bri Holt",
	author_email="info@memelang.net",
	description="A compact graph-relational query language",
	python_requires=">=3.7",
	packages=find_packages(),
)
