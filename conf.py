
# Config for postgres database

DB = {
	'host': 'localhost',
	'user': 'memeuser',
	'pass': 'memepswd',
	'name': 'memedb',
	'table': 'meme'
}

TABLE_ADD = f'''
CREATE TABLE IF NOT EXISTS {DB['table']} (r TEXT, alp TEXT, amt DOUBLE PRECISION, m BIGINT);
CREATE INDEX IF NOT EXISTS {DB['table']}_m_idx ON {DB['table']} (m);
CREATE INDEX IF NOT EXISTS {DB['table']}_amt_idx ON {DB['table']} (amt) WHERE amt IS NOT NULL;
CREATE INDEX IF NOT EXISTS {DB['table']}_r_idx ON {DB['table']} USING HASH ((LOWER(r)));
CREATE INDEX IF NOT EXISTS {DB['table']}_alp_idx ON {DB['table']} USING HASH ((LOWER(alp))) WHERE alp IS NOT NULL;
'''

DB_ADD = f'''
SELECT format('CREATE DATABASE {DB["name"]}') WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{DB["name"]}');
\\gexec

DO $do$
BEGIN
	IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{DB["user"]}') THEN
		CREATE ROLE {DB["user"]} LOGIN PASSWORD '{DB["pass"]}';
	END IF;
END
$do$;

\\connect {DB['name']};

{TABLE_ADD}

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE {DB['table']} TO {DB['user']};
'''