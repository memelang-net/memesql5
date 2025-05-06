import os
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from conf import *

GLOBAL_POOL = None

def poolinit():
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


def select(sql: str, params: list = None) -> list:
	if params is None: params = []
	pool = poolinit()
	conn = pool.getconn()
	try:
		with conn.cursor() as cursor:
			cursor.execute(sql, params)
			rows = cursor.fetchall()
		return [list(row) for row in rows]
	finally:
		conn.rollback()
		pool.putconn(conn)


def selectin(cols: dict = {}, table: str = None) -> list:
	if not table: raise ValueError("No table provided.")

	conds, params = [], []
	for col in cols:
		conds.append(f"{col} IN (" + ','.join(['%s'] * len(cols[col])) + ")")
		params.extend(cols[col])

	if not conds:
		return []

	pool = poolinit()
	conn = pool.getconn()
	try:
		with conn.cursor() as cursor:
			cursor.execute(f"SELECT DISTINCT * FROM {table} WHERE " + ' AND '.join(conds), params)
			rows = cursor.fetchall()
		return [list(row) for row in rows]
	finally:
		pool.putconn(conn)

def oselect(sql: str, params: list = None) -> list:
	if params is None: params = []
	pool = poolinit()
	conn = pool.getconn()
	try:
		with conn.cursor() as cursor:
			cursor.execute(sql, params)
			row = cursor.fetchone()
			return row[0] if row else None
	finally:
		conn.rollback()
		pool.putconn(conn)

def cselect(sql: str, params: list = None) -> list:
	if params is None: params = []
	pool = poolinit()
	conn = pool.getconn()
	try:
		with conn.cursor(cursor_factory=RealDictCursor) as cursor:
			cursor.execute(sql, params)
			return cursor.fetchall()
	finally:
		conn.rollback()
		pool.putconn(conn)

def coselect(sql: str, params: list = None) -> list:
	if params is None: params = []
	pool = poolinit()
	conn = pool.getconn()
	try:
		with conn.cursor(cursor_factory=RealDictCursor) as cursor:
			cursor.execute(sql, params)
			return cursor.fetchone() or {}
	finally:
		conn.rollback()
		pool.putconn(conn)


def exec(sql: str, params: list = None):
	if params is None: params = []
	pool = poolinit()
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


def cexec (table: str, row: dict, cols: tuple = ()):
	if not cols: cols = row.keys()
	return exec(f'INSERT INTO "{table}" ({','.join(cols)}) VALUES ({','.join(['%s'] * len(cols))})', [row[c] for c in cols])


def seqinc(seqn: str = None) -> int:
	if not seqn: raise ValueError("No sequence name provided.")
	pool = poolinit()
	conn = pool.getconn()
	try:
		with conn.cursor() as cursor:
			cursor.execute(f"SELECT nextval('{seqn}')")
			inc = int(cursor.fetchone()[0])
			conn.commit()
		return inc
	except Exception as e:
		conn.rollback()
		raise e
	finally:
		pool.putconn(conn)


def psql(sql: str, db: str = None):
	if not db: db = DB['name']
	command = f"sudo -u postgres psql -d {db} -c \"{sql}\""
	print(command)
	os.system(command)

