from web_utils import *
from web_config import cfg

app = Flask(__name__, static_folder=cfg.static_folder, static_url_path=cfg.static_url_path)
app.config['SECRET_KEY'] = cfg.secret_key

functions = {# {{{
    'ftp': 'FTP',
    'spider': 'Spider',
}# }}}

def check():# {{{
    if 'user' in session and session['user']:
        return True
    session['msg'] = ['[WRN] this module requires an authorization']
    return False
# }}}

def html(name='index.html', **kwargs):# {{{
    if 'msg' not in session:
        session['msg'] = []
    if 'user' not in session:
        session['user'] = None
    kwargs.update({
        'msg': session['msg'].copy(),
        'functions': functions,
        'login': session['user'] 
    })
    session['msg'] = []
    return render_template(name, **kwargs)
# }}}

def login():# {{{
    code1 = request.args.get('code', '')
    code2 = request.form.get('code', '')
    if code1 == cfg.key or code2 == cfg.key:
        session['user'] = 'user'
        session['msg'] = ['[SUC] login successfully']
    elif code1 != '' or code2 != '':
        session['msg'] = ['[ERR] wrong code']
        session['user'] = None
    return redirect(url_for('index'))
# }}}
