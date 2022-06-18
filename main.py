import json
from datetime import datetime

import requests as requests


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


def get_podcasts(name, url, last_download: datetime, high_quality=False):
	"""
	Function to download podcasts and save them
	:param name: Series title
	:param url: URL to series download page
	:param last_download: Date on which last download took place
	:param high_quality: If to download in higher quality
	"""
	data = requests.get(url).text
	download_links = get_download_links(data, high_quality)
	descriptions = json.loads(data.split('<script type="application/ld+json">')[-1].split('\n')[1])['hasPart']

	for link, desc in zip(download_links, descriptions):
		date = datetime.strptime(desc['datePublished'], '%Y-%m-%d').date()
		if date < last_download:
			continue
		name = desc['name'].strip('?')
		mp3 = requests.get(link).content
		file_name = f"{date.strftime('%Y%m%d')}-{name}.mp3"
		print(file_name)
		with open(file_name, 'wb') as f:
			f.write(mp3)


def main():
	podcasts_urls = load_data()
	last_download = datetime.strptime(input("Enter last download date in %Y-%m-%d format"), '%Y-%m-%d').date()
	for name, url in podcasts_urls.items():
		get_podcasts(name, url, last_download)


if __name__ == '__main__':
	main()
