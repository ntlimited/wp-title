# config handler for wp_title. Supplies defaults but allows overriding
# via ~/.config/wp_title.conf

import ConfigParser
import os

parser = ConfigParser.RawConfigParser()
# default initialization - these probably aren't what anyone but
# the author wants :)
parser.add_section('storage')
parser.set('storage', 'root', '/media/media/TV')
parser.set('storage', 'anime', './Anime')

parser.read([os.path.expanduser('~/.config/wp_title.conf')])

def override_config(path):
    parser.read([path])

def get(section, key):
    global parser

    return parser.get(section, key)
