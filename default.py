# -*- coding: utf-8 -*-
# Module: default
# Author: WzS
# Created on: 03.15.2017
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import os

from urllib import urlencode
from urlparse import parse_qsl

from time import time as now

import xbmcgui
import xbmcplugin

from resources.lib.yt import YT_live
from resources.lib.get_info import get_video_streams 
from resources.lib.common.addon import Addon

import StorageServer

REFRESH_URL_TH = 60*60*6 # set refresh url time out to 5 hours
'''
This is the main class for the addon, it inherits from Addon which is borrowed 
from common addon. 
'''
class WSliveTV(Addon):
    def __init__(self, addon_id, argv=None):
        '''
        The constuctor calls the Addon constructor, and instansite the YT_live
        class, and pass it the cache instance from common cache plugin
        '''
        Addon.__init__(self, addon_id, argv)

        self.cache = StorageServer.StorageServer("wslivetv",2)
        self.data = StorageServer.StorageServer("wslivetv_data",24*366*5)
        self.my_yt = YT_live(self.cache, self.data)

        self.yt_path = self.get_path()
        self.get_chans()
        self.categories = self.my_yt.categories.keys()
        self.categories.extend(['All', 'No_Cat'])
        
    def update_live_feed(self, flush=False):
        if flush:
            self.my_yt.delete_db()
        self.my_yt.youtube_search()
        self.my_yt.update_schans(flush=flush)

    def get_chans(self, category='All'):
        """
        get channel list from database
        """
        schans =  self.my_yt.dump_chansdb()
    
        if category == 'All':
            self.chans = schans
        else:
            self.chans = schans[category]
        
    def update_chan_url(self, chan, url):
        self.my_yt.update_chan_url(chan, url)

    def list_categories(self):
        """
        Create the list of video categories in the Kodi interface.
        """
        # Iterate through categories
        
        for category in self.categories:
            # Create a list item with a text label and a thumbnail image.
            image = os.path.join(self.yt_path, 'resources', 'media', category + ".png")
            image_f = os.path.join(self.yt_path, 'resources', 'media', category + "_f.jpg")
            queries = {}
            infolabels = {}
            queries['action']   = 'listing'
            queries['category'] = category
            infolabels['title'] = category
            infolabels['genre'] = category
            infolabels['label'] = category
            menu_items = self.add_context_menu(cat=category)
            self.add_directory(queries, infolabels, contextmenu_items=menu_items,
                               img=image, fanart=image_f, total_items=len(self.categories),)

        # Finish creating a virtual folder.
        self.end_of_directory()
    
    def create_listitem(self, chan, strm=0, lv=False, cat=''):
        '''
        create list item for channel
        '''
        thumb_url = 'https://i.ytimg.com/vi/%s/hqdefault_live.jpg'%chan
