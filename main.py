import os
import os.path
import logging
from io import StringIO
import cherrypy
from qobuz_dl.core import QobuzDL
import requests

# Initialize the logs
log_stream = StringIO()
log_handler = logging.StreamHandler(log_stream)
logger = logging.getLogger('qobuz_dl')
logger.setLevel(logging.DEBUG)
for handler in logger.handlers:
    logger.removeHandler(handler)
logger.addHandler(log_handler)

# Set the Download Directory
if "DOWNLOADDIR" in os.environ:
    qobuz = QobuzDL(quality=7, directory=os.environ['DOWNLOADDIR'])
else:
    qobuz = QobuzDL(quality=7, directory='/downloads')


def init_qobuz(email, password):
    if not email:
        email = os.environ['QOBUZNAME']
    if not password:
        password = os.environ['QOBUZPASS']

    try:
        qobuz.get_tokens()  # get 'app_id' and 'secrets' attrs
        qobuz.initialize_client(email, password, qobuz.app_id, qobuz.secrets)
    except:
        logger.error('Wrong Credentials')


class Stringdownload(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')


@cherrypy.expose
class StringdownloadWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def POST(self, url='', quality='', email='', password=''):
        # Reset Logs
        log_stream.truncate(0)
        try:
            # Intialize Qobuz
            init_qobuz(email, password)
            # Set wanted quality
            qobuz.quality = quality

            # Download the music
            qobuz.handle_url(url)
            logger.info('Downloaded')

            # Update Jellyfin if environment variables are used
            if "JELLYFINURL" in os.environ and "JELLYFINTOKEN" in os.environ:
                requests.post(os.environ['JELLYFINURL'],
                              headers={'X-MediaBrowser-Token':
                                       os.environ['JELLYFINTOKEN']})
                logger.info('Jellyfin Updated')
        except:
            logger.error('Error while downloading.')

        # Return the logs
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
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(webapp, '/', conf)
