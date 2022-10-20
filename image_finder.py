"""Markdown extension to faciliate embedding of images"""
import sys
from collections import defaultdict
import os, os.path
import re
from markdown import markdownFromFile, Extension
import xml.etree.ElementTree as ET
from markdown.inlinepatterns import SimpleTagPattern
from markdown.treeprocessors import Treeprocessor
from shutil import copyfile

from PIL import Image, ImageOps

def resize(src, dest, width, height):
    image = Image.open(src)
    if width:
        if height:
            factor = min(width/image.width, height/image.height)
        else:
            factor = width/image.width
    else:
        if height:
            factor = height/image.height
        else:
            factor = 1
    if factor < 1:
        resized = ImageOps.scale(image, factor)
        resized.save(dest)
        return resized.width, resized.height
    else:
        copyfile(src, dest)
        return image.width, image.height

class _ImageFinder(Treeprocessor):

    def __init__(self, config, images):
        self.config = config
        self.images = images

    def run(self, root):
        for ch in root.iter():
            if ch.tag == 'img':
                img_code = ch.get('src')
                basename, _, opt = img_code.partition(':')
                ma = re.match('([wh])([0-9]+)|([0-9])+x([0-9]+)', opt)
                width = 0
                height = 0
                if ma:
                    g = ma.groups()
                    if g[0] == 'h':
                        height = int(g[1])
                    elif g[0] == 'w':
                        width = int(g[1])
                    else:
                        width, height = int(g[2]), int(g[3])
                else:
                    width = self.config['width'][0]
                    height = self.config['height'][0]
              
                paths = self.images.get(basename)
                if paths:
                    src = paths[0]
                    if len(paths) > 1:
                        sys.stderr.write('ImageFinder: using %s\n' % src)
                    _, ext = os.path.splitext(src)
                    dest = basename + '_.' + ext
                    width, height = resize(src, dest, width, height)
                    ch.set('src', dest)
                    ch.set('width', str(width))
                    ch.set('height', str(height))
                else:
                    sys.stderr.write('ImageFinder: No file for \n' %
                                     basename)

class ImageFinder(Extension):
    """Markdown extension to graft included images from the file system,
    copy them (after optional scaling) into the working dir, and
    insert width and height attributres into the <img> tag."""

    default_config = {
        'image_dir': '.',
        'width' : 0,
        'height': 0
        }

    def __init__(self, **kw):
        super().__init__(**kw)
        
        self.images = defaultdict(list)
        for k, v in self.default_config.items():
            if not k in self.config:
                self.config[k] = [v, k]
        for root, _, files in os.walk(self.config['image_dir'][0]):
            for f in files:
                b, e = os.path.splitext(f)
                if e.lower() in ('jpg', 'png', 'gif'):
                    self.images[b].append(os.path.join(root, f))

    def extendMarkdown(self, md):
        md.treeprocessors.register(_ImageFinder(self.config, self.images),
                                   'image_finder', 3)

def makeExtension(**kw):
    return ImageFinder(**kw)
