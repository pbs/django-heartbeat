import socket
import psutil
from datetime import datetime
from django.template.defaultfilters import filesizeformat, timesince


ips = []
for nic, addrs in psutil.net_if_addrs().items():
    for addr in addrs:
        if(socket.AF_INET is addr.family and "127.0.0.1" not in addr.address):
            ips.append(addr.address)


def check(request):
    return {
            'hostname': socket.gethostname(),
            'ips': ips,
            'cpus': psutil.cpu_count(),
            'uptime': timesince(datetime.fromtimestamp(psutil.boot_time())),
            'memory': {
                'total': filesizeformat(psutil.virtual_memory().total),
                'available': filesizeformat(psutil.virtual_memory().available),
                'used': filesizeformat(psutil.virtual_memory().used),
                'free': filesizeformat(psutil.virtual_memory().free),
                'percent': psutil.virtual_memory().percent
            },
            'swap': {
                'total': filesizeformat(psutil.swap_memory().total),
                'used': filesizeformat(psutil.swap_memory().used),
                'free': filesizeformat(psutil.swap_memory().free),
                'percent': psutil.swap_memory().percent
            }
        }
