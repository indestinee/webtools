from web_utils import *
from ftp import *
from spider import *

init_session = {
    'msg': [],
    'user': None,
}

@app.route('/', methods=['GET', 'POST'])# {{{
@app.route('/index', methods=['GET', 'POST'])
def index():
    for key, value in init_session.items():
        if key not in session:
            session[key] = value
    return html(cur='index')
# }}}

@app.route('/login', methods=['GET', 'POST'])
def _login_():
    return login()

if __name__ == '__main__':
    print()
    print('    ' + '-' * 32)
    print('    >>  %s://%s:%s/login?code=%s' % (
        'https' if cfg.args.https else 'http', 
        cfg.host,
        cfg.port,
        cfg.key
    ))
    with open('key.txt', 'w') as f:
        f.write('%s\n'%cfg.key)
    print('    >>  code: %s' % cfg.key)
    print('    ' + '-' * 32)
    print()
    app.run(host=cfg.host, port=cfg.port, debug=cfg.debug, **cfg.params)



