# -*- coding: utf-8 -*-

"""
'resources', 'lib'
http://kset.kz/cinema/view/34514

http://kset.kz/cinema/config?id=34514_0&cv=1&ref=http://kset.kz/cinema/view/34514

"""

# Импортируем нужные нам библиотеки

import urllib, urllib2, re, sys, os, json, StringIO
from urllib import urlencode

sdir = os.path.dirname(__file__)
# print ' >>>>> OS : ' + sys.platform
if sys.platform == 'win32':
	sys.path.append(os.path.join( sdir , 'win32'))
elif sys.platform == 'linux2':
	sys.path.append(os.path.join( sdir , 'linux2'))
elif sys.platform == 'darwin':
	sys.path.append(os.path.join( sdir , 'osx'))
else:
	print ' ******* No module Crypto for ' + sys.platform + ' system! *******'
	sys.exit()
	
key_path = os.path.join(sdir , 'key.pem')

from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import Blowfish
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random

def get_config(url):
	
	id = re.findall('view/(.*)',url)[0]
	
	c_url = 'http://kset.kz/cinema/config?id=' + id + '_0&cv=1&ref=' + url
	
	headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
	'X-Requested-With' : 'ShockwaveFlash/16.0.0.257',
	'Referer' : url,
	'Content-Type':'application/x-www-form-urlencoded'
	}
	
	conn = urllib2.urlopen(urllib2.Request(c_url, urlencode({}), headers))

	ciphertext = conn.read(128)
	cipherdata = conn.read()

	key = RSA.importKey( open(key_path).read() )

	dsize = SHA.digest_size
	sentinel = Random.new().read(15+dsize)      

	cipher = PKCS1_v1_5.new(key)
	key_bf = cipher.decrypt(ciphertext, sentinel)

	iv = cipherdata[:8]
	hexdata = cipherdata.decode("hex")
	cipher2 = Blowfish.new(key_bf, Blowfish.MODE_CBC, iv)
	dec = cipher2.decrypt(hexdata)

	start_len = dec.find('}'+chr(0))

	if start_len != -1:
		dec = dec[ 8 : start_len + 1 ]
	else:
		dec = dec[ 8 : ]

	test = urllib.unquote(dec).replace('\\', '')
	
	ff = StringIO.StringIO( test )

	j = json.load( ff )

	#j = json.load( open('c:\json.txt'))

	#j = json.dumps(test)

	ff.close()
	conn.close()
	return j

