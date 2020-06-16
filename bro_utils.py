import re
import shutil
import os

from random import getrandbits

from flask import Request, render_template

from paths import APP_DIR
from configuration import read_config
config = read_config()

def render_template_themed(name, **kwargs):
    return render_template(os.path.join(config['template'], name).replace("\\", "/"), **kwargs)

def get_real_ip(request):
    try:
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        elif request.headers.getlist("X-Real-Ip"):
            ip = request.headers.getlist("X-Real-Ip")[0]
        else:
            ip = request.remote_addr
        return ip
    except:
        return "0.0.0.0"


def camelCaseSplit(text):
    """
    This function splits camel case into separate words
    :param text: Input text
    :return: array of words
    """
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', text)
    return [m.group(0) for m in matches]

def grouped(l, n):
    # Yield successive n-sized chunks from l.
    for i in range(0, len(l), n):
        yield l[i:i + n]

class ProxiedRequest(Request):
    def __init__(self, environ, populate_request=True, shallow=False):
        super(Request, self).__init__(environ, populate_request, shallow)
        # Support SSL termination. Mutate the host_url within Flask to use https://
        # if the SSL was terminated.
        x_forwarded_proto = self.headers.get('X-Forwarded-Proto')
        if x_forwarded_proto == 'https':
            self.url = self.url.replace('http://', 'https://')
            self.host_url = self.host_url.replace('http://', 'https://')
            self.base_url = self.base_url.replace('http://', 'https://')
            self.url_root = self.url_root.replace('http://', 'https://')


def disk_usage():
    '''
    BRO
    Returns disk usage in bytes in a form of a list (total, used, free)
    '''
    return shutil.disk_usage(APP_DIR)

def human_readable_bytes(num, suffix='B'):
    '''
    BRO
    Converts bytes into
    '''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def media_numbered_name(base_name, filter_model):
    i = 0
    found = False
    while not found:
        i += 1
        new_name = "{}_{}".format(base_name, str(i).zfill(3))
        check = filter_model.select().where(filter_model.name == new_name)
        if not check:
            found = True
            return new_name



def random_string(length=30):
    return '%0x' % getrandbits(length * 4)

def random_image_name(filename, data=None):
    existing = []
    for f in os.listdir(APP_DIR):
        name, ext = os.path.splitext(f)
        existing.append(name)
    name, ext = os.path.splitext(filename)
    while True:
        new_name = random_string()
        if new_name not in existing:
            return new_name+ext

