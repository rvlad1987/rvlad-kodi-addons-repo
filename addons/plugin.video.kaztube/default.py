# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, socket
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

# Определяем параметры плагина
_ADDON_NAME =   'plugin.video.kaztube'
_addon      =   xbmcaddon.Addon(id=_ADDON_NAME)
_addon_id   =   int(sys.argv[1])
_addon_url  =   sys.argv[0]
_addon_lang = _addon.getSetting('language')
_addon_result_thumbs = _addon.getSetting('list-view')
_url_page = 1

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
	
def Categories():
	url = 'http://kaztube.kz/'+_addon_lang
	html = getHTML(url)
	if html:
		addDir('[B]Поиск[/B]','',40,'',True, 0)
		addDir('[B]Рекомендуемое[/B]',url+'/',20,'',True, 0)		
		addDir('[B]Новое[/B]',url + '/video/', 20, '', True, 0)				

		category_video = re.compile('<li><a href="http://kaztube.kz/' + _addon_lang + '/video\?category_id=(.+?)">(.+?)</a></li>').findall(html)
		
		for link, title in category_video:
			addDir(title, url + '/video?category_id=' + link, 20,'', True, 0)

#	item = xbmcgui.ListItem('[B]Выход[/B]', iconImage='DefaultFolder.png', thumbnailImage='')
#	xbmcplugin.addDirectoryItem(_addon_id, 'plugin://' , item, True)	


def Movies(url):
	html = getHTML(url)

	png_links = re.compile('<img class="lazy" data-original="(.+?)" src="').findall(html)
	movie_links = re.compile('<a href="(.+?)" class="a ajax">\s+<span class="s1 ptsans_bold"><span class="hfx">(.+?)</span></span>').findall(html)
	
	item = xbmcgui.ListItem('[B]Категории[/B]', iconImage='DefaultFolder.png', thumbnailImage='')
	xbmcplugin.addDirectoryItem(_addon_id, 'plugin://plugin.video.kaztube/' , item, True)	
	
#	if _url_page > 1:
#		back_page = _url_page - 1
#		addDir('[COLOR F5DEB300]Назад[/COLOR]', url, 20, '', True, back_page)
		
	i = 0
	all = []

	for link, name in movie_links:
		all.append( (link, name, png_links[i] ) )
		i = i + 1

	for link, title, png in all:
		addDir(title, link, 30, png, False, 0)
	
	pages = re.compile('page="(.+?)" href="').findall(html)
		
	max_page = 0
	if pages:
		max_page = int(pages[-1])
		next_page = _url_page + 1
		if next_page <= max_page:
			addDir('[COLOR F5DEB300]Загрузить еще[/COLOR]', url, 20, '', True, next_page)

def Videos(url, title, png):
	html = getHTML(url)
	
	res = re.findall('startvideo\(\s+\'(.+?)\'',html)
	if res:
		link = res[0]
	else:
		res = re.findall('\&amp;file=(.+?)\&amp;link=',html)
		if res:
			link = res[0]
			
	item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=png)
	item.setInfo( type='Video', infoLabels={'Title': title} )
	#addLink(title, link)
	xbmc.Player().play(link, item)
   

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

	if page > 0:
		if url[-1] == '/':
			sys_url = sys_url + urllib.quote_plus( '?page='+str(page) )
		else:
			sys_url = sys_url + urllib.quote_plus( '&page='+str(page) )
	
	sys_url = sys_url + '&mode=' + urllib.quote_plus(str(mode)) 
	
	if png:
		spng = 'http://kaztube.kz' + png
		sys_url = sys_url + '&png=' + urllib.quote_plus(spng)
	else:
		spng = ''
	
	if page > 0:
		sys_url = sys_url + '&page=' + urllib.quote_plus(str(page))
		
	
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
	url = 'http://kaztube.kz/'+ _addon_lang +'/video?q='
	
	dialog = xbmcgui.Dialog()
	q = dialog.input('Введите название видео', type=xbmcgui.INPUT_ALPHANUM)
	
	url = url + urllib.quote(q) + '&sort=&duration=&added=&category_id=0'
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

try:    _url_page = int(params['page'])
except: pass


if mode == None:
	Categories()
elif mode == 20:
	Movies(url)
	switch_view()
elif mode == 30:
	Videos(url, title, png)
elif mode == 40:
	Find_video()	
	

xbmcplugin.endOfDirectory(int(sys.argv[1]))