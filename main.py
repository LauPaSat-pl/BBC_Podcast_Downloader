import json
from datetime import datetime
from tkinter import *

import requests as requests


def remove_forbidden_chars(name: str):
	"""
	Function to remove characters that are forbidden in a file name on Windows from file name
	:param name: Name to be modified
	:return: Correct name
	"""
	forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
	return name.translate({ord(x): '' for x in forbidden_chars})


def download(desc, selection):
	for ep, i in zip(desc, range(len(desc))):
		if not selection[i].get():
			continue
		series_name = ep['series']
		date = datetime.strptime(ep['datePublished'], '%Y-%m-%d').date()
		episode_name = ep['name']
		series_name = ''.join(series_name.split())
		file_name = f"{series_name}-{date.strftime('%Y%m%d')}-{episode_name}.mp3"
		file_name = remove_forbidden_chars(file_name)
		link = ep['link']
		mp3 = requests.get(link).content
		with open(file_name, 'wb') as f:
			f.write(mp3)
	root.destroy()


def get_download_links(data, high_quality=False):
	"""
	Function to get download links from given site
	:param high_quality: If to download in higher quality
	:param data: Website as string (text)
	:return: List of links
	"""
	links = []
	if high_quality:
		link_base = '//open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download/'
	else:
		link_base = '//open.live.bbc.co.uk/mediaselector/6/redir/version/2.0/mediaset/audio-nondrm-download-low/'
	data = data.split(link_base)
	for i in range(1, len(data)):
		t = 'http:' + link_base + data[i].split('"')[0]
		links.append(t)
	return links


def load_data():
	"""
	Function to load data from csv
	:return: Dictionary of podcasts and their urls
	"""

	podcasts_urls = {}
	with open("podcasts_url.csv", 'r') as file:
		raw = file.readlines()[1:]
		for line in raw:
			name, url = line.strip().split(', ')
			podcasts_urls[name] = url
	return podcasts_urls


def test(to_download_list):
	text = ''
	for val in to_download_list:
		text += str(val.get())
	Label(root, text=text).pack()


def get_podcasts(url, last_download: datetime, high_quality=False):
	"""
	Function to download podcasts and save them
	:param url: URL to series download page
	:param last_download: Date on which last download took place
	:param high_quality: If to download in higher quality
	"""
	data = requests.get(url).text
	download_links = get_download_links(data, high_quality)
	desc = json.loads(data.split('<script type="application/ld+json">')[-1].split('\n')[1])['hasPart']
	desc = [ep for ep in desc if datetime.strptime(ep['datePublished'], '%Y-%m-%d').date() >= last_download]
	for i in range(len(desc)):
		desc[i]['link'] = download_links[i]

	return desc


def choose_podcasts(podcasts):
	desc = []
	for k, v in podcasts.items():
		for episode in v:
			episode['series'] = k
		desc += v

	Label(root, text='Select podcasts to download', font='Arial 20 bold').pack()
	selection = [IntVar() for _ in range(len(desc))]
	print("Creating checklist")
	checklist = []

	for episode in desc:
		try:
			if episode['series'] != checklist[-1] and episode['series'] != checklist[-1]['series']:
				checklist.append(episode['series'])
		except IndexError:
			checklist.append(episode['series'])
		checklist.append(episode)
	print(checklist)
	counter = 0
	for c, i in zip(checklist, range(len(checklist))):
		if isinstance(c, str):
			Label(root, text=c, font='Arial 15 bold').pack()
		else:
			box = Checkbutton(root,
			                  text=desc[counter]['name'],
			                  variable=selection[counter]
			                  )
			box.select()
			box.pack()
			counter += 1
	Button(root, text='Download', command=lambda: download(desc, selection)).pack()
	root.mainloop()


def main():
	podcasts_urls = load_data()
	last_download = datetime.strptime(input("Enter last download date in %Y-%m-%d format"), '%Y-%m-%d').date()
	podcasts = {}
	for name, url in podcasts_urls.items():
		podcasts[name] = get_podcasts(url, last_download)
	choose_podcasts(podcasts)


if __name__ == '__main__':
	root = Tk()
	root.title("BBC podcast downloader")
	root.iconbitmap('icon.ico')
	root.geometry("400x400")
	main()