#        fanart_url = 'https://i.ytimg.com/vi/%s/hqdefault_live.jpg'%chan
#        icon_url = 'https://i.ytimg.com/vi/%s/hqdefault_live.jpg'%chan

        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=self.chans[chan]['name'])

        path = ''

        # set path and add context menu if avialable
        if 'url' in self.chans[chan]:
            path = self.chans[chan]['url'][int(strm)][1]
            self.log(msg='Found URL, strm=%s, path=%s'%(strm, path), level=xbmc.LOGDEBUG)

        menu_items = self.add_context_menu(chan=chan)
        list_item.addContextMenuItems(menu_items)

        if cat == 'All':
            title = '%s - %s' %(self.chans[chan]['name'], self.chans[chan]['category'])
        else:
            title = self.chans[chan]['name']
            self.log(msg='channel title=%s'%(title), level=xbmc.LOGNOTICE)

            if lv:
                # append a number to channel name if name exsits
                ft = title
                i = 1
                while title in self.titles:
                    title = '%s %d'%(ft, i)
                    i = i + 1
            
                self.chans[chan]['name'] = title
                self.titles.append(title)

        # Set additional info for the list item.
        list_item.setInfo('video', {'title': title, 
                                    'genre': self.chans[chan]['category']})

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.)
        # for the list item.  Here we use the same image for all items for
        # simplicity's sake.
        list_item.setArt({'thumb':  thumb_url,
                          'icon':   thumb_url,
                          'fanart': thumb_url})

        list_item.setPath(path=path)
        list_item.setLabel2(self.chans[chan]['label'])

        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')

        if lv:
            # if called with lv -list video- 
            # Create a URL for a plugin recursive call.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            url = self.build_plugin_url({'action':'play', 'video':self.chans[chan]['name'], 'strm':strm})

            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False

            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(self.handle, url, list_item, is_folder)
            xbmcplugin.setContent(self.handle, 'episodes')
        return list_item

    def list_videos(self, category = None):
        """
        Create the list of playable videos in the Kodi interface.

        :param category: Category name
        :type category: str
        """
        # Get the list of videos in the category.
        msg = 'listing channels for %s category' %category
        self.log(msg=msg, level=xbmc.LOGNOTICE)
        channels = {}
        if category != 'All':
            for chan in self.chans:
                if self.chans[chan]['category'] == category:
                    channels[chan] = self.chans[chan]
        else:
            channels = self.chans
        
        self.titles = []
        # Iterate through channels.
        for i, chan in enumerate(channels):
            # create the list item for channel
            self.create_listitem(chan, lv=True, cat=category)
            # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

        # Finish creating a virtual folder.
        self.end_of_directory()
        self.my_yt.update_chansdb()

    def find_chan(self, name):
       '''
       find channel id and path from channel name
       '''

       msg = "play_video - processing " + name
       self.log(msg=msg, level=xbmc.LOGNOTICE)

       chan_id = ''
       # search for channel name
       found = False
       for chan in self.chans:
           if self.chans[chan]['name'] == name:
           #if self.chans[chan]['name'].find(name) != -1 and self.chans[chan]['name'] == name:
               msg = b"Found %s in db, was looking for %s" \
                   % (self.chans[chan]['name'], name)

               self.log(msg=msg, level=xbmc.LOGNOTICE)
               found = True
               return (found, chan)
       # still not found
       msg = b"Not Found %s in db" % name
       self.log(msg=msg, level=xbmc.LOGNOTICE)
       return (found, '')
    

    def add_context_menu(self, chan=None, cat=None):
        # add to context menu alternative streams 
        menu_items = []
        if chan:
            ch_cat = 'channel'
            val2 = chan
            val3 = ''
        else:
            ch_cat = 'category'
            val2 = ''
            val3 = cat
           
        def _add_context_item(menu_items, command, label):
           # add update channel button
           encoded_url = self.build_plugin_url({'action':command, 'id':val2, 
                                                'cat':val3} )
           action = 'RunPlugin(%s)'    % encoded_url
           menu_items.append((label, action))
           
        _add_context_item(menu_items, command='update', label ='Update channels')
        _add_context_item(menu_items, command='move', label ='Move %s'%ch_cat)
        _add_context_item(menu_items, command='remove', label ='Remove %s'%ch_cat)
        _add_context_item(menu_items, command='rename', label ='Rename %s'%ch_cat)

        if cat:
            _add_context_item(menu_items, command='modify', label ='modify category')
            
        # set path and add context menu if avialable
        if chan and 'url' in self.chans[chan]:
            self.log(msg='context_menu_items %d' % len(menu_items), level=xbmc.LOGDEBUG)
            for i, url in enumerate(self.chans[chan]['url']):
                encoded_url = self.build_plugin_url({'action':'play', 'video':self.chans[chan]['name'], 'strm':i} )
                label  = 'Play %sp Stream Format' % url[0]
                if url[0] == 7:
                    label  = 'Play main Stream Format'
                action = 'PlayMedia(%s)'    % encoded_url
                menu_items.append((label, action)) 
        return menu_items
     
    def remove_channel(self, chan):
        """
        remove channel from categories database
        :param chan: channel id
        :type id: str
        """
        name = self.chans[chan]['name']
        current_cat = self.chans[chan]['category']
        try:
            self.my_yt.categories[current_cat].remove(name)
        except:
            pass
        self.chans[chan]['category'] = 'No_Cat'
        self.my_yt.update_chansdb()
        self.update_ui()   # force re-listing of menu after change
        
    def rename_channel(self, chan):
        """
        rename channel in categories database
        :param chan: channel id
        :type id: str
        """
        name = self.chans[chan]['name']
        label = self.chans[chan]['label']
        title = self.chans[chan]['title']
        current_cat = self.chans[chan]['category']
        
        dialog = xbmcgui.Dialog()

        modified_name = dialog.input('Modify channel name', 
                defaultt='%s - %s'%(name, label),type=xbmcgui.INPUT_ALPHANUM)

        self.log(msg='modified_name = %s' %modified_name, level=xbmc.LOGNOTICE)
        if not modified_name:
            modified_name = title
        
        if modified_name:
            try:
                self.my_yt.categories[current_cat].append(modified_name)
                self.my_yt.categories[current_cat].remove(name)
            except:
                pass
            self.chans[chan]['name'] = modified_name
            self.my_yt.update_chansdb()
            self.update_ui()   # force re-listing of menu after change
            
    def move_channel(self, chan):
        """
        move channel to a different folder
        :param chan: channel id
        :type id: str
        """
        current_cat = self.chans[chan]['category']
        name = self.chans[chan]['name']
        title = self.chans[chan]['title']
        label = self.chans[chan]['label']
        
        msg = 'move_channel - %s, id %s' %(name, chan)
        self.log(msg=msg, level=xbmc.LOGDEBUG)
        
        dialog = xbmcgui.Dialog()
        list_cat = self.categories
        list_cat.append('New Category ..')
        list_cat.remove('All')
        list_cat.remove('No_Cat')
        
        self.log(msg='name = %s, label = %s, title = %s' %(name, label, title), level=xbmc.LOGNOTICE)

        if name == title:
            modified_name = dialog.input('Modify channel name', 
                    defaultt='%s-%s'%(label, name),type=xbmcgui.INPUT_ALPHANUM)
            self.log(msg='modified_name = %s' %modified_name, level=xbmc.LOGNOTICE)
            if not modified_name:
                modified_name = title
