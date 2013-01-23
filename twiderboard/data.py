#  ConfigParser loads the configuration file containing
# all inforamation that will be used by other modules

from ConfigParser import SafeConfigParser
import os


parser = SafeConfigParser()
# ini file should be located one folder up from data module (in main repo)
ini_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'basic.ini')
parser.read(ini_path)

# Base :
engine_base = parser.get('base', 'engine')
engine_encoding = parser.get('base', 'encoding')

engine_url = engine_base
if len(engine_encoding) > 0:
    engine_url = engine_url + '?' + engine_encoding
print engine_url

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
oauth = parser.get('keys', 'oauth_id')
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
