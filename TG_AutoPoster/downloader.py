import requests
import time
import os
import youtube_dl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


headers = {
    'user-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}


def get_video(link, name):
    ydl_opts = {'outtmpl': f'{name}.mp4'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:

        ydl.download([link])
    return ydl_opts['outtmpl']


def get_n_save(song_name="Rammstein"):
    r = requests.Session()

    params = {'search': song_name, 'time': time.ctime()}
    try:
        response = r.get(
            "http://vk.music7s.cc/api/search.php?", headers=headers, params=params, verify=False)
        if response.status_code == 200:
            return save_song(response.json()['items'][0]['url'], song_name.replace(' ', '_') + '.mp3')

        else:
            return False
    except:
        return False


def save_song(link, file_name):
    try:
        r = requests.Session()
        response = r.get(
            f"https://vk.music7s.cc{link}", headers=headers, verify=False)
        if response.status_code == 200:
            try:
                file = open(file_name, 'wb')
                file.write(response.content)

                file.close()
                return os.path.abspath(file_name)
            except:
                return False
        else:
            return False
    except:
        return False
