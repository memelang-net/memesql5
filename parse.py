# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# Encode and decode Memelang string to list
# hexeme = [r operator, r value, a operator, a value, m operator, m value]
# meme = hexeme list = [hexeme, ...]
# memes = meme list = hexeme list list = [[hexeme, ...], ...]

import csv, random, re

MEMEBASE = {}
M_MIN = 1 << 20
M_MAX = 1 << 62

## ENCODE / DECODE

RO, RV, AO, AV, MO, MV = 0, 1, 2, 3, 4, 5
SEQL, SOUT = 0, 1 								# name for each slot in OPR[opr] list
END, SPC, NOT, CLS = ';', ' ', '!', ']'			# Special characters
AS, RS, MS = '@', '%', '#'						# Var symbols
POP, POP2, POP3 = '=^', '=^^', '=^^^'

OPR = { # operator characters and their settings
	None	: (None,	''),
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
	POP2	: ('=',		POP2),
	POP3	: ('=',		POP3),
}

OPRVAR = {AS, RS, MS}
OPRREL = {'!'}
OPRNUM = {'>', '<', '>=', '<='}
COLSTR = {'r', 'alp'}
#COLNUM = {'m', 'amt'}
#OPRSTR = {'=', '!='}
RE_NUM = re.compile(r'^[+-]?\d+$') # Matches non-numeric chars, must be string
RE_ALP = re.compile(r'[^a-zA-Z0-9_\$\#\%\@]') # Complex string must be wrapped in quotes
RE_VAR = re.compile(r'[\@\%\#]') # Variable symbols
RE_RJR = re.compile(r'([a-zA-Z0-9_\$\#\%\@]*)\[([a-zA-Z0-9_\$\#\%\@]*)')
RE_HEX = re.compile(
    r'("[^"]*(?:""[^"]*)*")'
    r'|(>=|<=|!=|=\^+|=|>|<|!|\]|\,)'
    r'|([a-zA-Z0-9_\$\#\%\@]+)'
    r'|([\s;]+)'
)

# Input: Memelang string as 'R=A R,R>A =A,"x y"; <=A !R=A'
# Output: memes
def decode(memestr: str) -> list[list[list]]:

	# Remove comments
	memestr = re.sub(r'\s*//.*$', '', memestr, flags=re.MULTILINE).strip()

	if len(memestr) == 0: raise Exception('Empty memestr')

	memes, meme, hexparts = [], [], []
	mo, mv, md = '=', [], 0

	# Group string parts into ['R,R,R!=A,"x,y",A', ...]
	preparts = RE_HEX.split(memestr+';')

	# Clean and desugar
	parts=[]
	for prepart in preparts:
		if not prepart: continue
		elif m:=RE_RJR.match(prepart): parts.extend([m.group(1),'=',SPC,'m','!=',MS,SPC,m.group(2),'=','@'])
		elif prepart == CLS: parts.extend(['m',POP,MS])
		else: parts.append(prepart.strip())

	preparts=[]

	for part in parts:
		# SPC or END
		if not part or part == END:
			if hexparts:
				slot = RO
				hexeme = [SPC, [], None, [], mo, mv]

				for hexpart in hexparts:
					if hexpart in OPRREL: # ro
						if slot!=RO: raise ValueError(f'Bad ro: {hexpart}')
						hexeme[RO]=hexpart
						slot+=1
					elif hexpart in OPR: # ao
						if slot>=AO: raise ValueError(f'Bad ao: {hexpart}')
						hexeme[AO]=hexpart
						slot+=1
					else: # rv, av
						if slot not in (RV,AV): slot+=1
						if isinstance(hexpart, str) and hexpart[:1]!='"':
							if RE_ALP.match(hexpart) or RE_VAR.match(hexpart[1:]): raise ValueError(f'Bad str: {hexpart}')
						if hexpart != ',': hexeme[slot].append(hexpart)

				# m=
				if hexeme[RV]==['m']: 
					if hexeme[AO].startswith(POP):
						md-=hexeme[AO].count('^')
						if md<0: raise Exception('Bad pop')
					else: md+=1
					mo, mv = hexeme[AO], hexeme[AV]
				else:
					meme.append(hexeme)
					mo, mv = '=', [MS] # implict m=# join

			# END
			if part == END:
				if meme: memes.append(meme)
				meme=[]
				mo, mv, md = '=', [], 0

			hexparts = []

		# Operator/Value
		else: 
			if part[:1]=='"':
				if part != '""': hexparts.append(next(csv.reader([part]))[0])
			elif '.' in part: hexparts.append(float(part))
			elif RE_NUM.fullmatch(part): hexparts.append(int(part))
			else: hexparts.append(part)

	return memes


