#!/usr/bin/python
# -*- coding: utf-8 -*

# the following 3 import lines are required to support the youtube api request
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import re

if __name__ != '__main__':
    import xbmcgui
    import xbmc
    debug = 0

# access file tool
import os

# The following 3 lines are required to prevent unicode type failures when
# dealing with non-ascii names
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# the following are needed to perform youtube api requests
DEVELOPER_KEY               = "AIzaSyD0JUnZb6_ZHZcBfS_Q8hWw08yQ5Nr7iqk"
YOUTUBE_API_SERVICE_NAME    = "youtube"
YOUTUBE_API_VERSION         = "v3"


class YT_live():
    def __init__(self, cache, data):
        '''
        perform initial tasks upon construcing the class instance
        '''
        msg = "YT_live.__init__"
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)

        self.cache = cache
        self.data = data
        self.chans = {}             # initialize chans dict
        self.schans = {}            # initialize chans dict
        
        self.dump_chansdb()         # retrieve saved channel database
        self.dump_data()            # retrieve saved categories and chan names 
        
    def dump_data(self):
        '''
        dump channel data from stored cache
        '''
        self.data.table_name = 'WsLiveTV_data'
        
        # get categories
        cached_data = self.data.get('categories')
        if cached_data == '':
            import categories
            self.categories = categories.categories
        else:
            self.categories = eval(cached_data)
            msg = 'categories = %s'%self._repr_dict2(self.categories)
            xbmc.log(msg=msg,level=xbmc.LOGDEBUG)
            
        # get filter_pattern
        cached_filters = self.data.get('filters')
        if cached_filters == '':
            import categories
            self.filters = categories.filters
        else:
            self.filters = eval(cached_filters)
            msg = 'filters = %s'%self._repr_list(self.filters)
            xbmc.log(msg=msg,level=xbmc.LOGDEBUG)
        
        # get search_list    
        cached_search_list = self.data.get('search_list')
        if cached_search_list == '':
            import categories
            self.search_list = categories.search_list
        else:
            self.search_list = eval(cached_search_list)
            msg = 'search_list = %s'%self._repr_list(self.search_list)
            xbmc.log(msg=msg,level=xbmc.LOGDEBUG)

        # get exclusion list
        cached_excludes = self.data.get('excludes')
        if cached_excludes == '':
            import categories
            self.excludes = categories.excludes
        else:
            self.excludes = cached_excludes
            msg = 'excludes = %s'%self.excludes
            xbmc.log(msg=msg,level=xbmc.LOGDEBUG)
            
    def dump_chansdb(self):
        '''
        dump pickled chans db to schans dict
        '''

        msg = "YT_live.dump_chansdb, __debug__ %s" % __debug__
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)

        self.cache.table_name = 'WsLiveTV'
        cached_data = self.cache.get('chans')
        if cached_data == '':
            msg = "YT_live.dump_chansdb - No cache exists "
            try:
                print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)
            except:
                pass
            self.schans = {}
        else:
            msg = "YT_live.dump_chansdb - cache exists"
            try:
                print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)
            except:
                pass
            self.schans = eval(cached_data)
        return self.schans
    def update_chansdb(self):
        '''
        pickle chans
        '''
        
        msg = "YT_live.update_chansdb"
        try:
            print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)
        except:
            pass
        
        if not type(self.schans) is dict: raise AssertionError('saved channels is not dict format')
        msg = "YT_live.update_chansdb - " + str(self.schans)
        try:
            print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)
        except:
            pass
        self.cache.table_name = 'WsLiveTV'
        self.cache.set("chans", repr(self.schans))
        self.data.table_name = 'WsLiveTV_data'
        self.data.set("categories", repr(self.categories))
        self.data.set("filters", repr(self.filters))
        self.data.set("excludes", self.excludes)
        self.data.set("search_list", repr(self.search_list))
        
    def delete_db(self):
        '''
        delete chans database
        '''
        msg = "YT_live.delete_db"
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)
        
        self.cache.delete("chans")
        
        self.schans = {}
        self.update_chansdb()

    def update_schans(self, flush=False):
        '''
        update channels info in schans dict db with current live content
        Add new content, and remove old ones
        '''

        msg = "YT_live.update_schans"

        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGNOTICE)

        if flush:
            self.schans = self.chans
            self.update_chansdb()
            return

        if not debug:
            pDialog = xbmcgui.DialogProgressBG()
            pDialog.create('WS Live TV - Updating Channels')

        i = 0
        chans_count = len(self.chans)
        msg = "live channel count %d" % chans_count
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGNOTICE)
        
        if not type(self.schans) is dict: raise AssertionError('saved channels is not dict format, it is %s - %s' %(str(type(self.schans)), self.schans))
        schans_count = len(self.schans)

        msg = "Saved channel count %d %s" % (schans_count,type(self.schans))
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGNOTICE)
        
        for chan in self.chans:
            
            percentage = int(float(i) / chans_count * 100)
            if not debug: pDialog.update(percentage, 'updating %s' % self.chans[chan]['name'])
            
            # check if channel exists already in DB
            if chan not in self.schans:
                # channel does not exist in DB, copy it to schans
                i += 1
                self.schans[chan] = self.chans[chan]
                msg = self.schans[chan]['name'] \
                    + self.schans[chan]['label'] + ' New live channel, added'
                try:
                    print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGNOTICE)
                except:
                    pass
                
        dellist =[]
        for chan in self.schans:
            # check if saved channels are still avialble, if not, remove them
            # from schans dict
            if chan not in self.chans:
                dellist.append(chan)
    
        i2 = 0
    
        for chan in dellist:
            i2 += 1
    
            percentage = int(float(i) / chans_count * 100)
            if not debug: pDialog.update(percentage, 'removing offline %s'
                           % self.schans[chan]['name'])
            msg = self.schans[chan]['name'] + ' no longer live, removed'
            try:
                print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGNOTICE)
            except:
                pass
            
            del self.schans[chan]
        msg = '%d channels added, and %d channels removed'%(i, i2)
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGNOTICE)
        self.update_chansdb()
        
    def update_chan_url(self, chan, url):
        self.schans[chan]['url'] = url
        self.update_chansdb()
        
    def _repr_dict(self, d):
        return '{%s}' % ','.join("'%s': %s" % (x, y) for (x, y) in d.iteritems())
    
    def _repr_dict2(self, d):
        return '{%s}' % ',\n'.join("'%s': %s" % (x, self._repr_list(y)) for (x, y) in d.iteritems())
    def _repr_list(self, l):
        return '[%s]' % ','.join(" %s" % item for item in l)
    
    def youtube_search(self):
        '''
        Search for live Arabic Youtube channels by executing API calls
        '''
        msg = "YT_live.youtube_search"
        print msg if debug else xbmc.log(msg=msg, level=xbmc.LOGDEBUG)
        
        
        def _create_patt_obj(li):
            patt_str = r''                             # initialize the pattern
            for entry in li:                           # loop over the List array
                patt_str += '(%s)|'% entry             # create qualifer pattern str
            patt_str = patt_str[:-1]                   # remove the last pipe |
