#!/usr/bin/env python3

__version__ 	= "5.0.9"
__title__		= "memelang"
__summary__		= "A compact graph-relational query language"
__uri__			= "https://memelang.net/"
__author__		= "Bri Holt"
__email__		= "info@memelang.net"
__copyright__	= "© 2025 HOLTWORK LLC. Patents Pending."

from .parse import encode, decode, memopr
from .sql import select, selectify, insert
from .app import dbget, dbadd