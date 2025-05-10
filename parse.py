# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# Encode and decode Memelang string to list
# pair = [r operator, r value, a operator, a value]
# meme = pair list = [pair, ...]
# memes = meme list = pair list list = [[pair, ...], ...]

import re, json

MEMEBASE = {}
M_MIN = 1 << 20
M_MAX = 1 << 62
M_VAL = None

SCOL, SEQL, SOUT = 0, 1, 2 			# name for each slot in OPR[opr] list
BID, RID, AID = 'm', 'r', 'a'		# name for each column in OPR[opr][SCOL]
END, SPC, NOT = ';', ' ', '!'		# Special characters
AS, RS, MS = '@', '~', '#'			# Var symbols

OPR = { # operator characters and their settings
	None	: (None,	None,	None),
	END		: (None,	None,	END),
	SPC		: (RID,		'=',	SPC),
	NOT		: (RID,		'!=',	SPC+NOT),
	'='		: (AID,		'=',	'='),
	'!='	: (AID,		'!=',	'!='),
	'>'		: (AID,		'>',	'>'),
	'<'		: (AID,		'<',	'<'),
	'>='	: (AID,		'>=',	'>='),
	'<='	: (AID,		'<=',	'<='),
}

OPRSTR = {'=', '!='}
OPRNUM = {'>', '<', '>=', '<='}
COLSTR = {'r', 'alp'}
COLNUM = {'m', 'amt'}

RE_DIV = re.compile(r'([\s;]+)') # Dividers between pairs
RE_QOT = re.compile(r'("(?:(?:\\.)|[^"\\])*")') # String between quotes
RE_NUM = re.compile(r'^[+-]?\d+(?:\.\d+)?$') # Matches non-numeric chars, must be string
RE_ALP = re.compile(r'[^a-zA-Z0-9_\$\#\~\@]') # Complex string must be wrapped in quotes
RE_VAR = re.compile(r'[\@\~\#\$]') # Variable symbols
RE_PAR = re.compile(r"(!)?([a-zA-Z0-9_\$\#\~\@]*)(>=|<=|!=|=|>|<)?([a-zA-Z0-9_\$\#\~\@\.\-\+]*)") # !R>=A

# Input: Memelang string as 'R=A R>A ="x y"; <=A !R=A'
# Output: memes
def decode(memestr: str) -> list[list[list]]:

	# Remove comments, newlines, and empty quotes
	memestr = re.sub(r'\s*//.*$|""|\n', '', memestr, flags=re.MULTILINE).strip()

	if len(memestr) == 0: raise Exception('Empty memestr')

	memes, meme = [], []

	# Split by quotes, skip inside the quotes, parse outside of the quotes
	parts = RE_QOT.split(memestr)
	if len(parts) % 2 == 0: raise ValueError('Unclosed quote')

	for p, part in enumerate(parts):

		# Assign string inside quotes straight to ="value"
		if p % 2 == 1:
			if not meme: raise ValueError('Start quote')
			elif meme[-1][2] not in OPRSTR: raise ValueError(f'Bad quote ao: {meme[-1][2]}""')
			meme[-1][3]=json.loads(part)
			continue

		# Desugar shorthand
		part = re.sub(r'([a-zA-Z0-9_\$\#\~\@]*):([a-zA-Z0-9_\$\#\~\@]*)', r'\1= m!=# \2=@', part)

		# Parse string outside quotes into R=A
		for subpart in RE_DIV.split(part):
			# space
			if subpart == '' or re.fullmatch(RE_DIV, subpart):
				if END in subpart:
					if meme: memes.append(meme)
					meme=[]
				continue

			# R=A
			m=re.fullmatch(RE_PAR, subpart)
			if not m: raise ValueError(f'Bad form: {subpart}')
			ro, rv, ao, av = m.group(1), m.group(2), m.group(3), m.group(4)

			# Check operators
			if ro in (None,''): ro=SPC
			elif ro not in OPR: raise ValueError(f"Bad ro: {ro}")

			if ao in (None,''): ao=None
			elif ao not in OPR: raise ValueError(f"Bad ao: {ao}")

			# Check values
			if rv == '': rv = None
			else:
				rv = str(rv)
				if RE_VAR.match(rv[1:]): raise ValueError(f'Bad rv: {rv}')

			if av == '': av = None
			elif RE_NUM.fullmatch(av): av=json.loads(av) # numeric
			else:
				if OPR[ao][SEQL] not in OPRSTR: raise Exception(f"Bad ao: {ao} for {av}")
				if RE_VAR.match(av[1:]): raise ValueError(f'Bad av: {av}')

			meme.append([ro, rv, ao, av])

	if meme: memes.append(meme)

	return memes

# Input: memes
# Output: Memelang string "opr1val1opr2val2"
def encode(memes: list[list[list]]) -> str:
	memestr = ''
	for meme in memes:
		for ro, rv, ao, av in meme:
			for o, v in ((ro, rv), (ao, av)):
				if o: memestr += str(OPR[o][SOUT])
				if v is not None: memestr += (v if isinstance(v, str) and not RE_ALP.search(v) else json.dumps(v))
		memestr+=END
	return memestr.rstrip(END)


# Choose a is 'alp' for str or 'amt' for numeric
def alpamt(ao:str, av) -> str:
	if ao in OPRNUM or isinstance(av, (int, float)): return 'amt'
	return 'alp'


