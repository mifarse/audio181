# -*- coding: utf8 -*-
import requests, random, urllib2, pyvona
from pygame import mixer
from threading import Thread

v = pyvona.create_voice('GDNAJVKVFZS7FXQKGDLA', 'SjID1xWuAwZgo7P6T/PztcW8Kfrhk74Tw/1fdt0T')
v.voice_name = 'Maxim'

BOT = "https://api.telegram.org/bot214845784:AAHxJmUQcnYejv10siWkemKYr7Y68EnLu8c";
searchArtist_query = "http://ws.audioscrobbler.com/2.0/?method=artist.search&api_key=44694551b394e4a51530539a07cfa753&format=json"
artistTop_query = "http://ws.audioscrobbler.com/2.0/?method=artist.getTopTracks&api_key=44694551b394e4a51530539a07cfa753&format=json&limit=15&mbid="
artistSimilar_query = "http://ws.audioscrobbler.com/2.0/?method=artist.getSimilar&api_key=44694551b394e4a51530539a07cfa753&format=json&limit=100"
trackSimilar_query = "http://ws.audioscrobbler.com/2.0/?method=track.getSimilar&api_key=44694551b394e4a51530539a07cfa753&format=json&limit=10"
vkAudio_query = "https://api.vk.com/method/audio.search?access_token=9107a569ca4be8a80eead4e10e52956091055123f80eade3be60d901efbaf143c290bbfde38405be01b0b"

mbid_artist = ''
next_track    = False
is_similar    = False
player_isnt_sleeping = True
is_volume_changed = False
volume = 20

def getRandomTrack():
	global mbid_artist
	print "Generating random track..."
	person = open(random.choice(['serafim.txt', 'vadim.txt', 'nickolay.txt']), 'r')
	artist = random.choice([line for line in person])[:-1]
	person.close()

	print "select: "+artist
	request = requests.get(searchArtist_query, params={'artist': artist})
	data = request.json()
	mbid_artist = data['results']['artistmatches']['artist'][0]['mbid']

	if random.random() > 0.75:
		request = requests.get(artistSimilar_query, params={'artist': artist, 'autocorrect': 1})
		data = request.json()
		artists = random.choice(data['similarartists']['artist'])
		try:
			mbid_artist = artists['mbid']
			artist = artists['name']
			print artists['mbid']
		except:
			pass

	request = requests.get(artistTop_query+mbid_artist)
	data = request.json()
	track = random.choice(data['toptracks']['track'])
	print "Track generated!"

	return {'artist': artist, 'track': track['name'], 'full': artist+" "+track['name']}

def getSimilarTrack(artist, track):
	request = requests.get(trackSimilar_query, params={'artist': artist, 'track': track})
	data = request.json()
	print data
	tracks = random.choice(data['similartracks']['track'])
	return {'artist': tracks['artist']['name'], 'track': tracks['name'], 'full': tracks['artist']['name']+" "+tracks['name']}

def telegramListener():
	offset      = 0
	last_answer = 0
	global is_volume_changed
	global next_track
	global is_similar
	global player_isnt_sleeping
	global volume	

	while True:
		r = requests.get(BOT+"/getUpdates?offset="+str(offset))
		data = r.json()
		last_item = len(data['result']) - 1
		try:
			message = data['result'][0]['message']['text']

			if message == u'/next' and last_answer != offset:
				payload = {'text': u'Ок, ща подгоним. Думаю стоит включить...', 'chat_id': '-32380809'}
				requests.get(BOT+"/sendMessage", params=payload)
				next_track = True
				last_answer = data['result'][0]['update_id']

			if message == u'/similar' and last_answer != offset:
				is_similar = True
				payload = {'text': u'Все остальные треки будут похожими на этот', 'chat_id': '-32380809'}
				requests.get(BOT+"/sendMessage", params=payload)
				last_answer = data['result'][0]['update_id']

			if message == u'/random' and last_answer != offset:
				is_similar = False
				payload = {'text': u'Да будет Random!', 'chat_id': '-32380809'}
				requests.get(BOT+"/sendMessage", params=payload)
				last_answer = data['result'][0]['update_id']

			if message == u'/off' and last_answer != offset:
				player_isnt_sleeping = False
				payload = {'text': u'Отк лю ча ю с ь..', 'chat_id': '-32380809'}
				requests.get(BOT+"/sendMessage", params=payload)
				last_answer = data['result'][0]['update_id']

			if message == u'/on' and last_answer != offset:
				player_isnt_sleeping = True
				payload = {'text': u'Вест сайд хоме. Че кого, сучара?', 'chat_id': '-32380809'}
				requests.get(BOT+"/sendMessage", params=payload)
				last_answer = data['result'][0]['update_id']
			
			if u'volume' in message and last_answer !=offset:
				kek = message.split(' ')
				print kek[1]
				volume = float(kek[1])
				volume = volume/100
				is_volume_changed=True			
				payload = {'text': u'Понял, брат! Будет '+ kek[1], 'chat_id': '-32380809'}
				requests.get(BOT+"/sendMessage", params=payload)
				last_answer = data['result'][0]['update_id']

		except:
			pass
		offset = data['result'][last_item]['update_id']

tt = Thread(target=telegramListener)
tt.start()

while True:
	if (player_isnt_sleeping):
		track = getSimilarTrack(track['artist'], track['track']) if is_similar else getRandomTrack()
		track_request = {'q': track['full']}
		print track_request['q']
		request = requests.get(vkAudio_query, params=track_request)
		data = request.json()

		try:
			print "downloading and saving..."
			track_file_url = urllib2.urlopen(data['response'][1]['url'])
			output = open('song.mp3','wb')
			output.write(track_file_url.read())
			output.close()
			print "Done!"

			payload = {'text': '#np <b>'+track['artist']+'</b> - '+track['track'], 'chat_id': '-32380809', 'parse_mode': 'HTML'}
			requests.get(BOT+"/sendMessage", params=payload)

			mixer.init()
			mixer.music.load('song.mp3')
			#DJ MAX START
			f = open("DJcomments.txt")
			listComments = f.readlines()
			a = random.choice(listComments)
			b = a+' '+track['artist']
			v.speak(b)
			#DJ MAX FINISH
			mixer.music.play()
			while mixer.music.get_busy():
				if (next_track == True):
					print next_track
					break
				if(is_volume_changed):
					mixer.music.set_volume(volume)
					is_volume_changed=False
			next_track = False
		except:
			pass
