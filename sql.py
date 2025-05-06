import random
from parse import *

# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# 'aid' is stored as either 'alp' for str or 'amt' for int/float
# b=X specifies bid value

DEFTBL = 'meme'

def selectify(meme: list[list], table: str = None, t:int = 0) -> tuple[str, list]:

	tm1 = 0
	acol = 'alp'
	last_acol = 'alp'
	table = table or DEFTBL
	selects, wheres, joins, groupbys, params, bids = [], [], [], [], [], []
	vcols = {}

	for (ro, rv, ao, av) in meme:
		joint = {'rel':None, 'alp':None, 'amt':None, 'bid':None}

		# Unjoin with !b
		if ro == NOT and rv == 'b':
			if len(bids)<2: raise Exception('no bid unjoin')
			bids.pop()
			tm1=bids[-1]
			#selects.append(f"' {NOT}b'")
			selects.append(f"' b='")
			selects.append(f"t{tm1}.bid")
			continue

		# RID
		rvl = rv.lower() if isinstance(rv, str) else rv
		sel = f"""'{ro}' || t{t}.rel || '=' """

		# AID
		# Decide if aid is alp or amt
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
		for c, e, v in (('rel', memopr[ro][SEQL], rvl), (acol, memopr[ao][SEQL], avl)):
			if v is None or not e: continue
			elif isinstance(v, str) and v.startswith('$'):
				if not bids: raise Exception('no bid join')
				if v in ('$', '$'+c[0:1]): joint[c]=f"t{tm1}.{c}=t{t}.{c}" # $ join on slot
				elif v == '$a': joint[c]=f"t{tm1}.{last_acol}=t{t}.{c}" # join on previous alp/amt
				elif v == '$r': joint[c]=f"t{tm1}.rel=t{t}.{c}" # join on previous rel
				elif v == '$b': joint[c]=f"t{tm1}.bid=t{t}.{c}" # join on previous bid (default)
				elif v in vcols: # where current alp/amt equals previous alp/amt for $rel
					col = f"LOWER(t{t}.{c})" if c in ('alp','rel') else f"t{t}.{c}"
					wheres.append(f"{col}{e}{vcols[v]}")
				else: raise Exception(f'var {v}')
			else: # where current col equals value
				col = f"LOWER(t{t}.{c})" if c in ('alp','rel') else f"t{t}.{c}"
				wheres.append(f"{col}{e}%s")
				params.append(v)

		# set variable
		if memopr[ro][SEQL] == '=' and rv is not None:
			vcols[f'${rv}'] = f"LOWER(t{t}.alp)" if acol=='alp' else f"t{t}.amt"
		last_acol = acol

		# Specific b=X
		if (rv == 'b'): continue

		# Join
		elif not joins: # start with from
			joins.append(f'FROM {table} t{t}')
			groupbys.append(f"t{t}.bid")
			selects.append("'b='")
			selects.append(f"t{t}.bid")
			bids.append(t)
		
		else: # join
			# default join on bid
			if all(v is None for v in joint.values()):
				joint['bid']=f"t{tm1}.bid=t{t}.bid"
			else:
				groupbys.append(f"t{t}.bid")
				selects.append("' b='")
				selects.append(f"t{t}.bid")
				bids.append(t)

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

	return f"SELECT CONCAT({selectstr}, '') AS m {joinstr} {wherestr} GROUP BY {groupbystr}", params


def select(memes: list[list[list]], table: str = None) -> tuple[str, list]:
	selects, params = [], []
	for s, meme in enumerate(memes):
		qry_select, qry_params = selectify(meme, table)
		selects.append(qry_select)
		params.extend(qry_params)
	return "SELECT string_agg(m, '; ') AS mm FROM (" + ' UNION '.join(selects) + ")", params


def insert (memes: list[list[list]], table: str = None) -> tuple[str, list]:
	
	table = table or DEFTBL
	rows, params = [], []

	for meme in memes:

		bv = None
		for (ro, rv, ao, av) in meme:
			if memopr[ro][SEQL] != '=': raise ValueError(f'bad ro {ro}')
			elif ao != '=': raise ValueError(f'bad ao {ao}')
			elif rv is None: raise ValueError(f'no rv')
			elif av is None: raise ValueError(f'no av')
			elif rv=='b':
				if bv: raise Exception('double bid')
				bv=av

		if not bv: bv = 2**20 + random.getrandbits(62)

		for (ro, rv, ao, av) in meme:
			if rv=='b': continue
			rows.append('(%s,%s,%s,%s)')
			params.extend([rv, None, None, bv])
			if isinstance(av, str): params[-3]=av
			else: params[-2]=av

	if rows: return f"INSERT INTO {table} VALUES " + ','.join(rows) + " ON CONFLICT DO NOTHING", params

	return None, []


def morgify(sql: str, params: list) -> str:
	for param in params:
		rep = param.replace("'", "''") if isinstance(param, str) else str(param)
		sql = sql.replace("%s", rep, 1)
	return sql