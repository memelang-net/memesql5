# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# Encode and decode Memelang string to list
# ram = [r operator, r value, a operator, a value, m operator, m value]
# meme = ram list = [ram, ...]
# memes = meme list = ram list list = [[ram, ...], ...]

import json, random, re

MEMEBASE = {}
M_MIN = 1 << 20
M_MAX = 1 << 62

## ENCODE / DECODE

RO, RV, AO, AV, MO, MV = 0, 1, 2, 3, 4, 5
SEQL, SOUT = 0, 1 									# name for each slot in OPR[opr] list
END, SPC, NOT, CLS, POP = ';', ' ', '!', ']', '=^'	# Special characters
AS, RS, MS = '@', '%', '#'							# Var symbols

OPR = { # operator characters and their settings
	None	: (None,	None),
	END		: (None,	END),
	SPC		: ('=',		SPC),
	NOT		: ('!=',	SPC+NOT),
	'='		: ('=',		'='),
	'!='	: ('!=',	'!='),
	'>'		: ('>',		'>'),
	'<'		: ('<',		'<'),
	'>='	: ('>=',	'>='),
	'<='	: ('<=',	'<='),
	POP		: ('=',		POP),
}

OPRSTR = {'=', '!='}
OPRNUM = {'>', '<', '>=', '<='}
COLSTR = {'r', 'alp'}
COLNUM = {'m', 'amt'}

RE_DIV = re.compile(r'([\s;]+)') # Dividers between pairs
RE_QOT = re.compile(r'("(?:(?:\\.)|[^"\\])*")') # String between quotes
RE_NUM = re.compile(r'^[+-]?\d+(?:\.\d+)?$') # Matches non-numeric chars, must be string
RE_ALP = re.compile(r'[^a-zA-Z0-9_\$\#\%\@]') # Complex string must be wrapped in quotes
RE_VAR = re.compile(r'[\@\%\#]') # Variable symbols
RE_PAR = re.compile(r"(!)?([a-zA-Z0-9_\#\%\@]*)(>=|<=|!=|=\^|=|>|<)?([a-zA-Z0-9_\#\%\@\.\-\+]*)") # !R>=A

RE_RJR = re.compile(r'([a-zA-Z0-9_\$\#\%\@]*)\[([a-zA-Z0-9_\$\#\%\@]*)')
RE_RMR = r'\1= m!=# \2=@'

# Input: Memelang string as 'R=A R>A ="x y"; <=A !R=A'
# Output: memes
def decode(memestr: str) -> list[list[list]]:

	# Remove comments, newlines, and empty quotes
	memestr = re.sub(r'\s*//.*$|""|\n', '', memestr, flags=re.MULTILINE).strip()

	if len(memestr) == 0: raise Exception('Empty memestr')

	memes, meme = [], []
	mo, mv, md = '=', None, 0

	# Split by quotes, skip inside the quotes, parse outside of the quotes
	parts = RE_QOT.split(memestr)
	if len(parts) % 2 == 0: raise ValueError('Unclosed quote')

	for p, part in enumerate(parts):

		# Assign string inside quotes straight to ="value"
		if p % 2 == 1:
			if not meme: raise ValueError('Start quote')
			if meme[-1][AO] not in OPRSTR: raise ValueError(f'Bad quote ao: {meme[-1][2]}""')
			if isinstance(meme[-1][AV], str): meme[-1][AV]+=json.loads(part)
			else: meme[-1][AV]=json.loads(part)
			continue

		# Parse string outside quotes into R=A

		# Desugar shorthand
		part = re.sub(RE_RJR, RE_RMR, part)
		part = part.replace(CLS, 'm'+POP+MS)

		# Split by spaces
		for subpart in RE_DIV.split(part):

			# space/end
			if subpart == '' or re.fullmatch(RE_DIV, subpart):
				if END in subpart:
					if meme: memes.append(meme)
					meme=[]
					mo, mv, md = '=', None, 0
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

			# m=
			if rv == 'm':
				if ro != SPC: raise ValueError(f"Bad {ro}m")
				if len(str(av))>1 and av == mv: av = MS # consecutive literals become variable
				if ao != '=' or av != MS:
					mo, mv = ao, av
					if mo == POP:
						if md<2: raise ValueError(f"Bad m{mo}{mv}")
						md-=1
					else: md+=1
				continue

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

			meme.append([ro, rv, ao, av, mo, mv])
			mo, mv = '=', MS

	if meme: memes.append(meme)

	return memes

# Input: memes
# Output: Memelang string "opr1val1opr2val2"
def encode(memes: list[list[list]]) -> str:
	memestr = ''
	for meme in memes:
		for ro, rv, ao, av, mo, mv in meme:
			if mo not in (None, '=') or mv not in (None, MS):
				memestr += ' m' + OPR[mo][SOUT]
				if mv is not None: memestr += (mv if isinstance(mv, str) and not RE_ALP.search(mv) else json.dumps(mv))

			for o, v in ((ro, rv), (ao, av)):
				if o: memestr += OPR[o][SOUT]
				if v is not None: memestr += (v if isinstance(v, str) and not RE_ALP.search(v) else json.dumps(v))
		memestr+=END
	return memestr.rstrip(END)



