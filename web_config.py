import os, argparse, hashlib
from web_utils import *

def get_args():
    parser = argparse.ArgumentParser(description='IC')
    parser.add_argument('--https', action='store_true', default=False)
    parser.add_argument('--public', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--ftp', type=str, default='files')
    parser.add_argument('-p', '--port', type=int, default=7777)
    return parser.parse_args()

class Config(object):
    def __init__(self):
        self.args = get_args()
        self.host = '0.0.0.0' if self.args.public else '127.0.0.1'
        self.port = self.args.port
        self.debug = self.args.debug
        self.static_folder = 'static'
        self.static_url_path = ''
        self.secret_key = os.urandom(16)

        self.params = {}


        self.ftp_path = os.path.abspath(self.args.ftp)
        self.ftp_link = os.path.join(self.static_folder, 'ftp')
        
        mkdir(self.ftp_path)
        remove(self.ftp_link)
        os.system('ln -s %s %s' % (self.ftp_path, self.ftp_link))


        self.key = hashlib.md5(os.urandom(16)).hexdigest()[:16]\
                if not self.args.debug else ''


        if self.args.https:
            self.https()
            self.params['ssl_context'] = (
                './certificate/server-cert.pem',
                './certificate/server-key.pem',
            )


    def https(self):
        path = 'certificate'
        pub = 'server-cert.pem'
        pri = 'server-key.pem'
        
        if not (os.path.isfile(os.path.join(path, pub)) and\
                os.path.isfile(os.path.join(path, pri))):
            os.system('./certificate/cert.sh')
        




cfg = Config()