#                return
        else:
            modified_name = name
        
        selected_cat = dialog.select('Choose a category', self.categories)
        self.log(msg='selected cat = %s'%(selected_cat), level=xbmc.LOGNOTICE)
        if selected_cat == -1:  return
        
        if list_cat[selected_cat] == 'New Category ..':
            # create a new category
            cat_name = dialog.input('Enter New Category Name', type=xbmcgui.INPUT_ALPHANUM)
            if not cat_name:  return
            
            # update database
            self.categories.append(cat_name)
            self.my_yt.categories[cat_name] = [modified_name,]
        else:
            cat_name = list_cat[selected_cat]
            self.log(msg='selected cat = %s, cat_name = %s'%(selected_cat, cat_name), level=xbmc.LOGNOTICE)
            if not cat_name:  return

            # update database
            self.log(msg='my_yt.categories[cat_name] = %s' %self.my_yt.categories[cat_name], level=xbmc.LOGNOTICE)
            self.my_yt.categories[cat_name].append(modified_name)
            if current_cat and current_cat != 'No_Cat' and current_cat in self.my_yt.categories:
                self.my_yt.categories[current_cat].remove(name)
                
        self.my_yt.schans[chan]['category'] = cat_name
        self.my_yt.schans[chan]['name'] = modified_name
        self.my_yt.update_chansdb()
        self.update_ui()    # force re-listing of menu after change

    def move_category(self, cat):
        self.log(msg='inside move_category', level=xbmc.LOGNOTICE)
    def remove_category(self, cat):
        cn = self.my_yt.categories[cat]
        self.log(msg='inside remove_category %s, content %s'%(cat,cn) , level=xbmc.LOGNOTICE)

        for name in cn:
            for chan in self.chans:
                if self.chans[chan]['name'] == name:
                    self.chans[chan]['category'] = 'No_Cat'
                    break
                
        del self.my_yt.categories[cat]    
        self.my_yt.update_chansdb()
        self.update_ui()    # force re-listing of menu after change
        
    def rename_category(self, cat):
        self.log(msg='inside rename_category', level=xbmc.LOGNOTICE)
        
    def modify(self, var):
        if var == 'search':
            data = self.my_yt.search_list
        elif var == 'filter':
            data = self.my_yt.filters
        elif var == 'exclude':
            data == self.my_yt.excludes
        else:
            # modify category
            data = self.my_yt.categories[var]

        add_new = 'Add a new %s item ..'%var
        enter_new = 'Enter new %s item'%var
        rename_msg = 'Rename %s item'%var
        data.append(add_new)

        self.log(msg='inside modify, var=%s'%var, level=xbmc.LOGNOTICE)
        dialog = xbmcgui.Dialog()
        selected_var = dialog.select('Choose a %s entry to modify or create a new one'%var, data)
        self.log(msg='selected_var=%s'%selected_var, level=xbmc.LOGNOTICE)
        if selected_var == -1:  return
        
        if data[selected_var] == add_new:
            # create a new item
            item_name = dialog.input(enter_new, type=xbmcgui.INPUT_ALPHANUM)
            if not item_name:  return
            # update database
            data.append(item_name)
        else:
            item_name = data[selected_var]
            self.log(msg='selected item = %s, item_name = %s'%(selected_var, item_name), level=xbmc.LOGNOTICE)
            modified_name = dialog.input(rename_msg, item_name ,type=xbmcgui.INPUT_ALPHANUM)
            if modified_name:
                data.append(modified_name)
            data.remove(item_name)
        data.remove(add_new)
        self.my_yt.update_chansdb()
        
        
    def play_video(self, name, strm=0):
        """
        Play a video by the provided path.

        :param name: channel name
        :type path: str
        
        :param strm: steam number
        :type name: int
        """

        found, chan = self.find_chan(name)
        msg = 'Play_video - %s, id %s' %(name, chan)
        self.log(msg=msg, level=xbmc.LOGDEBUG)
        current_time = now()
        if not found:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('WS Live TV - play_video', 'channel %s is offline' % name)
        else:
            if 'url_ts' not in self.chans[chan] or \
                current_time - self.chans[chan]['url_ts'] > REFRESH_URL_TH:
                # channel does not have a URL, so let's get it
                msg = 'URL not found attempting to retrieve it ...'
                self.log(msg=msg, level=xbmc.LOGDEBUG)
                streams = get_video_streams(chan)
                if len(streams) == 0:
                    dialog = xbmcgui.Dialog()
                    ok = dialog.ok('WS Live TV - play_video', 'channel %s is offline' % name)
                    return
                url_list = []

                #save alternative stream to chans dictionary
                for stream in streams:
                    url_list.append((stream['sort'][0], stream['url']))
                self.chans[chan]['url'] = url_list

                # save current time in url_ts
                self.chans[chan]['url_ts'] = current_time
                
                # save db with the change
                self.update_chan_url(chan, url_list)

