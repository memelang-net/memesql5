#!/usr/bin/env python3

__version__ 	= "5.0.12"
__title__		= "memesql"
__summary__		= "A compact graph-relational query language"
__uri__			= "https://memelang.net/"
__author__		= "Bri Holt"
__email__		= "info@memelang.net"
__copyright__	= "© 2025 HOLTWORK LLC. Patents Pending."

from .parse import *
from .app import dbget, dbadd