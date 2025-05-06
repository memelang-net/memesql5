import sys, parse, sql, db

def dbget (memestr: str):
	return db.oselect(*sql.select(parse.decode(memestr)))

def dbadd (memestr: str):
	return db.exec(*sql.insert(parse.decode(memestr)))


if __name__ == "__main__":

	if len(sys.argv)==0: raise Exception('no args')

	elif len(sys.argv)==1 or sys.argv[1]=='q':
		print(str(dbget(sys.argv[2])).replace(';', '\n'))

	elif sys.argv[1]=='qry':
		memes = parse.decode(sys.argv[2])
		sqlstr, params = sql.select(memes)
		print('TOKENS: ', memes)
		print('SQL: ', sql.morgify(sqlstr, params))
		print('RESULTS:')
		print(str(dbget(sys.argv[2])).replace(';', '\n'))

	elif sys.argv[1]=='i':
		dbadd(sys.argv[2])
		print('status=success')