import random
from .parse import *

# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# 'aid' is stored as either 'alp' for str or 'amt' for int/float
# b=X specifies bid value

DEFTBL = 'meme'

def selectify(meme: list[list], table: str = None, t:int = 0) -> tuple[str, list]:

	tm1 = 0
	acol = 'alp'
	table = table or DEFTBL
	selects, wheres, joins, groupbys, params, bids = [], [], [], [], [], []

	for (ro, rv, ao, av) in meme:
		joint = {'rid':None,'alp':None,'amt':None,'bid':None}

		# Unjoin with CLS=']'
		if ro == CLS:
			if not bids: raise Exception('no bid unjoin')
			bids.pop()
			tm1=bids[-1]
			selects.append("']'")
			continue

		# [rid defaults to [rid=$a
		elif ro == OPN and ao in (None,'=') and av is None: ro, ao, av = SPC, '=', '$a'

		# RID
		rvl = rv.lower() if isinstance(rv, str) else rv
		sel = f"""'{ro}' || t{t}.rid || '=' """

		# AID
		# Decide if aid is alp or amt
		if av is None or (isinstance(av, str) and av.startswith('$')):
			avl = av
			acol = 'alp'
			sel += f"""|| (CASE WHEN t{t}.amt IS NOT NULL THEN t{t}.amt::text ELSE '"' || t{t}.alp || '"' END)"""
		elif isinstance(av, str):
			avl = av.lower()
			acol = 'alp'
			sel += f"""|| '"' || t{t}.alp || '"'"""
		else:
			avl = av
			acol = 'amt'
			sel += f"""|| t{t}.amt"""

		# Where
		for c, e, v in (('rid', memopr[ro][SEQL], rvl), (acol, memopr[ao][SEQL], avl)):
			if v is None or not e: continue
			elif isinstance(v, str) and v.startswith('$'):
				if not bids: raise Exception('no bid join')
				if v in ('$', '$'+c[0:1]): joint[c]=f"""t{tm1}.{c}=t{t}.{c}"""
				elif v == '$a': joint[c]=f"""t{tm1}.{acol}=t{t}.{c}""" # fix to last-acol
				elif v == '$r': joint[c]=f"""t{tm1}.rid=t{t}.{c}"""
				elif v == '$b': joint[c]=f"""t{tm1}.bid=t{t}.{c}"""
				else: raise Exception(f'var {v}')
			else:
				col = f"LOWER(t{t}.{c})" if isinstance(v, str) else f"t{t}.{c}"
				wheres.append(f"{col}{e}%s")
				params.append(v)

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
				joint['bid']=f"""t{tm1}.bid=t{t}.bid"""
			else:
				groupbys.append(f"t{t}.bid")
				selects.append("' [b='")
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
	return "SELECT string_agg(m, '; ') FROM (" + ' UNION '.join(selects) + ")", params


def insert (memestr: str, table: str = None) -> tuple[str, list]:
	
	memes = decode(memestr)

	table = table or DEFTBL
	rows, params = [], []

	for movs in memes:

		values={BID:[], RID:[], AMT:[]}

		for opr, val in movs:
			for v in values: values[v].append(None)
			values[memopr[opr][SCOL]][-1]=val

		values[BID] = [x for x in values[BID] if x is not None]

		if len(values[BID])>1: raise Exception(f'redundant bid')

		if not values[BID]: values[BID].append(2**20 + random.getrandbits(62))

		gbrow = SQLPARAM.copy()
		gbrow[SQLCOLS[BID]], = values[BID][0]

		for i,rid in enumerate(values[RID]):
			if rid is None: continue
			row = gbrow.copy()
			row[SQLCOLS[RID]] = rid
			row[SQLCOLS[ALP if isinstance(values[AMT][i+1], str) else AMT]] = values[AMT][i+1]
			rows.append(SQLPLACE)
			params.extend(row)

	if rows: return f"INSERT INTO {DEFTBL} VALUES " + ','.join(rows) + " ON CONFLICT DO NOTHING", params

	return None, []