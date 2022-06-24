import json
import os
import shutil
from datetime import datetime
from tkinter import *
from tkinter import messagebox

import requests as requests
from mutagen.mp3 import MP3


def remove_forbidden_chars(name: str):
	"""
	Function to remove characters that are forbidden in a file name on Windows from file name
	:param name: Name to be modified
	:return: Correct name
	"""
	forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
	return name.translate({ord(x): '' for x in forbidden_chars})


def download(podcasts, selection):
	"""
	Function to download selected podcasts
	:param podcasts: All podcasts visible in the GUI
	:param selection: Selection of podcasts to download (1 for podcasts to download and 0 for podcasts to skip)
	:return:
	"""
	try:
		for series in podcasts:
			series_name = ''.join(series.split())
			for ep, i in zip(podcasts[series], range(len(series))):
				if not selection[series][i].get():
					continue
				date = datetime.strptime(ep['datePublished'], '%Y-%m-%d').date()
				episode_name = ep['name']
				file_name = f"{series_name}-{date.strftime('%Y%m%d')}-{episode_name}.mp3"
				file_name = remove_forbidden_chars(file_name)
				link = ep['link']
				mp3 = requests.get(link).content
				with open(file_name, 'wb') as f:
					f.write(mp3)
		messagebox.showinfo(message="Podcasts downloaded")
	except Exception as e:
		messagebox.showerror(message="Error occurred. Please check your internet connection and try again.")
	finally:
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
	global last_download
	global path_to_save
	podcasts_urls = {}
	with open("podcasts_url.csv", 'r') as file:
		raw = file.readlines()[1:]
		for line in raw:
			name, url = line.strip().split(', ')
			podcasts_urls[name] = url
	with open('configure.txt', 'r') as f:
		last_download = datetime.strptime(f.readline().split('=')[1].strip(), '%Y-%m-%d').date()
		path_to_save = f.readline().split('=')[1].strip()

	return podcasts_urls


def get_podcasts(url, high_quality=False):
	"""
	Function to download podcasts and save them
	:param url: URL to series download page
	:param high_quality: If to download in higher quality
	"""
	data = requests.get(url).text
	download_links = get_download_links(data, high_quality)
	desc = json.loads(data.split('<script type="application/ld+json">')[-1].split('\n')[1])['hasPart']
	desc = [ep for ep in desc if datetime.strptime(ep['datePublished'], '%Y-%m-%d').date() >= last_download]
	for i in range(len(desc)):
		desc[i]['link'] = download_links[i]

	return desc


def prepare_screen():
	"""
	Function to prepare GUI for podcast checkboxes (title and scrollbar)
	:return:
	"""
	global frame
	global tooltip
	Label(root, text='Select podcasts to download', font='Arial 20 bold').pack()
	tooltip = Label(root, text='', bd=1, relief=SUNKEN, anchor=E)
	tooltip.pack(fill=X, side=BOTTOM)

	main_frame = Frame(root)
	main_frame.pack(fill=BOTH, expand=1)

	canvas = Canvas(main_frame)
	canvas.pack(side=LEFT, fill=BOTH, expand=1)

	scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
	scrollbar.pack(side=RIGHT, fill=Y)

	canvas.configure(yscrollcommand=scrollbar.set)
	canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

	frame = Frame(canvas)
	canvas.create_window((0, 0), window=frame, anchor='nw')


def tooltip_show(e, for_tooltip):
	k = for_tooltip[e.widget]
	tooltip.config(text=k)


def tooltip_hide(e):
	tooltip.config(text='')


def choose_podcasts(podcasts):
	"""
	GUI screen
	:param podcasts: List of podcast
	:return:
	"""
	prepare_screen()
	selection = {k: [IntVar() for _ in range(len(podcasts[k]))] for k in podcasts}

	frames = []
	for_tooltip = {}
	for k in podcasts:
		Label(frame, text=k, font='Arial 15 bold').pack()
		frames.append(Frame(frame))
		frames[-1].pack()
		for episode, i in zip(podcasts[k], range(len(podcasts[k]))):
			box = Checkbutton(
				frames[-1],
				text=f"{episode['name']} - {episode['datePublished']}",
				variable=selection[k][i],
				anchor=W)
			for_tooltip[box] = episode['description']
			box.select()
			box.bind('<Enter>', lambda e: tooltip_show(e, for_tooltip))
			box.bind('<Leave>', tooltip_hide)
			box.grid(row=i, column=0, sticky=W)
	Button(root, text='Download', command=lambda: download(podcasts, selection)).pack()
	root.mainloop()


def move_podcasts(path):
	# TODO Work in progress. Currently dead code and storage for code to get audio length
	for file in os.listdir():
		name, ext = os.path.splitext(file)
		if ext != '.mp3':
			continue

		shutil.move(file, path + file)

		audio = MP3(file)
		duration = int(audio.info.length)
		hours = duration // 3600
		minutes = (duration // 60) % 60
		seconds = duration % 60

		new_name = f"{name}{ext}"
		os.rename(file, new_name)


def main():
	podcasts_urls = load_data()
	podcasts = {}
	for name, url in podcasts_urls.items():
		try:
			podcasts[name] = get_podcasts(url)
		except Exception as e:
			messagebox.showerror(message="Error occurred. Please check your internet connection and try again.")
			return None
	choose_podcasts(podcasts)


# if path_to_save != '':
# move_podcasts()


if __name__ == '__main__':
	root = Tk()
	root.title("BBC podcast downloader")
	root.iconbitmap('icon.ico')
	root.geometry("400x400")
	main()
