# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, socket, os
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs

# Определяем параметры плагина
_ADDON_NAME =   'plugin.video.kset'
_addon      =   xbmcaddon.Addon(id=_ADDON_NAME)
_addon_id   =   int(sys.argv[1])
_addon_url  =   sys.argv[0]
_addon_path =   _addon.getAddonInfo('path').decode('utf-8')
sys.path.append(os.path.join( _addon_path , 'resources', 'lib'))
_addon_lang = _addon.getSetting('language')
_addon_result_thumbs = _addon.getSetting('list-view')
_url_page = '0'
_url = 'http://kset.kz'
_find_mode = ''
#scroll_last_object  10     
_scroll_last_offset = '0'
_type = ''
_genre = ''

from kset_config import get_config

def getVideo(url):
	try:
		headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
		post_data = {'scroll_last_object' :  _url_page, 'scroll_last_offset' : _url_page}
		conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode(post_data), headers))
	except urllib2.URLError, socket.timeout:
		xbmc.executebuiltin('Notification(%s,%s)' % (_string(100501), _string(100502)))
#		xbmc.log(url)
	else:
		html = conn.read()
		conn.close()
		return html

def getHTML(url):
	try:
		headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
		conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
	except urllib2.URLError, socket.timeout:
		xbmc.executebuiltin('Notification(%s,%s)' % (_string(100501), _string(100502)))
#		xbmc.log(url)
	else:
		html = conn.read()
		conn.close()
		return html

# Вспомогательная функция для отображения строк интерфейса
def _string(string_id):
	return _addon.getLocalizedString(string_id).encode('utf-8')

# mode == Null
def Categories():
	global _find_mode
	
	url = 'http://kset.kz/cinema/'
	
	_find_mode = 'movie'
	addDir('[B]Фильмы[/B]',url + '?search_string=&type=movie&genre=', 20, '', True, '0')
	_find_mode = 'series'
	addDir('[B]Сериалы[/B]',url + '?search_string=&type=series&genre=', 20, '', True, '0')				

# mode == 20 
def Movies(url):
	global _find_mode
	
	html = getVideo(url)

	movie_links = re.compile('<a class="cinema-poster fl_l bcFF pad6 sh1302 br5 us_none a navi" href="(.+?)">\s+<img class="fl_l br4" src="(.+?)" alt="(.+?)">').findall(html)
	
	is_cat = False
	
	if 'type=series' in url:
		is_cat = True
		_find_mode = 'series'
	elif 'type=movie' in url:
		is_cat = False
		_find_mode = 'movie'
		
	addDir('[B]Поиск[/B]','',40,'',True, '0')
	
	item = xbmcgui.ListItem('[B]Категории[/B]', iconImage='DefaultFolder.png', thumbnailImage='')
	xbmcplugin.addDirectoryItem(_addon_id, 'plugin://plugin.video.kset/' , item, True)	
	
	for link, png, title in movie_links:
		addDir(title, _url + link, 30, png, is_cat, _url_page)
	
	
	if 'paginateLastOffset = 0' not in html:
		addDir('[COLOR F5DEB300]Загрузить еще[/COLOR]', url, 20, '', True, str( int(_url_page) + 10 ))

def Videos(url, title, png, is_seria):
	if is_seria == True:
		
		item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=png)
		item.setInfo( type='Video', infoLabels={'Title': title} )		
		xbmc.Player().play(url, item)		
	else:
		config = get_config(url)
		
		if config['type'] == 'series':
			for vid in config['videos']:
				if vid['episode'] == '':
					ep_index = '1'
				else:
					ep_index = vid['episode']
				ep_index = 'Episode ' + ep_index
				addDir(ep_index, vid['file'], 50, vid['poster'], False, _url_page)
		else:
			item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=png)
			item.setInfo( type='Video', infoLabels={'Title': title} )
			xbmc.Player().play(config['videos'][0]['file'], item)
 

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
                            
    return param


def addLink(title, url):
    item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


def addDir(title, url, mode, png, is_cat, page):
	sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url)

	sys_url = sys_url + '&mode=' + urllib.quote_plus(str(mode)) 
	
	if png:
		spng = png
		sys_url = sys_url + '&png=' + urllib.quote_plus(spng)
	else:
		spng = ''
	
	sys_url = sys_url + '&page=' + urllib.quote_plus(page)
	sys_url = sys_url + '&type=' + urllib.quote_plus(_find_mode)	
	
	item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=spng)
	item.setInfo( type='Video', infoLabels={'Title': title} )

	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=is_cat)

# Переключаемся на нужный вид в зависимости от текущего скина.
def switch_view():
	if _addon_result_thumbs == 'true':
		skin_used = xbmc.getSkinDir()
		if skin_used == 'skin.confluence':
			xbmc.executebuiltin('Container.SetViewMode(500)') # Вид "Эскизы".
		elif skin_used == 'skin.aeon.nox':
			xbmc.executebuiltin('Container.SetViewMode(512)') # Вид "Инфо-стена"
		
def Find_video():
	dialog = xbmcgui.Dialog()
	q = dialog.input('Введите название', type=xbmcgui.INPUT_ALPHANUM)
	url = 'http://kset.kz/cinema/?search_string='+urllib.quote(q)+'&type='+_find_mode+'&genre='
	Movies(url)
	switch_view()

params = get_params()
url    = None
title  = None
mode   = None
png	   = None


try:    title = urllib.unquote_plus(params['title'])
except: pass

try:    url = urllib.unquote_plus(params['url'])
except: pass

try:    mode = int(params['mode'])
except: pass

try:    png = urllib.unquote_plus(params['png'])
except: pass

try:    _url_page = params['page']
except: pass

try:    _find_mode = urllib.unquote_plus(params['type'])
except: pass

if mode == None:
	Categories()
elif mode == 20:
	Movies(url)
	switch_view()
elif mode == 30:
	Videos(url, title, png, False)
elif mode == 40:
	Find_video()
elif mode == 50:
	Videos(url, title, png, True)	

xbmcplugin.endOfDirectory(int(sys.argv[1]))