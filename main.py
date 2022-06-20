import json
from datetime import datetime

import requests as requests


def remove_forbidden_chars(name: str):
	"""
	Function to remove characters that are forbidden in a file name on Windows from file name
	:param name: Name to be modified
	:return: Correct name
	"""
	forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
	return name.translate({ord(x): '' for x in forbidden_chars})


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


def get_podcasts(series_name, url, last_download: datetime, high_quality=False):
	"""
	Function to download podcasts and save them
	:param series_name: Series title
	:param url: URL to series download page
	:param last_download: Date on which last download took place
	:param high_quality: If to download in higher quality
	"""
	data = requests.get(url).text
	download_links = get_download_links(data, high_quality)
	desc = json.loads(data.split('<script type="application/ld+json">')[-1].split('\n')[1])['hasPart']
	desc = [ep for ep in desc if datetime.strptime(ep['datePublished'], '%Y-%m-%d').date() >= last_download]
	print(f"There are {len(desc)} podcasts to download")
	for link, ep in zip(download_links, desc):  # Links are in chronological order
		date = datetime.strptime(ep['datePublished'], '%Y-%m-%d').date()
		series_name = ''.join(series_name.split())
		episode_name = ep['name']
		file_name = f"{series_name}-{date.strftime('%Y%m%d')}-{episode_name}.mp3"
		file_name = remove_forbidden_chars(file_name)
		download = ''
		while download != 'y' and download != 'n':
			download = input(f'Press y to download {file_name} and n to skip it')
		if download == 'y':
			mp3 = requests.get(link).content
			with open(file_name, 'wb') as f:
				f.write(mp3)


def main():
	podcasts_urls = load_data()
	last_download = datetime.strptime(input("Enter last download date in %Y-%m-%d format"), '%Y-%m-%d').date()
	for name, url in podcasts_urls.items():
		get_podcasts(name, url, last_download)


if __name__ == '__main__':
	main()
