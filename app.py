#!/usr/bin/env python3
import sys, parse

def dbget (memestr: str):
	import db
	return db.select(*parse.select(parse.decode(memestr)))

def dbadd (memestr: str):
	import db
	return db.exec(*parse.insert(parse.decode(memestr)))


if __name__ == "__main__":

	if len(sys.argv)==0: raise Exception('no args')

	elif len(sys.argv)==1 or sys.argv[1]=='q':
		print(str(dbget(sys.argv[2])).replace(';', '\n'))

	elif sys.argv[1]=='qry':
		memes = parse.decode(sys.argv[2])
		sqlstr, params = parse.select(memes)
		print('TOKENS: ', memes)
		print('SQL: ', parse.morgify(sqlstr, params))
		print('RESULTS:')
		print(str(dbget(sys.argv[2])).replace(';', '\n'))

	elif sys.argv[1]=='i':
		dbadd(sys.argv[2])
		print('status=success')

	elif sys.argv[1]=='install':
		from db import DB_ADD
		print(DB_ADD)

	elif sys.argv[1]=='test':
		known = 'actor="Mark Hamill" role="Luke Skywalker" movie="Star Wars"; actor="Harrison Ford" role="Han Solo" movie="Star Wars"; actor="Carrie Fisher" role="Princess Leia" movie="Star Wars"; actor="Alec Guinness" role="Obi-Wan Kenobi" movie="Star Wars"; actor="Peter Cushing" role="Grand Moff Tarkin" movie="Star Wars";'
		query = 'actor="Mark Hamill" movie[movie actor='

		memes = parse.decode(known)
		print('Known Tokens:', memes)
		print()

		print('Known String:', parse.encode(memes))
		print()

		from parse import MEMEBASE
		parse.add('movies', memes)
		print('Known Base:  ', MEMEBASE['movies'])
		print()

		print('Query Results:')
		print(parse.encode(parse.qry('movies', parse.decode(query))).replace(';',";\n"))
		print()
		print()