# Compare two values
def cmpv(c:str, e:str, v1, v2) -> bool:
	if v1 is None or e is None: return True
	if v2 is None: raise ValueError(f'cmpv none {c} {v1}{e}{v2}')
	if c in COLSTR:
		if e == '=': return (str(v1).lower() == str(v2).lower())
		elif e == '!=': return (str(v1).lower() != str(v2).lower())
		else: raise ValueError(f'cmpv str opr {c} {v1}{e}{v2}')
	elif not isinstance(v1, (int, float)) or not isinstance(v2, (int, float)): raise TypeError(f'cmpv !num {c} {v1}{e}{v2}')
	elif e == '=':  return (v2 == v1)
	elif e == '!=': return (v2 != v1)
	elif e == '>':  return (v2 > v1)
	elif e == '>=': return (v2 >= v1)
	elif e == '<':  return (v2 < v1)
	elif e == '<=': return (v2 <= v1)
	else: raise ValueError(f'cmpv num opr {c} {v1}{e}{v2}')


# Store memes as in-memory DB
def add(memeloc:str, memes: list[list[list]], mkeep:bool=True):
	global M_VAL

	if memeloc not in MEMEBASE: MEMEBASE[memeloc]=[]

	for meme in memes:
		mv = None
		for ro, rv, ao, av in meme:
			if rv is None: raise ValueError(f'Bad rv, cannot be empty')
			if av is None: raise ValueError(f'Bad av for {rv}')
			if ro != SPC: raise ValueError(f'Bad ro: {ro}{rv}{ao}{av}')
			if ao != '=': raise ValueError(f'Bad ao: {ro}{rv}{ao}{av}')

			if (isinstance(rv, str) and RE_VAR.match(rv[:1])) \
			or (isinstance(av, str) and RE_VAR.match(av[:1])):
				raise ValueError('add(): variables not allowed')

			# m is specified
			if rv == 'm':
				if mkeep: mv = av
				continue
			# m empty, generate random
			elif not mv:
				if not M_VAL:
					import random
					M_VAL = random.randrange(M_MIN, M_MAX)
				M_VAL += 1
				mv = M_VAL

			row = {'m':mv, 'r':rv, 'alp':None, 'amt':None}
			row[alpamt('=', av)]=av
			MEMEBASE[memeloc].append(row)


# Evaluate one query-pattern meme against rows (full join logic)
def qry(memeloc: str, pattern: list[list[list]]) -> list[list[list]]:
	results = []

	if memeloc not in MEMEBASE: raise ValueError('qry memeloc')
	if len(pattern) != 1: raise ValueError('qry pattern')

	def dfs(idx:int, chosen:list, vcols:dict, me:str, mstack:list):
		if idx == len(pattern[0]):
			results.append(chosen[:])
			return

		ro, rv, ao, av = pattern[0][idx]
		rv = str(rv).lower()

		if isinstance(rv, str) and RE_VAR.match(rv[:1]):
			if rv in vcols: rv = vcols.get(rv)
			else: raise Exception(f'Bad rv {rv}')

		if isinstance(av, str) and RE_VAR.match(av[:1]):
			if av in vcols: av = vcols.get(av)
			else: raise Exception(f'Bad av {av}')

		acol = alpamt(ao, av)

		# explicit mv
		if rv == 'm':
			# !m
			if ro == NOT:
				if len(mstack) < 2 or ao or av: raise ValueError('Bad !m')
				vcols2 = vcols.copy()
				vcols2[MS] = mstack[-2]
				dfs(idx + 1, chosen, vcols2, '=', mstack[:-1])

			# on m= make a new mstack, no a/r
			else: dfs(idx + 1, chosen, vcols.copy(), ao, mstack[:] + [av])

			return # don't evaluate further on rv=m

		# implicit mv
		else:
			mv = None
			mstack2 = mstack[:]
			if mstack2:
				mv = mstack2[-1]
				if not mv: mstack2.pop()

		# Search for matching rows
		for row in MEMEBASE[memeloc]:

			if not cmpv('m', me, mv, row['m']): continue
			if not cmpv('r', OPR[ro][SEQL], rv, row['r']): continue
			if not cmpv(acol, OPR[ao][SEQL], av, row[acol]): continue

			# new var values
			vcols2 = vcols.copy()
			vcols2[AS] = row[acol]
			vcols2[RS] = row['r']
			vcols2[MS] = row['m']
			vcols2[AS+str(row['r']).lower()] = row[acol]

			# new mstack
			mstack3 = mstack2[:]
			if row['m']!=mv:
				mstack3.append(row['m'])
				chosen.append({'m':row['m'], 'r':'m', 'alp':None, 'amt':row['m']})

			# Recurse
			chosen.append(row)
			dfs(idx + 1, chosen, vcols2, mstack3)
			if row['m']!=mv: chosen.pop() # pop m=
			chosen.pop()

	dfs(0, [], {}, None, [])

	# Convert satisfying row tuples back into meme structures
	output = []
	for combo in results:
		meme_out = []
		for row in combo:
			val = row['alp'] if row['alp'] is not None else row['amt']
			meme_out.append([SPC, row['r'], '=', val])
		output.append(meme_out)

	return output