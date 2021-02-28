import os, os.path
import logging
from io import StringIO
import cherrypy
from qobuz_dl.core import QobuzDL

email = os.environ['QOBUZNAME']
password = os.environ['QOBUZPASS']

log_stream = StringIO()
log_handler = logging.StreamHandler(log_stream)
logger = logging.getLogger('qobuz_dl')
logger.setLevel(logging.INFO)
for handler in logger.handlers:
    logger.removeHandler(handler)
logger.addHandler(log_handler)


qobuz = QobuzDL(quality=7, directory='/downloads')
qobuz.get_tokens() # get 'app_id' and 'secrets' attrs
qobuz.initialize_client(email, password, qobuz.app_id, qobuz.secrets)

class Stringdownload(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')

@cherrypy.expose
class StringdownloadWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return cherrypy.session['mystring']

    def POST(self, url=''):
        log_stream.truncate(0)
        qobuz.handle_url(url)
        return log_stream.getvalue()

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/download': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'public'
        }
    }
    webapp = Stringdownload()
    webapp.download = StringdownloadWebService()
    cherrypy.quickstart(webapp, '/', conf)
