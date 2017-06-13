import re
import requests
import urllib
from video_format import FORMAT
import urlparse

def get_info(url, video_id, meta_info=None):
    #print 'ws get_info, url = %s'%url
    headers = {'Host': 'manifest.googlevideo.com',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
               'Accept': '*/*',
               'DNT': '1',
               'Referer': 'https://www.youtube.com/watch?v=%s' % video_id,
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}
    result = requests.get(url, headers=headers, allow_redirects=True)
    lines = result.text.splitlines()

    _meta_info = {'video': {},
                  'channel': {},
                  'images': {},
                  'subtitles': []}
    meta_info = meta_info if meta_info else _meta_info
    dash =     {'url': url, 'sort':[4000, 0]}
    streams = [dash]
    re_line = re.compile(r'RESOLUTION=(?P<width>\d+)x(?P<height>\d+)')
    re_itag = re.compile(r'/itag/(?P<itag>\d+)')
    for i in range(len(lines)):
        re_match = re.search(re_line, lines[i])
        if re_match:
            line = lines[i + 1]

            re_itag_match = re.search(re_itag, line)
            if re_itag_match:
                itag = re_itag_match.group('itag')
                if __name__ == '__main__':
                    print 'itag = ', itag
                yt_format = FORMAT.get(itag, None)
                if not yt_format:
                    raise Exception('unknown yt_format for video id %s itag "%s" line %s' % (video_id, itag, line))

                width = int(re_match.group('width'))
                height = int(re_match.group('height'))
                video_stream = {'url': line,
                                'meta': meta_info}
                if __name__ == '__main__':
                    print 'video_stream before = ', video_stream
                video_stream.update(yt_format)
                if __name__ == '__main__':
                    print 'video_stream after = ', video_stream
                streams.append(video_stream)
                #print 'streams = ', streams
                pass
            pass
        pass
    return streams

def watch(video_id, reason=u'', meta_info=None):
    if __name__ == '__main__':
        print 'ws - watch'
    headers = {'Host': 'www.youtube.com',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
               'Accept': '*/*',
               'DNT': '1',
               'Referer': 'https://www.youtube.com',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

    params = {'v': video_id,
              'hl': 'en-US',
              'gl': 'US'}

    url = 'https://www.youtube.com/watch'

    result = requests.get(url, params=params, headers=headers, verify=True, allow_redirects=True)
    html = result.text

    pos = html.find('ytplayer.config')
    if pos >= 0:
        html2 = html[pos:]
        pos = html2.find('</script>')
        if pos:
            html = html2[:pos]
            pass
        pass
    
    _meta_info = {'video': {},
                  'channel': {},
                  'images': {},
                  'subtitles': []}
    meta_info = meta_info if meta_info else _meta_info

    re_match_hlsvp = re.search(r'\"hlsvp\"[^:]*:[^"]*\"(?P<hlsvp>[^"]*\")', html)
    if re_match_hlsvp:
        hlsvp = urllib.unquote(re_match_hlsvp.group('hlsvp')).replace('\/', '/')
        #print('call get_info - url %s' %hlsvp)
        return get_info(hlsvp, video_id, meta_info=meta_info)


def get_video_streams(video_id):
    if __name__ == '__main__':
        print 'ws get_video_streams'

    video_streams = _method_get_video_info(video_id)
    if not isinstance(video_streams, list):
        # try again
        video_streams = _method_get_video_info(video_id)
        if not isinstance(video_streams, list):
            return []
    
    # update title
    for video_stream in video_streams:
        if __name__ == '__main__':
            print video_stream
        if 'title' in video_stream:
            title = '[B]%s[/B] (%s;%s / %s@%d)' % (
                video_stream['title'], video_stream['container'], video_stream['video']['encoding'],
                video_stream['audio']['encoding'], video_stream['audio']['bitrate'])
            video_stream['title'] = title
        pass

    def _sort_stream_data(_stream_data):
        return _stream_data.get('sort', 0)
    
    video_streams = sorted(video_streams, key=_sort_stream_data, reverse=True)

    return video_streams

def _method_get_video_info(video_id):
    if __name__ == '__main__':
        print 'ws - _method_get_video_info'
    headers = {'Host': 'www.youtube.com',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
               'Accept': '*/*',
               'DNT': '1',
               'Referer': 'https://www.youtube.com/tv',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}
    params = {'video_id': video_id,
              'hl': 'en-US',
              'gl': 'US',
              'eurl': 'https://youtube.googleapis.com/v/' + video_id,
              'ssl_stream': '1',
              'ps': 'default',
              'el': 'default'}

    url = 'https://www.youtube.com/get_video_info'

    result = requests.get(url, params=params, headers=headers, verify=True, allow_redirects=True)

    stream_list = []

    data = result.text
    params = dict(urlparse.parse_qsl(data))

    meta_info = {'video': {},
                 'channel': {},
                 'images': {},
                 'subtitles': []}
    meta_info['video']['id'] = params.get('vid', params.get('video_id', ''))
    meta_info['video']['title'] = params.get('title', '')
    meta_info['channel']['author'] = params.get('author', '')
    try:
        meta_info['video']['title'] = meta_info['video']['title'].decode('utf-8')
        meta_info['channel']['author'] = meta_info['channel']['author'].decode('utf-8')
    except:
        pass
    meta_info['channel']['id'] = 'UC%s' % params.get('uid', '')
    image_data_list = [
        {'from': 'iurlhq', 'to': 'high'},
        {'from': 'iurlmq', 'to': 'medium'},
        {'from': 'iurlsd', 'to': 'standard'},
        {'from': 'thumbnail_url', 'to': 'default'}]
    for image_data in image_data_list:
        image_url = params.get(image_data['from'], '')
        if image_url:
            meta_info['images'][image_data['to']] = image_url
            pass
        pass

    if params.get('status', '') == 'fail':
        return watch(video_id, reason=params.get('reason', 'UNKNOWN'), meta_info=meta_info)

    if params.get('live_playback', '0') == '1':
        url = params.get('hlsvp', '')
        if url:
            if __name__ == '__main__':
                print 'url from hlsvp %s' %url
            return get_info(url, video_id, meta_info=meta_info)
        pass

if __name__ == '__main__':
#    videoids = eval(open('videoids').read())
#    print (len(videoids))
#    for video_id in videoids :
    video_id ='EeCQQnRoccU'
#    url = 'https://www.youtube.com/get_video_info'
#        print('processing video id %s' %video_id)
    info = get_video_streams(video_id)
    print(info[0]['url'])