def hexencode(row: list, opr = None):
	if not row: return OPR[opr][SOUT]
	out = []
	for f in row:
		if f is None: continue
		s = str(f)
		if isinstance(f, str) and (RE_ALP.match(s) or RE_VAR.match(s[1:])): s = '"' + s.replace('"', '""') + '"'
		out.append(s)
	return OPR[opr][SOUT] + ','.join(out)


# Input: memes
# Output: Memelang string "opr1val1opr2val2"
def encode(memes: list[list[list]]) -> str:
	memestr = ''
	for meme in memes:
		for ro, rv, ao, av, mo, mv in meme:
			if mo not in (None, '=') or (mv and mv!=[MS]):
				memestr += ' m' + hexencode(mv, mo)
			memestr += hexencode(rv, ro) + hexencode(av, ao)	
		memestr += END
	return memestr


## IN-MEMORY DB

# Is this string a variable?
def isvar (val) -> bool:
	return isinstance(val, str) and val[0] in OPRVAR

# Choose a is 'alp' for str or 'amt' for numeric
def alpamt(av: list, ao:str = None) -> str:
	if ao in OPRNUM or (av and isinstance(av[0], (int, float))): return 'amt'
	return 'alp'
	

# Compare two values
def cmpv(c:str, e:str, v1: list, v2) -> bool:
	if not v1 or e is None: return True
	if v2 is None: raise ValueError(f'cmpv none {c} {v1}{e}{v2}')

	if isinstance(v1[0], (int, float)): 
		if not isinstance(v2, (int, float)): raise ValueError('v2 num')
		if len(v1)>1: raise ValueError('v1 len')
		if e == '=':  return (v2 == v1[0])
		elif e == '!=': return (v2 != v1[0])
		elif e == '>':  return (v2 > v1[0])
		elif e == '>=': return (v2 >= v1[0])
		elif e == '<':  return (v2 < v1[0])
		elif e == '<=': return (v2 <= v1[0])
		else: raise ValueError(f'cmpv opr {c} {v1[0]}{e}{v2}')
	
	if e == '=': return (str(v2).lower() in v1)
	elif e == '!=': return (str(v2).lower() not in v1)
	else: raise ValueError(f'cmpv str opr {c} {v1}{e}{v2}')


# Store memes as in-memory DB
def add(memeloc:str, memes: list[list[list]]):
	mval = None

	if memeloc not in MEMEBASE: MEMEBASE[memeloc]=[]

	for meme in memes:
		mv = [None]
		for ro, rv, ao, av, mo, _mv in meme:
			if len(rv) != 1 or rv[0] is None: raise ValueError(f'Bad rv, cannot be empty')
			if len(av) != 1 or av[0] is None: raise ValueError(f'Bad av for {rv}')
			if len(_mv) > 1: raise ValueError(f'Bad m for {rv}')
			if ro != SPC: raise ValueError(f'Bad ro: {ro}{rv}{ao}{av}')
			if ao != '=': raise ValueError(f'Bad ao: {ro}{rv}{ao}{av}')
			if mo != '=': raise ValueError(f'Bad mo: m{mo}{_mv}')

			if isvar(rv[0]) or isvar(av[0]): raise ValueError('add(): variable not allowed')

			if _mv != [MS]:
				if isvar(_mv[0]): raise ValueError('add(): variable not allowed')
				elif _mv[0]: mv = _mv # use specified m=123
				else: # generate random m=456
					if not mval: mval = random.randrange(M_MIN, M_MAX)
					mval += 1
					mv = [mval]

			row = {'m':mv[0], 'r':rv[0], 'alp':None, 'amt':None}
			row[alpamt(av)]=av[0]
			MEMEBASE[memeloc].append(row)