#        # Pass the item to the Kodi player.
        self.resolve_url(chan, strm)
        
    def update_ui(self):
        '''
        force update UI to re-list menu where chan is located
        '''
        import xbmc
        xbmc.executebuiltin('Container.Refresh')
        
    def resolve_url(self, chan, strm):
        play_item = self.create_listitem(chan, strm)
        xbmcplugin.setResolvedUrl(self.handle, True, play_item)
        
    
    def start_menu(self):
        """
        display the start menu.

        :param name: None
        :type path: None
        """
        # Add List Categories directory item
        image = os.path.join(self.yt_path, 'resources', 'media', 'listcat' + ".png")
        image_f = os.path.join(self.yt_path, 'resources', 'media', 'listcat' + "_f.jpg")
        self.add_directory({'action':'list_categories'}, {'title':'List Categories'},
                           img=image, fanart=image_f)
        # Add Setting directory item
        image = os.path.join(self.yt_path, 'resources', 'media', 'setting' + ".png")
        image_f = os.path.join(self.yt_path, 'resources', 'media', 'setting' + "_f.jpg")
        self.add_directory({'action':'setting'}, {'title':'Setting'},
                           img=image, fanart=image_f)

        # Finish creating a virtual folder.
        self.end_of_directory()
        
    def router(self, paramstring):
        """
        Router function that calls other functions
        depending on the provided paramstring

        :param paramstring: URL encoded plugin paramstring
        :type paramstring: str
        """
        # Parse a URL-encoded paramstring to the dictionary of
        # {<parameter>: <value>} elements
        params = dict(parse_qsl(paramstring))

        msg = 'router url %s, handle %d' %(self.url, self.handle)
        self.log(msg=msg, level=xbmc.LOGNOTICE)
        self.log(msg=str(params), level=xbmc.LOGNOTICE)
    
        # Check the parameters passed to the plugin
        if params:
            if params['action'] == 'listing':
                # Display the list of videos in a provided category.
                self.list_videos(params['category'])
            elif params['action'] == 'play':
                # Play a video from a provided URL.
                if 'strm' in params:
                    self.play_video(params['video'], params['strm'])
                else:
                    self.play_video(params['video'])
            elif params['action'] == 'update':
                flush = False
                if 'flush' in params:
                    flush = params['flush']
                self.update_live_feed(flush=flush)
                self.update_ui()
            elif params['action'] == 'move':
                if 'id' in params:
                    self.move_channel(params['id'])
                if 'cat' in params:
                    self.move_category(params['cat'])
            elif params['action'] == 'remove':
                if 'id' in params:
                    self.remove_channel(params['id'])
                else:
                   if 'cat' in params:
                      self.remove_category(params['cat'])
                   else:
                       self.remove_category('')
                       
            elif params['action'] == 'rename':
                if 'id' in params:
                    self.rename_channel(params['id'])
                if 'cat' in params:
                    self.rename_category(params['cat'])
            elif params['action'] == 'list_categories':
                # display the list of video categories
                self.list_categories()
            elif params['action'] == 'modify':
                # modify parameters
                if 'var' in params:
                    self.modify(params['var'])
                elif 'cat' in params:
                    self.modify(params['cat'])
            elif params['action'] == 'setting':
                 self.show_settings()
            else:
                # If the provided paramstring does not contain a supported action
                # we raise an exception. This helps to catch coding errors,
                # e.g. typos in action names.
                raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
        else:
            self.log(msg='Plugin called from kodi UI without any parameters', level=xbmc.LOGNOTICE)
            #   If the plugin is called from Kodi UI without any parameters
            self.update_live_feed(flush=False)

            # display the list of video categories
            self.start_menu()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
#    msg = 'wslivetv sys.argv[2][1:] ' + sys.argv[2][1:]
    msg = 'wslivetv sys.argv[2] ' + sys.argv[2]
    ws = WSliveTV('plugin.video.wslivetv', sys.argv)
    ws.log(msg=msg, level=xbmc.LOGNOTICE)
    ws.router(sys.argv[2][1:])
