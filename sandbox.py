import requests
import re
from fastapi.encoders import jsonable_encoder
from bs4 import BeautifulSoup

class VideoHomepage:
    def __init__(self,video_id,title,description,views,creator_name,creator_id,thumbnail):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.views = views
        self.creator_name = creator_name
        self.creator_id = creator_id
        self.thumbnail = thumbnail

class VideoPage:
    def __init__(self,title,description,views,likes,creator_id,video_uuid):
        self.title = title
        self.description = description
        self.views = views
        self.likes = likes
        self.creator_id = creator_id
        self.video_uuid = video_uuid

class VideoUserPage:
    def __init__(self,video_id,title,description,views,thumbnail):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.views = views
        self.thumbnail = thumbnail

class VideoRecommended:
    def __init__(self,video_id,title,creator_name,views,thumbnail):
        self.video_id = video_id
        self.title = title
        self.creator_name = creator_name
        self.views = views
        self.thumbnail = thumbnail

class UserData:
    def __init__(self, username, avatar_image, subscribers,account_views,about):
        self.username = username
        self.avatar_image = avatar_image
        self.subscribers = subscribers
        self.account_views = account_views
        self.about = about

def get_homepage():
    pages = []
    videos = []
    pages.append(requests.get("https://www.tracle.tv/?p=1"))
    pages.append(requests.get("https://www.tracle.tv/?p=2"))
    pages.append(requests.get("https://www.tracle.tv/?p=3"))
    for page in pages:
        soup = BeautifulSoup(page.content, 'html.parser')
        feed = soup.find_all(class_="feed__video")
        for i in feed:
            video_id = str(i.a['href'])[-11:]
            title = i.find(class_="feed__video__details__title").text
            description = i.find(class_="feed__video__details__description").text
            views = str(i.find(class_="feed__video__details__views").text)[:1]
            creator_name = i.find(class_="feed__video__details__channel").text
            creator_id = str(i.find(class_="feed__video__details__channel")['href'])[-11:]
            thumbnail = "https://tracle.tv/static/web/img/thumbnail_default.jpg" if i.img['src'] == "/static/web/img/thumbnail_default.jpg" else i.img['src']
            videos.append(VideoHomepage(video_id,title,description,views,creator_name,creator_id,thumbnail))

        videos = jsonable_encoder(videos)

    return videos

def get_video(video_id):
    videos = []
    page = requests.get("https://www.tracle.tv/watch?v={}".format(video_id))
    soup = BeautifulSoup(page.content,'html.parser')
    video_details = soup.find(class_="panel")
    title = soup.title.text
    description = video_details.find(class_="panel__details__description").text
    views = video_details.find(class_="panel__actions__views").text[:1]
    likes = video_details.find(id="like-counter").text
    creator_id = str(video_details.find(class_="panel__details__uploader").a['href'])[-11:]
    video_uuid = re.findall(r"b\-cdn\.net\/(.*)\/playlist\.m3u8", str(soup.find_all('script')[7]), re.MULTILINE)[0]
    video_in_page = VideoPage(title,description,views,likes,creator_id,video_uuid)
    # recommended videos
    feeds = soup.find_all(class_="secondary-feed__video")
    for video in feeds:
        video_id_rec = video['href'][-11:]
        title_rec = video.find(class_="secondary-feed__video__details__title").text
        creator_name_rec = video.find(class_="secondary-feed__video__details__channel").text
        views_rec = video.find(class_="secondary-feed__video__details__views").text[:1]
        thumbnail_rec = video.img['src']
        videos.append(VideoRecommended(video_id_rec,title_rec,creator_name_rec,views_rec,thumbnail_rec))

    return jsonable_encoder([video_in_page,videos])

def get_user_profile(creator_id):
    videos = []
    page = requests.get("https://www.tracle.tv/channel/{}/feed".format(creator_id))
    soup = BeautifulSoup(page.content, 'html.parser')
    username = soup.find(class_="channel__header__title").text
    avatar_image = soup.find(class_="channel__header__thumb")['src']
    subscribers = soup.find(id="sub-count").text
    account_views = soup.find(class_="channel__header__views").find("span").text
    about = soup.find(class_="channel-profile__about").text
    user_page = UserData(username,avatar_image,subscribers,account_views,about)
    # video user
    feeds = soup.find_all(class_="activity-feed__item")
    for video in feeds:
        video_id = video.find(class_="title")['href'][-11:]
        title = video.find(class_="title").text
        description = video.find(class_="description").text
        views = video.find(class_="views").text[:1]
        thumbnail = video.img['src']
        videos.append(VideoUserPage(video_id,title,description,views,thumbnail))

    return jsonable_encoder([user_page, videos])