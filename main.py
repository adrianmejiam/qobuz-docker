import os
import os.path
import logging
import requests
import shutil
import uuid
import re
from io import StringIO

import cherrypy
from cherrypy.lib import static
from qobuz_dl.core import QobuzDL

# Default Variables
TMP_DIR = '/tmp/qobuz/'

# Initialize the logs
log_stream = StringIO()
log_handler = logging.StreamHandler(log_stream)
logger = logging.getLogger('qobuz_dl')
logger.setLevel(logging.DEBUG)
for handler in logger.handlers:
    logger.removeHandler(handler)
logger.addHandler(log_handler)


# Initialize Qobuz object
qobuz = QobuzDL(quality=7, directory=TMP_DIR)


# Clean TMP Directory
def clean_tmp_dir():
    # Set tmp folder
    folder = TMP_DIR
    if "TMPDIR" in os.environ:
        folder = os.environ['TMPDIR']

    # Delete everything in the TMP folder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


# Create Zip file from directory
def make_archive(source, destination):
    name = destination.split('.')[0]
    format = os.path.basename(destination).split('.')[1]
    shutil.make_archive(name,
                        format,
                        root_dir=source)


# Format the input url as https://play.qobuz.com/album/ALBUM_ID
def handle_album_url(url):
    url_1 = re.match(r'^https?://w?w?w?\.qobuz\.com/.*/album\/.*\/(.*)$', url)
    url_2 = re.match(r'^http?s://play\.qobuz\.com\/album/(.*)$', url)

    if url_1:
        qobuz_url = 'https://play.qobuz.com/album/' + url_1.group(1)
    elif url_2:
        qobuz_url = 'https://play.qobuz.com/album/' + url_2.group(1)
    else:
        qobuz_url = ''
        logger.error('Only Albums can be downloaded.')

    return qobuz_url


# Generate Random String
def my_random_string(string_length=5):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-", "")
    return random[0:string_length]


# Initialize Qobuz Object
def init_qobuz(email, password):
    # Set the password and email
    if not email:
        email = os.environ['QOBUZNAME']
    if not password:
        password = os.environ['QOBUZPASS']

    try:
        qobuz.get_tokens()  # get 'app_id' and 'secrets' attrs
        qobuz.initialize_client(email, password, qobuz.app_id, qobuz.secrets)
    except:
        logger.error('Wrong Credentials')


# Serve index.html
class Stringdownload(object):
    @cherrypy.expose
    def index(self):
        return open('index.html')


# /download : Download music to server, returns logs
@cherrypy.expose
class DownloadService(object):

    @cherrypy.tools.accept(media='text/plain')
    def POST(self, url='', quality='', email='', password=''):
        # Reset Logs
        log_stream.truncate(0)

        try:
            # Intialize Qobuz
            init_qobuz(email, password)

            # Set wanted quality
            qobuz.quality = quality

            # Set the Download Directory
            if "DOWNLOADDIR" in os.environ:
                qobuz.directory = os.environ['DOWNLOADDIR']
            else:
                qobuz.directory = TMP_DIR

            # Verify that the url is correct
            qobuz_url = handle_album_url(url)

            if qobuz_url:
                # Download the music
                qobuz.handle_url(qobuz_url)

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


# /downloadzip : Download music and make .zip file
# returns logs and link to .zip file
@cherrypy.expose
class DownloadZipService(object):

    # Download Music and Create Zip File
    @cherrypy.tools.accept(media='text/plain')
    def POST(self, url='', quality='', email='', password=''):
        # Generate a random string for the folder and zip file
        dirname = my_random_string()

        # Reset Logs
        log_stream.truncate(0)

        try:
            # Intialize Qobuz
            init_qobuz(email, password)

            # Set wanted quality
            qobuz.quality = quality

            # Set TMP Directory
            if "TMPDIR" in os.environ:
                if os.environ['TMPDIR'][-1] == "/":
                    qobuz.directory = os.environ['TMPDIR'] + dirname
                else:
                    qobuz.directory = os.environ['TMPDIR'] + "/" + dirname
            else:
                qobuz.directory = TMP_DIR + dirname

            # Verify that the url is correct
            qobuz_url = handle_album_url(url)

            if qobuz_url:
                # Download the music
                qobuz.handle_url(qobuz_url)
                logger.info('Downloaded')

                # Make a .Zip file of the downloaded directory
                make_archive(qobuz.directory, TMP_DIR + dirname + '.zip')

                # Make <a> link in the log
                logger.info('<a href="/downloadzip?file=' + dirname + '">Download .Zip file</a>')
        except:
            logger.error('Error while downloading.')

        # Return the logs
        return log_stream.getvalue()

    # Get the created Zip File
    @cherrypy.tools.accept(media='text/plain')
    def GET(self, file=''):
        # Get the filename
        if "TMPDIR" in os.environ:
            if os.environ['TMPDIR'][-1] == "/":
                zipfile = os.environ['TMPDIR'] + file + '.zip'
            else:
                zipfile = os.environ['TMPDIR'] + "/" + file + '.zip'
        else:
            zipfile = TMP_DIR + file + '.zip'

        # Returns the .zip file
        return static.serve_file(zipfile, 'application/x-download',
                                 'attachment', os.path.basename(zipfile))


# /clean : Clean the TMP directory
@cherrypy.expose
class CleanService(object):

    # Clean TMP folder
    @cherrypy.tools.accept(media='text/plain')
    def POST(self, url='', quality='', email='', password=''):
        # Reset Logs
        log_stream.truncate(0)

        try:
            logger.info('Cleaning TMP directory...')
            clean_tmp_dir()
            logger.info('Cleaned TMP directory')
        except:
            logger.error('Failed to clean TMP directory')
        return log_stream.getvalue()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/download': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/downloadzip': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/clean': {
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
    webapp.download = DownloadService()
    webapp.downloadzip = DownloadZipService()
    webapp.clean = CleanService()

    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'engine.autoreload.on': False})

    cherrypy.quickstart(webapp, '/', conf)
