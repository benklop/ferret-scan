"""Python 2/3 compatibility shims for Horus."""

import sys

if sys.version_info[0] >= 3:
    import builtins
    import collections.abc
    import types

    builtins.unicode = str
    builtins.xrange = range

    import collections

    collections.MutableMapping = collections.abc.MutableMapping

    types.BooleanType = bool
    types.IntType = int
    types.FloatType = float
    types.UnicodeType = str
    types.ListType = list
    types.StringType = str
    types.DictType = dict
