from web import *
from crawl.spider import Spider
from crawl.html_lib import url_analysis, fix_url, add_prefix


spiders = {}

headers_keys = [
    'Accept', 'Accept-Encoding', 'Accept-Language', 'Cache-Control', 'Connection', 'User-Agent']
@app.route('/spider', methods=['GET', 'POST'])# {{{
def spider():
    if 'spider' not in session:
        spider = Spider(headers={key: request.headers[key] for key in headers_keys if key in request.headers}, encoding='utf-8')
        session['spider'] = id(spider)
        spiders[id(spider)] = spider

    spider = spiders[session['spider']]
    default_url = 'https://baidu.com'
    url = request.form.get('url', default_url)
    if url == default_url:
        url = request.args.get('url', default_url)
    protocol, host = url_analysis(url)[1][:2]
    content = add_prefix(fix_url(spider.get(url).text, protocol, host),\
            '/spider?url=')
    _html = html(name='spider.html', cur='spider', url=url)
    return _html + content

# }}}
