from flask import Flask, render_template, redirect,\
        url_for, request, session,\
        send_from_directory, make_response
import shutil, chardet, os, time


def exist(path):# {{{
    path = os.path.realpath(path)
    if os.path.isfile(path):
        return 1
    if os.path.isdir(path):
        return 2
    return 0
# }}}
def get_items(path):# {{{
    return os.listdir(path)
# }}}
def mkdir(path):# {{{
    if not os.path.isdir(path) and not os.path.isfile(path):
        os.makedirs(path)
        return True
    return False
# }}}
def remove(path):# {{{
    if os.path.islink(path):
        os.unlink(path)
        return True
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False
# }}}
def remove_dirs(path):# {{{
    if os.path.islink(path):
        os.unlink(path)
        return True
    elif os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False
# }}}
def is_prefix(target, prefix):# {{{
    return target[:len(prefix)] == prefix
# }}}
def is_suffix(target, suffix):# {{{
    return target[-len(suffix):] == suffix
# }}}
def simplify_path(path):# {{{
    dirs = path.split('/')
    rets = []
    for each in dirs:
        if each == '.' or each == '':
            continue
        elif each == '..':
            rets = rets[:-1]
        else:
            rets.append(each)
    return '/'.join(rets)
# }}}
def url_parent_directory(path):
    if path.find('/') == -1:
        return ''
    return '/'.join(path.split('/')[:-1])
file_size_suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

def file_info(path):
    try:
        stat = os.stat(path)
    except:
        return ['????/??/?? ??:??:??', '?? B', -1]
    size = stat.st_size
    cnt = 0
    while size > 1024:
        size /= 1024
        cnt += 1
    
    t = time.strftime("%Y/%m/%d %H:%M:%S",\
            time.localtime(stat.st_ctime))
    return [t, '%.2f %s' % (size, file_size_suffix[cnt]), stat.st_size]
        
def get_path_tree(path):
    sub_path = path.split('/')
    path_tree = []
    prefix = ''
    if path != '':
        for each in sub_path:
            prefix = '/'.join([prefix, each])
            path_tree.append([each, prefix])
    return path_tree

def legal(name):
    name = name.replace('/', '|')
    if name == '..':
        name = '__'
    if name == '.':
        name = '_'
    return name
