# memesql5

This is prototype Python-Postgres implementation of [Memelang v5](memelang.md). This Python script receives Memelang queries, converts them to SQL, executes them on a Postgres database, then returns results as a Memelang string. Contact [info@memelang.net](mailto:info@memelang.net).

| File | Purpose |
|------|---------------------------------------------------------------------|
| **app.py** | Command-line interfaces |
| **db.py** | Postgres database config and functions |
| **memelang.md** | Spec explaining the Memelang format |
| **parse.py** | Encode / decode Memelang strings |
| **readme.md** | Project overview (this file) |
| **setup.py** | Python package settings |

## Installation

Installation on Ubuntu:

	# Install packages
	sudo apt install -y git postgresql python3 python3-psycopg2
	sudo systemctl start postgresql
	sudo systemctl enable postgresql
	
	# Download files
	git clone https://github.com/memelang-net/memesql5.git memesql
	cd memesql

	# Edit db.py as you like

	# Create database
	sudo -u postgres bash -c 'python3 ./app.py install | psql'

## Example Python Usage

	import memesql

	# Convert a Memelang string to a meme token list
	memes = memesql.decode('student=JohnAdams =')

	# Convert a meme token list to an SQL query
	sqlstr, params = memesql.select(memes)

	# Return result Memelang string from database for a Memelang query
	result_meme_str = memesql.dbget('student=JohnAdams =')

## Example CLI Usage

	python3 ./app.py q 'student=JohnAdams ='

	# OUTPUT:
	m=1234 student="JohnAdams" college="Harvard"

## Legal

Copyright 2025 HOLTWORK LLC. Patents Pending.