#            print 'patt_str = %s' %patt_str
            return re.compile(patt_str, re.IGNORECASE) # return the pattern object

        qual_patt = _create_patt_obj(self.filters)
        
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)

        if not debug:
            pDialog = xbmcgui.DialogProgressBG()
            pDialog.create('WS Live TV - Getting Channels')

        i = 0
        LI_count = len(self.search_list)
        exclude_patt = re.compile(self.excludes, re.IGNORECASE)
        qual_dict = {}
        for li in self.search_list:
            i += 1

            if not debug:
                percentage = int(float(i) / LI_count * 100)
                pDialog.update(percentage, 'searching for %s' % li)
            # Call the search.list method to retrieve results matching the specified
            # query term.
            search_response = youtube.search().list(
                q=li,
                part="id,snippet",
                maxResults=50,
                type="video",
                eventType='live'
                ).execute()

            # Add live channels to the dict chans
            added = 0
            for search_result in search_response.get("items", []):
                try:
                    vid     = search_result["id"]["videoId"]
                    title   = search_result["snippet"]["title"].encode('utf8')
                    title2  = search_result["snippet"]["channelTitle"].encode('utf8')
                except:
                    break
                
                if vid not in self.chans.keys() and exclude_patt.search(title) == None:
                    match2 = qual_patt.search(title)
                    if match2:
                        # track the effectiveness of each filter by counting the number
                        # of channels added for each filter
                        match_str = match2.group().lower().encode('utf8')
                        if match_str in qual_dict:
                            qual_dict[match_str] += 1
                        else:
                            qual_dict[match_str] = 1
                             
                        added += 1
                        category_found = False
                        for (category_name, channels) in self.categories.items():
                           patt_chans = _create_patt_obj(channels)
                           match =patt_chans.search('%s-%s'%(title,title2))
                           if match:
                                   category_found = True
                                   self.chans[vid] = {'category': category_name,
                                                      'name':  match.group(0),
                                                      'label': title2,
                                                      'title': title
                                                      }
                           if not category_found:
                               self.chans[vid] = {'category': 'No_Cat',
                                                     'name':  '%s' %title,
                                                     'label': title2,
                                                     'title': title
                           }
                       
            msg = "searching for " + li + " added " + str(added) + " chans"

            if debug: print msg
            else:
                xbmc.log(msg=msg, level=xbmc.LOGNOTICE)
                pDialog.update(percentage, 'searching for %s complete' % li, 'added %d channels' % added )
        msg = 'qual_dict is %s'%self._repr_dict(qual_dict)
        if debug: print msg
        else:
            xbmc.log(msg=msg, level=xbmc.LOGNOTICE)

if __name__ == "__main__":
    debug = 1
    if debug: print "instantiate YT_live class"
    class cache():
        def __init__(self, name):
            print('cache - __init__ name = %s' %name)
            self.table_name = ''
            self.name = ''

        def get(self, name):
#            print('cache - get name = %s' % name)
            return self.name
                
        def set(self, name, value):
#            print('cache - set name = %s, value %s' % (name, value))
            self.name = value

        def save(self):
            videoids = []
            f = open('chans', 'wb')
            for (key, ch) in eval(self.name).items():
                f.write('category %10s -- name: %20s - label: %30s title: %20s\n' %
                        (ch['category'], ch['name'], ch['label'], ch['title']))
                videoids.append(key)
            f.close()
            open('videoids', 'wb').write(str(videoids))

#        def dump(self):
#            f = open('chans', 'rb')
#            f.read()

    d1 = cache('data')
    c1 = cache('chans')
    my_yt = YT_live(c1, d1)

    if debug: print "call youtube_search method"
    try:
        my_yt.youtube_search()
    except HttpError, e:
        if debug: print "An HTTP error %d occurred:\n%s" % (e.resp.status,
                                                           e.content)
    if debug: print "call update_schans method"
    my_yt.update_schans(flush=False)
    
    c1.save()
    
