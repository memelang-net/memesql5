# Memelang.net | (c) HOLTWORK LLC | Patents Pending

import random, json
from parse import *

MEMEBASE = {}

# Store memes as in-memory DB
def add(memekey:str, memes: list[list[list]]):

	if memekey not in MEMEBASE: MEMEBASE[memekey]=[]
	mvrand = None

	for meme in memes:
		# TO DO: Handle joined memes with multiple m= here
		mv = None
		for ro, rv, ao, av in meme:
			if rv == 'm' and memopr[ro][SEQL] == '=':
				if mv is not None: raise ValueError('dup m')
				mv = av

		if mv is None:
			if not mvrand: mvrand = 2**20 + random.getrandbits(62)
			else: mvrand += 1
			mv = mvrand
			
		for ro, rv, ao, av in meme:
			if rv is None: raise ValueError(f'Bad rv, cannot be empty')
			elif av is None: raise ValueError(f'Bad av for {rv}')
			elif ro is None: raise ValueError(f'Bad ro for {rv}')
			elif ao is None: raise ValueError(f'Bad ao for {rv}')
			elif rv == 'm': continue

			row = {'m':mv, 'r':rv, 'alp':None, 'amt':None}
			row[acolid('=', av)]=av
			MEMEBASE[memekey].append(row)


# Compare two values
def cmpr(c:str, e:str, v1, v2) -> bool:
	if v1 is None or e is None: return True
	elif v2 is None: raise Exception(f'cmpr none {c} {v1}{e}{v2}')
	elif c in ('r', 'alp'):
		if e == '=': return (str(v1).lower() == str(v2).lower())
		elif e == '!=': return (str(v1).lower() != str(v2).lower())
		else: raise Exception(f'cmpr str opr {c} {v1}{e}{v2}')
	elif not isinstance(v1, (int, float)) or not isinstance(v2, (int, float)): raise Exception(f'cmpr int {c} {v1}{e}{v2}')
	else:
		if   e == '=':  return (v2 == v1)
		elif e == '!=': return (v2 != v1)
		elif e == '>':  return (v2 > v1)
		elif e == '>=': return (v2 >= v1)
		elif e == '<':  return (v2 < v1)
		elif e == '<=': return (v2 <= v1)
		else: raise Exception(f'cmpr opr {c} {v1}{e}{v2}')


# Choose a is 'alp' for str or 'amt' for numeric
def acolid(ao:str, av):
	if isinstance(av, (int, float)) or ao in ('>','<','>=','<='): return 'amt'
	return 'alp'


# Evaluate ONE query-pattern meme against rows (full join logic)
def get(memekey: str, pattern: list[list[list]]) -> list[list[list]]:
	results = []

	if memekey not in MEMEBASE: raise ValueError('get memekey')

	def dfs(idx, chosen, vcols, mv):
		if idx == len(pattern):
			results.append(list(chosen))
			return

		ro, rv, ao, av = pattern[idx]

		acol = acolid(ao, av)
		rv = str(rv).lower()
		me = '='

		if isinstance(rv, str) and RE_VAR.match(rv[:1]):
			me='!=' # join on different m
			if rv in vcols: rv = vcols.get(rv)
			else: raise Exception(f'Bad rv {rv}')

		if isinstance(av, str) and RE_VAR.match(av[:1]):
			me='!=' # join on different m
			if av in vcols: av = vcols.get(av)
			else: raise Exception(f'Bad av {av}')

		for row in MEMEBASE[memekey]:
			if not cmpr('m', me, mv, row['m']): continue
			if not cmpr('r', memopr[ro][SEQL], rv, row['r']): continue
			if not cmpr(acol, memopr[ao][SEQL], av, row[acol]): continue

			# new var values
			vcols2 = vcols.copy()
			vcols2[AS] = row[acol]
			vcols2[RS] = row['r']
			vcols2[MS] = row['m']
			vcols2[AS+str(row['r']).lower()] = row[acol]

			if me == '!=': chosen.append([SPC, 'm', '=', row['m']])

			# Recurse
			chosen.append(row)
			dfs(idx + 1, chosen, vcols2, row['m'])
			chosen.pop()

	dfs(0, [], {}, None)

	# Convert satisfying row tuples back into meme structures
	output = []
	for combo in results:
		meme_out = [[SPC, 'm', '=', combo[0]['m']]]
		for (ro, _, ao, _), row in zip(pattern, combo):
			val = row['alp'] if row['alp'] is not None else row['amt']
			meme_out.append([ro, row['r'], ao, val])
		output.append(meme_out)

	return output