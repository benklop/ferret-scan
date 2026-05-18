import platform

_s = platform.system()


def is_linux():
    return _s == 'Linux'


def is_darwin():
    return _s == 'Darwin'


def is_windows():
    return _s == 'Windows'


def is_wx28():
    import wx

    return wx.__version__.startswith('2.8')


def is_wx30():
    import wx

    return wx.__version__.startswith('3.0')
