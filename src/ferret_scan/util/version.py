import json
import logging
import platform
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

from ferret_scan import __commit__, __datetime__, __version__
from ferret_scan.util import system as sys

logger = logging.getLogger(__name__)


class Version:
    def __init__(self, version):
        self.number = ''
        self.prenumber = ''
        for p in ['a', 'b', 'rc']:
            data = version.split(p)
            if len(data) == 2:
                self.number = data[0]
                self.prenumber = p + data[1]
        if self.prenumber == '':
            self.number = version
            self.prenumber = 'z'

    def __str__(self):
        return str(self.number) + str(self.prenumber)


current_version = Version(__version__)
current_datetime = __datetime__
current_commit = __commit__

latest_version = ''
latest_datetime = ''
latest_commit = ''

URL_API_RELEASES = 'https://api.github.com/repos/benklop/ferret-scan/releases/latest'
URL_DOWNLOAD = 'https://github.com/benklop/ferret-scan/releases/download/'


def _linux_distro_version_id():
    try:
        info = platform.freedesktop_os_release()
        return info.get('VERSION_ID', '') or info.get('VERSION', '')
    except (AttributeError, OSError):
        return ''


def download_lastest_data():
    global latest_version, latest_commit, latest_datetime
    try:
        f = urllib.request.urlopen(URL_API_RELEASES, timeout=1)
        content = json.loads(f.read())
        tag_name = content['tag_name']
        f = urllib.request.urlopen(URL_DOWNLOAD + tag_name + '/version', timeout=1)
        content = json.loads(f.read())
        latest_version = Version(content['version'])
        latest_datetime = content['datetime']
        latest_commit = content['commit']
    except Exception:
        logger.debug('Update check failed', exc_info=True)


def check_for_updates():
    return (
        latest_version != ''
        and latest_version.number >= current_version.number
        and latest_version.prenumber >= current_version.prenumber
        and current_datetime != ''
        and latest_datetime > current_datetime
    )


def _get_executable_url(version):
    url = None
    if sys.is_linux():
        url = URL_DOWNLOAD
        url += str(version)
        url += '/ferret-scan_'
        url += str(version)
        vid = _linux_distro_version_id()
        if vid:
            url += f'_{vid}'
        if platform.architecture()[0] == '64bit':
            url += '_amd64.AppImage'
        elif platform.architecture()[0] == '32bit':
            url += '_i386.AppImage'
        else:
            url += '.AppImage'
    elif sys.is_windows():
        url = URL_DOWNLOAD
        url += str(version)
        url += '/ferret-scan_'
        url += str(version) + '.exe'
    elif sys.is_darwin():
        url = URL_DOWNLOAD
        url += str(version)
        url += '/ferret-scan_'
        url += str(version) + '.dmg'
    return url


def download_latest_version():
    url = _get_executable_url(latest_version)
    if url is not None:
        webbrowser.open(url)
