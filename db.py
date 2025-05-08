from conf import *

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