## IN-MEMORY DB

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
def add(memeloc:str, memes: list[list[list]]):
	mval = None

	if memeloc not in MEMEBASE: MEMEBASE[memeloc]=[]

	for meme in memes:
		mv = None
		for ro, rv, ao, av, mo, _mv in meme:
			if rv is None: raise ValueError(f'Bad rv, cannot be empty')
			if av is None: raise ValueError(f'Bad av for {rv}')
			if ro != SPC: raise ValueError(f'Bad ro: {ro}{rv}{ao}{av}')
			if ao != '=': raise ValueError(f'Bad ao: {ro}{rv}{ao}{av}')
			if mo != '=': raise ValueError(f'Bad mo: m{mo}{_mv}')

			if (isinstance(rv, str) and RE_VAR.match(rv[:1])) \
			or (isinstance(av, str) and RE_VAR.match(av[:1])):
				raise ValueError('add(): variable not allowed')

			if _mv != MS:
				if isinstance(_mv, str) and RE_VAR.match(_mv[:1]):
					raise ValueError('add(): variable not allowed')
				elif _mv: mv = _mv # use specified m=123
				else: # generate random m=456
					if not mval: mval = random.randrange(M_MIN, M_MAX)
					mval += 1
					mv = mval

			row = {'m':mv, 'r':rv, 'alp':None, 'amt':None}
			row[alpamt(None, av)]=av
			MEMEBASE[memeloc].append(row)


# Evaluate one query-pattern meme against rows (full join logic)
def qry(memeloc: str, pattern: list[list[list]]) -> list[list[list]]:
	results = []

	if memeloc not in MEMEBASE: raise ValueError('qry memeloc')
	if len(pattern) != 1: raise ValueError('qry pattern')

	def dfs(idx:int, chosen:list, vcols:dict, mstack:list):
		if idx == len(pattern[0]):
			results.append(chosen[:])
			return

		ram = pattern[0][idx][:]
		mstack2 = mstack[:]
		vcols2 = vcols.copy()

		newm = ram[MO]!='=' or ram[MV] != MS

		# Populate variables
		for i in (RV, AV, MV):
			if not isinstance(ram[i], str) or not RE_VAR.match(ram[i][:1]): continue
			elif ram[i-1] == POP: # m=^#
				mstack2.pop()
				ram[i], vcols2[MS] = mstack2[-1], mstack2[-1]
			elif ram[i] in vcols2: ram[i] = vcols2[ram[i]]
			else: raise Exception(f'Bad var {ram[i]}')

		ro, rv, ao, av, mo, mv = ram
		rv = str(rv).lower()
		acol = alpamt(ao, av)

		# Search for matching rows
		for row in MEMEBASE[memeloc]:

			if not cmpv('m', mo, mv, row['m']): continue
			if not cmpv('r', OPR[ro][SEQL], rv, row['r']): continue
			if not cmpv(acol, OPR[ao][SEQL], av, row[acol]): continue

			# new var values
			vcols2[AS] = row[acol]
			vcols2[RS] = row['r']
			vcols2[MS] = row['m']
			vcols2[AS+str(row['r']).lower()] = row[acol]

			# Recurse
			chosen.append(row)
			dfs(idx + 1, chosen, vcols2, mstack2)
			chosen.pop()

	dfs(0, [], {}, [])

	# Convert satisfying row tuples back into meme structures
	output = []
	for combo in results:
		meme_out = []
		mv = None
		for row in combo:
			meme_out.append([
				SPC, row['r'], 
				'=', (row['alp'] if row['alp'] is not None else row['amt']), 
				'=', ('#' if row['m']==mv else row['m'])
			])
			mv=row['m']
		output.append(meme_out)

	return output



## SQL DB
# 'a' is a value stored as either 'alp' for str or 'amt' for int/float
# 'r' is the relation of 'a' to the meme
# 'm' is a meme identifier that groups r=a pairs

