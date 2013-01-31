#  ConfigParser loads the configuration file containing
# all inforamation that will be used by other modules

from ConfigParser import SafeConfigParser
import os
import sys

parser = SafeConfigParser()
# ini file should be located one folder up from data module (in main repo)
ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'basic.ini')

# checking whether file exists
print "Checking ini file in : %s" % (ini_path)
if not os.path.exists(ini_path):
    print "Ini file not found. Exiting!"
    sys.exit(0)

parser.read(ini_path)

# Base :
engine_base = parser.get('base', 'engine')
engine_encoding = parser.get('base', 'encoding')

engine_url = engine_base
if len(engine_encoding) > 0:
    engine_url = engine_url + '?' + engine_encoding

root = parser.get('base', 'root')

# Log
deb = parser.get('log', 'debug')
if deb != 'True':
    debug = False
else:
    debug = True
log_name = parser.get('log', 'name')
log_path = os.path.join(root, log_name)

# Keys
oa = parser.get('keys', 'oauth_id')
if oa != 'True':
    oauth = False
else:
    oauth = True
keys_root = parser.get('keys', 'root')
oauth_name = parser.get('keys', 'oauth')
basic_name = parser.get('keys', 'basic')

oauth_keys = os.path.join(keys_root, oauth_name)
basic_keys = os.path.join(keys_root, basic_name)

# HTML
html_root = parser.get('html', 'root')
html = parser.get('html', 'html')
tmpl = parser.get('html', 'tmpl')
html_file = os.path.join(html_root, html)
tmpl_file = os.path.join(html_root, tmpl)
