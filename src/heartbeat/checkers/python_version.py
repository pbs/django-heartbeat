import sys


def check(request):
    return {
            'version': '{major}.{minor}.{micro}'.format(
                major=sys.version_info.major,
                minor=sys.version_info.minor,
                micro=sys.version_info.micro
            ),
            'info': sys.version,
            'executable': sys.executable,
            'platform': sys.platform
        }
