
# Config for postgres database

DEFTBL = 'meme'

SQLTABLE = f'''
CREATE TABLE IF NOT EXISTS {DEFTBL} (rel TEXT, alp TEXT, amt DOUBLE PRECISION, bid BIGINT);
CREATE INDEX IF NOT EXISTS {DEFTBL}_bid_idx ON {DEFTBL} (bid);
CREATE INDEX IF NOT EXISTS {DEFTBL}_amt_idx ON {DEFTBL} (amt) WHERE amt IS NOT NULL;
CREATE INDEX IF NOT EXISTS {DEFTBL}_rel_idx ON {DEFTBL} USING HASH ((LOWER(rel)));
CREATE INDEX IF NOT EXISTS {DEFTBL}_alp_idx ON {DEFTBL} USING HASH ((LOWER(alp))) WHERE alp IS NOT NULL;
'''

DB = {
	'host': 'localhost',
	'user': 'memeuser',
	'pass': 'memepswd',
	'name': 'memedb',
	'table': {}
}