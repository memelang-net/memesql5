# memesql4.1

This is prototype Python/Postgres implementation of [Memelang 4.1](memelang.md). This Python script receives Memelang queries, converts them to SQL, executes them on a Postgres database, then returns results as a Memelang string.

| File | Purpose |
|------|---------------------------------------------------------------------|
| **app.py** | Command-line interfaces |
| **conf.py** | Postgres database configuration |
| **db.py** | Postgres database helper functions |
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
	git clone https://github.com/memelang-net/memesql4.1.git memesql
	cd memesql

	# Edit conf.py as you like

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
	b=1234 student="JohnAdams" college="Harvard"

## Legal

Copyright 2025 HOLTWORK LLC. Patents Pending.