
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


GLOBAL_POOL = None

def ppool():
	# lazily call psycopg2 in case developer wants to use their own DB driver
	from psycopg2.pool import ThreadedConnectionPool
	from psycopg2.extras import RealDictCursor

	global GLOBAL_POOL
	if GLOBAL_POOL is None:
		GLOBAL_POOL = ThreadedConnectionPool(
			minconn=1,
			maxconn=5,
			host=DB['host'],
			database=DB['name'],
			user=DB['user'],
			password=DB['pass']
		)
	return GLOBAL_POOL

def pselect(sql: str, params: list = None) -> list:
	if params is None: params = []
	pool = ppool()
	conn = pool.getconn()
	try:
		with conn.cursor() as cursor:
			cursor.execute(sql, params)
			row = cursor.fetchone()
			return row[0] if row else None
	finally:
		conn.rollback()
		pool.putconn(conn)

def pexec(sql: str, params: list = None):
	if params is None: params = []
	pool = ppool()
	conn = pool.getconn()
	try:
		with conn.cursor() as cursor:
			cursor.execute(sql, params)
			conn.commit()
	except Exception as e:
		conn.rollback()
		raise e
	finally:
		pool.putconn(conn)
