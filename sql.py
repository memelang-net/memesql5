import random
from parse import *
from conf import *

# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# 'a' is a value stored as either 'alp' for str or 'amt' for int/float
# 'r' is the relation of 'a' to the meme
# 'm' is a meme identifier that groups r=a pairs

def selectify(meme: list[list], table: str = None, t:int = 0) -> tuple[str, list]:

	tm1 = 0
	acol = 'alp'
	last_acol = 'alp'
	table = table or DB['table']
	selects, wheres, joins, groupbys, params, ms = [], [], [], [], [], []
	vcols = {}

	for (ro, rv, ao, av) in meme:
		joint = {'r':None, 'alp':None, 'amt':None, 'm':None}

		# Unjoin with !m
		if ro == NOT and rv == 'm':
			if len(ms)<2: raise Exception(f'no m unjoin')
			ms.pop()
			tm1=ms[-1]
			#selects.append(f"' {NOT}m'")
			selects.append(f"' m='")
			selects.append(f"t{tm1}.m")
			continue

		# RID
		rvl = rv.lower() if isinstance(rv, str) else rv
		sel = f"""'{ro}' || t{t}.r || '=' """

		# AID
		# Decide if a is alp or amt
		if isinstance(av, float) or isinstance(av, int) or ao in {'>', '<', '>=', '<='}:
			avl = av
			acol = 'amt'
			sel += f"""|| t{t}.amt"""
		elif isinstance(av, str) and not av.startswith('$'):
			avl = av.lower()
			acol = 'alp'
			sel += f"""|| '"' || t{t}.alp || '"'"""
		else:
			avl = av
			acol = 'alp'
			sel += f"""|| (CASE WHEN t{t}.amt IS NOT NULL THEN t{t}.amt::text ELSE '"' || t{t}.alp || '"' END)"""
		
		# Where
		for c, e, v in (('r', memopr[ro][SEQL], rvl), (acol, memopr[ao][SEQL], avl)):
			if v is None or not e: continue

			# Variable value, reference previous value
			elif isinstance(v, str) and RE_VAR.match(v[:1]):
				if not ms: raise Exception(f'no m join')

				# @, ~, # Join on previous alp/amt, r, or m
				if v == AS: joint[c]=f"t{tm1}.{last_acol}=t{t}.{c}"
				elif v == RS: joint[c]=f"t{tm1}.r=t{t}.{c}"
				elif v == MS: joint[c]=f"t{tm1}.m=t{t}.{c}"

				# @r, where current alp/amt equals previous alp/amt for r
				elif v in vcols:
					col = f"LOWER(t{t}.{c})" if c in ('alp','r') else f"t{t}.{c}"
					wheres.append(f"{col}{e}{vcols[v]}")
				else: raise Exception(f'var {v}')

			# Static value, equivicate
			else:
				col = f"LOWER(t{t}.{c})" if c in ('alp','r') else f"t{t}.{c}"
				wheres.append(f"{col}{e}%s")
				params.append(v)

		# set variable
		if memopr[ro][SEQL] == '=' and rv is not None:
			vcols[f'{AS}{rv}'] = f"LOWER(t{t}.alp)" if acol=='alp' else f"t{t}.amt"
		last_acol = acol

		# Specific b=X
		if (rv == 'm'): continue

		# Join
		elif not joins: # start with from
			joins.append(f'FROM {table} t{t}')
			groupbys.append(f"t{t}.m")
			selects.append(f"'m='")
			selects.append(f"t{t}.m")
			ms.append(t)
		
		else: # join
			# default join on m
			if all(v is None for v in joint.values()):
				joint['m']=f"t{tm1}.m=t{t}.m"
			else:
				groupbys.append(f"t{t}.m")
				selects.append(f"' m='")
				selects.append(f"t{t}.m")
				ms.append(t)

			jands, jors = [], []
			for col, cond in joint.items():
				if cond: jands.append(cond)
				else: jors.append(f"t{tm1}.{col}!=t{t}.{col}")

			if not jands: raise Exception('join')

			jandstr = ' AND '.join(jands)
			jorstr = (' AND (' + ' OR '.join(jors) + ')') if jors else ''
			joins.append(f"LEFT JOIN {table} t{t} ON {jandstr}{jorstr}")

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


def select(memes: list[list[list]], table: str = None) -> tuple[str, list]:
	selects, params = [], []
	for meme in memes:
		qry_select, qry_params = selectify(meme, table)
		selects.append(qry_select)
		params.extend(qry_params)
	return f"SELECT string_agg(v, '') AS vv FROM (" + ' UNION '.join(selects) + ")", params


def insert (memes: list[list[list]], table: str = None) -> tuple[str, list]:
	
	table = table or DB['table']
	rows, params = [], []

	for meme in memes:

		mv = None
		for (ro, rv, ao, av) in meme:
			if memopr[ro][SEQL] != '=': raise ValueError(f'bad ro {ro}')
			elif ao != '=': raise ValueError(f'bad ao {ao}')
			elif rv is None: raise ValueError(f'no rv')
			elif av is None: raise ValueError(f'no av')
			elif rv == 'm':
				if mv: raise Exception(f'double m')
				mv=av

		if not mv: mv = 2**20 + random.getrandbits(62)

		for (ro, rv, ao, av) in meme:
			if rv == 'm': continue
			rows.append('(%s,%s,%s,%s)')
			params.extend([rv, None, None, mv])
			if isinstance(av, str): params[-3]=av
			else: params[-2]=av

	if rows: return f"INSERT INTO {table} VALUES " + ','.join(rows) + " ON CONFLICT DO NOTHING", params

	return None, []


def morgify(sql: str, params: list) -> str:
	for param in params:
		rep = param.replace("'", "''") if isinstance(param, str) else str(param)
		sql = sql.replace("%s", rep, 1)
	return sql