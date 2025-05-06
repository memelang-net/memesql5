# memesql5

This is prototype Python/Postgres implementation of [Memelang v4](https://memelang.net/04/). This Python script receives Memelang queries, converts them to SQL, executes them on a Postgres database, then returns results as a Memelang string.

## Files

| File | Purpose |
|------|---------------------------------------------------------------------|
| **app.py** | Command-line interfaces |
| **conf.py** | Postgres database configuration |
| **db.py** | Postgres database helper functions |
| **parse.py** | Encode / decode Memelang strings into meme-token lists |
| **readme.md** | Project overview (this file) |
| **setup.py** | Python package settings |
| **sql.py** | Encode a meme-token list into an SQL query |

## Installation

Installation on Ubuntu:

	# Install packages
	sudo apt install -y git postgresql python3 python3-psycopg2
	sudo systemctl start postgresql
	sudo systemctl enable postgresql
	
	# Download files
	git clone https://github.com/memelang-net/memesql5.git memesql
	cd memesql

## Database table

	CREATE TABLE IF NOT EXISTS meme (rel TEXT, alp TEXT, amt NUMERIC(18, 6), bid BIGINT);
	CREATE INDEX IF NOT EXISTS meme_rel_idx ON meme ((LOWER(rel)));
	CREATE INDEX IF NOT EXISTS meme_alp_idx ON meme ((LOWER(alp))) WHERE alp IS NOT NULL;
	CREATE INDEX IF NOT EXISTS meme_amt_idx ON meme (amt) WHERE amt IS NOT NULL;
	CREATE INDEX IF NOT EXISTS meme_bid_idx ON meme (bid);
	ALTER TABLE meme ADD CONSTRAINT alp_xor_amt CHECK ((alp IS NOT NULL) <> (amt IS NOT NULL));

## Example CLI Usage

Execute a query:

	python3 ./app.py q "student=JohnAdams ="


## Legal

Copyright 2025 HOLTWORK LLC. Patents Pending.