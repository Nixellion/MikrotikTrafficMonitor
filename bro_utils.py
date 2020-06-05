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

from PIL import Image

def resize_and_crop(img, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.
    args:
        img_path: path for the image to resize.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.
    """
    # Get current and desired ratio for the images
    size = [int(size[0]), int(size[1])]
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], int(size[0] * img.size[1] / img.size[0])),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (int(img.size[1] - size[1]) / 2), int(img.size[0]), int((img.size[1] + size[1]) / 2))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((int(size[1] * img.size[0] / img.size[1]), size[1]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (int((img.size[0] - size[0]) / 2), 0, int((img.size[0] + size[0]) / 2), int(img.size[1]))
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
                Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    return img


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

