# Memelang.net | (c) HOLTWORK LLC | Patents Pending
# Encode and decode Memelang string to list
# pair = [r operator, r value, a operator, a value]
# meme = pair list = [pair, ...]
# memes = meme list = pair list list = [[pair, ...], ...]

import re, json

SCOL, SEQL, SOUT = 0, 1, 2 			# name for each slot in memopr[opr] list
BID, RID, AID = 'm', 'r', 'a'		# name for each column in memopr[opr][SCOL]
END, SPC, NOT = ';', ' ', '!'		# Special characters
AS, RS, MS = '@', '~', '#'			# Var symbols

memopr = { # operator characters and their settings
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

STREQL = ('=','!=') # String equalities
RE_DIV = re.compile(r'([\s;\]]+)') # Dividers between pairs
RE_QOT = re.compile(r'("(?:(?:\\.)|[^"\\])*")') # String between quotes
RE_NUM = re.compile(r'^[+-]?\d+(?:\.\d+)?$') # Matches non-numeric chars, must be string
RE_ALP = re.compile(r'[^a-zA-Z0-9_\$\#\~\@]') # Complex string must be wrapped in quotes
RE_VAR = re.compile(r'[\@\~\#\$]') # Variable symbols
RE_PAR = re.compile(r"(!)?([a-zA-Z0-9_\$\#\~\@]*)(>=|<=|!=|=|>|<)?([a-zA-Z0-9_\$\#\~\@\.\-\+]*)") # !R>=A

# Input: Memelang string as "R=A:B R>A:B R<=A <=A =:B !R=A"
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
			elif meme[-1][2] not in STREQL: raise ValueError(f'Bad quote ao: {meme[-1][2]}""')
			meme[-1][3]=json.loads(part)
			continue

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
			elif not memopr.get(ro): raise ValueError(f"Bad ro: {ro}")

			if ao in (None,''): ao=None
			elif not memopr.get(ao): raise ValueError(f"Bad ao: {ao}")

			# Check values
			if rv == '': rv = None
			else:
				rv = str(rv)
				if RE_VAR.match(rv[1:]): raise ValueError(f'Bad rv: {rv}')

			if av == '': av = None
			elif RE_NUM.fullmatch(av): av=json.loads(av) # numeric
			else:
				if memopr[ao][SEQL] not in STREQL: raise Exception(f"Bad ao: {ao} for {av}")
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
				if o: memestr += str(memopr[o][SOUT])
				if v is not None: memestr += (v if isinstance(v, str) and not RE_ALP.search(v) else json.dumps(v))
		memestr+=END
	return memestr.rstrip(END)