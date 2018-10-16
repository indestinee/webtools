from web import *

from crawl.spider import Spider
_spider = Spider(headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8', 'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'})

@app.route('/delete', methods=['GET'])# {{{
def delete():
    if not check():
        return redirect(url_for('index'))
    path = simplify_path(request.args.get('path', ''))
    local_path = os.path.join(cfg.ftp_path, path)
    file_type = exist(local_path)
    if file_type == 2:
        remove_dirs(local_path)
        if path == '':
            mkdir(cfg.ftp_path)
    if file_type == 1:
        if os.path.islink(local_path):
            os.unlink(local_path)
        else:
            os.remove(local_path)
    return redirect(url_for('ftp', path=url_parent_directory(path)))
# }}}

@app.route('/new', methods=['GET', 'POST'])# {{{
def new_file():
    if not check():
        return redirect(url_for('index'))
    path = simplify_path(request.args.get('path', ''))
    filename = legal(request.form.get('filename', ''))
    filepath = os.path.join(path, filename)
    local_path = os.path.join(cfg.ftp_path, filepath)
    dir_local = os.path.dirname(local_path)
    if exist(local_path) > 0:
        session['msg'] += ['[ERR] file exists']
        return redirect(url_for('ftp', path=path))
    elif exist(dir_local) != 2:
        session['msg'] += ['[ERR] parent directoryfolder error']
        return redirect(url_for('ftp', path=path))
    return redirect(url_for('edit', path=filepath))
# }}}

@app.route('/edit', methods=['GET', 'POST'])# {{{
def edit():
    if not check():
        return redirect(url_for('index'))
    path = simplify_path(request.args.get('path', ''))
    local_path = os.path.join(cfg.ftp_path, path)
    dirname = url_parent_directory(path)
    filename = os.path.basename(local_path)
    file_type = exist(local_path)
    if file_type == 1:
        sz = os.stat(local_path).st_size
        if sz > 65536:
            session['msg'] += ['[ERR] the size of file is too large']
            return redirect(url_for('ftp', path=dirname))
        else:
            with open(local_path, 'rb') as f:
                data = f.read()
            try:
                encoding = chardet.detect(data)['encoding']
                if not encoding:
                    encoding = 'utf-8'
                content = data.decode(encoding=encoding)
            except:
                session['msg'] += ['[ERR] cannot found suitable encoding for the file!']
                return redirect(url_for('ftp', path=dirname))
            return html(cur='edit', path=path, filename=filename,\
                    name='edit.html', content=content,\
                    dirname=dirname, encoding=encoding,\
                    path_tree=get_path_tree(dirname))
    elif file_type == 0 and exist(os.path.dirname(local_path)) == 2:
        return html(cur='edit', path=path, filename=filename,\
                name='edit.html', content='',\
                dirname=dirname, encoding='utf-8',\
                path_tree=get_path_tree(dirname))
    else:
        return redirect(url_for('ftp', path=dirname))
# }}}

@app.route('/submit', methods=['GET', 'POST'])# {{{
def save():
    if not check():
        return redirect(url_for('index'))
    path = simplify_path(request.form.get('path', ''))
    content = request.form.get('content', '')
    encoding = request.form.get('encoding', 'utf-8')

    try:
        local_path = os.path.join(cfg.ftp_path, path)
        with open(local_path, 'w', encoding=encoding) as f:
            f.write(content)
        session['msg'] += ['[SUC] save successfully!']
    except:
        session['msg'] += ['[ERR] failed! found illegal character!']
    return redirect(url_for('edit', path=path))
# }}}

@app.route('/mkdir', methods=['GET', 'POST'])# {{{
def remote_mkdir():
    if not check():
        return redirect(url_for('index'))
    path = simplify_path(request.args.get('path', ''))
    dirname = legal(request.form.get('dirname', ''))
    filename = simplify_path(os.path.join(path, dirname))
    local_path = os.path.join(cfg.ftp_path, filename)
    if mkdir(local_path):
        session['msg'] += ['[SUC] mkdir successfully!']
    else:
        session['msg'] += ['[ERR] file exist or name ilegal']
    return redirect(url_for('ftp', path=path))
# }}}

@app.route('/download', methods=['GET'])# {{{
def download():
    # if not check():
    #     return redirect(url_for('index'))
    path = simplify_path(request.args.get('path', ''))
    local_path=os.path.join(cfg.ftp_path, path)
    file_type = exist(local_path)
    if file_type == 2:
        session['msg'] += ['[ERR] cannot download a folder']

    if file_type == 1:
        return make_response(send_from_directory(
            os.path.dirname(local_path), 
            os.path.basename(local_path),
            as_attachment=True
        ))
    return redirect(url_for('ftp', path=path))
# }}}

@app.route('/upload', methods=['GET', 'POST'])# {{{
def upload():
    if not check():
        return redirect(url_for('index'))
    path = simplify_path(request.form.get('path', ''))
    local_path = os.path.join(cfg.ftp_path, path)
    if 'file' in request.files:
        file = request.files['file']
        file_path = os.path.join(
            local_path, 
            simplify_path(file.filename),
        )
        try:
            file.save(file_path)
            session['msg'] += ['[SUC] upload successfully']
        except:
            session['msg'] += ['[ERR] uploading failed']
    elif 'url' in request.form:
        url = request.form.get('url', '')
        response = _spider.get(url)
        file_path = os.path.join(
            local_path, 
            simplify_path(url.split('/')[-1]),
        )
        print(url, file_path)
        if response:
            try:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                session['msg'] += ['[SUC] upload successfully']
            except:
                pass
    else:
        session['msg'] += ['[WRN] no file selected']
    return redirect(url_for('ftp', path=url_parent_directory(path)))
# }}}

@app.route('/ftp') # {{{
@app.route('/ftp', methods=['GET'])
def ftp():
    # if not check():
    #     return redirect(url_for('index'))
    path=simplify_path(request.args.get('path', ''))
    local_path=os.path.join(cfg.ftp_path, path)
    if exist(local_path) != 2:
        session['msg'] += ['[ERR] no such path']
        return redirect(url_for('ftp', path=url_parent_directory(path)))
    
    files = [{
        'name': f, 'type': exist(os.path.join(local_path, f)), 'path': os.path.join(path, f),
        'info': file_info(os.path.join(local_path, f)), 'protect': False,
    } for f in get_items(local_path)]

    defaults = [{
        'name': '..', 'type': 2, 'path': '%s/..'%path,
        'info': ['Time', 'Size', 0], 'protect': True,
    }, {
        'name': '.', 'type': 2, 'path': '%s'%path,
        'info': file_info(local_path), 'protect': False,
    }]
    files.sort(key=lambda x: [-x['type'], x['name']])
    files = defaults + files

    return html(name='ftp.html', cur='ftp', files=files, root=path, path_tree=get_path_tree(path))
# }}}