# Evaluate one query-pattern meme against rows (full join logic)
def qry(memeloc: str, pattern: list[list[list]]) -> list[list[list]]:
	results = []

	if memeloc not in MEMEBASE: raise ValueError('qry memeloc')
	if len(pattern) != 1: raise ValueError('qry pattern')

	def dfs(idx:int, chosen:list, vcols:dict):
		if idx == len(pattern[0]):
			results.append(chosen[:])
			return

		hexeme = pattern[0][idx][:]
		vcols2 = vcols.copy()
		if not MS+MS in vcols2: vcols2[MS+MS]=[]

		newm = hexeme[MO]!='=' or hexeme[MV] != [MS]

		# Populate variables
		for i in (RV, AV, MV):
			for j,v in enumerate(hexeme[i]):
				if not v or not isinstance(v,str): continue
				if isvar(v):
					if hexeme[i-1].startswith(POP):
						vcols2[MS + MS] = vcols2[MS + MS][:-1*hexeme[i - 1].count('^')]
						hexeme[i][j], vcols2[MS] = vcols2[MS+MS][-1], vcols2[MS+MS][-1]
					elif v in vcols2: hexeme[i][j] = vcols2[v]
					else: raise Exception(f'Bad var {v}')
				else: hexeme[i][j] = v.lower()

		ro, rv, ao, av, mo, mv = hexeme
		acol = alpamt(av, ao)

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
			if newm: vcols2[MS+MS].append(row['m'])

			# Recurse
			chosen.append(row)
			dfs(idx + 1, chosen, vcols2)
			chosen.pop()

	dfs(0, [], {})

	# Convert satisfying row tuples back into meme structures
	output = []
	for combo in results:
		meme_out = []
		mvv = None
		for row in combo:
			meme_out.append([
				SPC, row['r'], 
				'=', (row['alp'] if row['alp'] is not None else row['amt']), 
				'=', ('#' if row['m']==mvv else row['m'])
			])
			mvv=row['m']
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
		newm = mo != '=' or mv != [MS]
		newg = newm

		# R
		rv = [str(v).lower() for v in rv]
		sel = f"""'{ro}' || t{t}.r || '=' """

		# A as ALP/AMT
		acol = alpamt(av, ao)
		if acol == 'amt':
			sel += f"""|| t{t}.amt"""
		elif av and not isvar(av[0]):
			av = [v.lower() if isinstance(v, str) else v for v in av]
			sel += f"""|| '"' || t{t}.alp || '"'"""
		else:
			sel += f"""|| (CASE WHEN t{t}.amt IS NOT NULL THEN t{t}.amt::text ELSE '"' || t{t}.alp || '"' END)"""

		# Where
		for c, o, v in (('m', mo, mv), ('r', OPR[ro][SEQL], rv), (acol, OPR[ao][SEQL], av)):
			if v is None or not o: continue

			# Expand variables
			lv = {}
			for i,vv in enumerate(v):
				if isvar(vv):
					if vv not in vcols: raise ValueError(f'var {vv}')
					if c == 'm' and o.startswith(POP):
						mstack = mstack[:-1*o.count('^')]
						tm1=mstack[-1]
						vcols[MS] = f"t{tm1}.m"
						vv=MS
						newg=False

					lv[i] = vcols[vv]

			col = f"LOWER(t{t}.{c})" if c in COLSTR else f"t{t}.{c}"
			vlen = len(v)

			if vlen==1 and len(lv)==1: joint[c] = f"{col}{o}{lv[0]}"
			else:
				wherestr = col
				if vlen == 1: wherestr+=o
				elif o == '=': wherestr+=' IN ('
				elif o == '!=': wherestr+=' NOT IN ('
				else: raise Exception('where in')

				for i,vv in enumerate(v):
					if i>0: wherestr+=','
					if i in lv: wherestr+=lv[i]
					else:
						wherestr+="%s"
						params.append(vv)

				if vlen > 1: wherestr+=')'
				wheres.append(wherestr)

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
		if OPR[ro][SEQL] == '=' and len(rv)==1:
			vcols[f'{AS}{rv[0]}'] = f"LOWER(t{t}.alp)" if acol=='alp' else f"t{t}.amt"

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
	
	memeloc = 'tmp'+str(random.randrange(M_MIN, M_MAX))
	add(memeloc, memes)

	rows, params = [], []
	for row in MEMEBASE[memeloc]:
		rows.append('(%s,%s,%s,%s)')
		params.extend([row['r'], row['alp'], row['amt'], row['m']])

	MEMEBASE[memeloc]=[]

	if rows: return f"INSERT INTO {table} VALUES " + ','.join(rows) + " ON CONFLICT DO NOTHING", params

	return None, []


def morgify(sql: str, params: list) -> str:
	for param in params: sql = sql.replace("%s", param, 1)
	return sql