def selectify(meme: list[list], table: str = 'meme', t:int = 0) -> tuple[str, list]:

	tm1 = 0
	acol = 'alp'
	selects, wheres, joins, groupbys, params, mstack = [], [], [], [], [], []
	vcols = {}

	for ro, rv, ao, av, mo, mv in meme:
		joint = {'r':None, 'alp':None, 'amt':None, 'm':None}

		# M
		newm = mo!='=' or mv != MS
		newg = newm

		# R
		rvl = rv.lower() if isinstance(rv, str) else rv
		sel = f"""'{ro}' || t{t}.r || '=' """

		# A as ALP/AMT
		acol = alpamt(ao, av)
		if acol == 'amt':
			avl = av		
			sel += f"""|| t{t}.amt"""
		elif isinstance(av, str) and not RE_VAR.match(av[:1]):
			avl = av.lower()
			sel += f"""|| '"' || t{t}.alp || '"'"""
		else:
			avl = av
			sel += f"""|| (CASE WHEN t{t}.amt IS NOT NULL THEN t{t}.amt::text ELSE '"' || t{t}.alp || '"' END)"""

		# Where
		for c, o, v in (('m', mo, mv), ('r', OPR[ro][SEQL], rvl), (acol, OPR[ao][SEQL], avl)):
			if v is None or not o: continue

			# Expand variables
			if isinstance(v, str) and RE_VAR.match(v[:1]):
				if v not in vcols: raise ValueError(f'var {v}')

				if c == 'm' and o == POP: # m=^ unjoin
					mstack.pop()
					tm1=mstack[-1]
					vcols[MS] = f"t{tm1}.m"
					v=MS
					newg=False

				col = f"LOWER(t{t}.{c})" if c in COLSTR else f"t{t}.{c}"
				joint[c] = f"{col}{o}{vcols[v]}"

			# Static value, equivicate
			else:
				col = f"LOWER(t{t}.{c})" if c in COLSTR else f"t{t}.{c}"
				wheres.append(f"{col}{o}%s")
				params.append(v)

		# JOINING
		# start with from
		if not joins:
			joins.append(f'FROM {table} t{t}')
			newm, newg = True, True
	
		# new join
		if all(v is None for v in joint.values()): raise Exception('join')
		jands, jors = [], []
		for col, cond in joint.items():
			if cond: jands.append(cond)
			else: jors.append(f"t{tm1}.{col}!=t{t}.{col}")

		jandstr = ' AND '.join(jands)
		jorstr = (' AND (' + ' OR '.join(jors) + ')') if jors else ''
		joins.append(f"LEFT JOIN {table} t{t} ON {jandstr}{jorstr}")

		# new m, group by m and select m=
		if newm:
			if newg: groupbys.append(f"t{t}.m")
			selects.append(f"' m='")
			selects.append(f"t{t}.m")
			mstack.append(t)

		# set @rel variable
		if OPR[ro][SEQL] == '=' and rv is not None:
			vcols[f'{AS}{rv}'] = f"LOWER(t{t}.alp)" if acol=='alp' else f"t{t}.amt"

		vcols[AS] = f"t{t}.{acol}" if acol == 'amt' else f"LOWER(t{t}.{acol})"
		vcols[RS] = f"LOWER(t{t}.r)"
		vcols[MS] = f"t{t}.m"

		# Select
		selects.append(f"""string_agg(DISTINCT {sel}, '')""")

		tm1=t
		t+=1

	if not joins: raise Exception('missing k=v')

	joinstr = ' '.join(joins)
	selectstr = ','.join(selects)
	groupbystr = ','.join(groupbys)
	wherestr = ('WHERE ' + ' AND '.join(wheres)) if wheres else ''

	return f"SELECT CONCAT({selectstr}, '{END} ') AS v {joinstr} {wherestr} GROUP BY {groupbystr}", params


def select(memes: list[list[list]], table: str = 'meme') -> tuple[str, list]:
	selects, params = [], []
	for meme in memes:
		qry_select, qry_params = selectify(meme, table)
		selects.append(qry_select)
		params.extend(qry_params)
	return f"SELECT string_agg(v, '') AS vv FROM (" + ' UNION '.join(selects) + ")", params


def insert (memes: list[list[list]], table: str = 'meme') -> tuple[str, list]:
	
	rows, params = [], []
	mval = None

	for meme in memes:
		mv = None
		for ro, rv, ao, av, mo, _mv in meme:
			if OPR[ro][SEQL] != '=': raise ValueError(f'bad ro {ro}')
			elif ao != '=': raise ValueError(f'bad ao {ao}')
			elif mo != '=': raise ValueError(f'bad mo {mo}')
			elif rv is None: raise ValueError(f'no rv')
			elif av is None: raise ValueError(f'no av')

			if _mv == MS: pass
			elif _mv: mv = int(_mv)
			else:
				if not mval: mval = random.randrange(M_MIN, M_MAX)
				mval+=1
				mv = mval
			if not mv: raise Exception(f'insert mv')

			rows.append('(%s,%s,%s,%s)')
			params.extend([rv, None, None, mv])
			if isinstance(av, str): params[-3]=av
			else: params[-2]=av

	if rows: return f"INSERT INTO {table} VALUES " + ','.join(rows) + " ON CONFLICT DO NOTHING", params

	return None, []


def morgify(sql: str, params: list) -> str:
	for param in params: sql = sql.replace("%s", json.dumps(param), 1)
	return sql