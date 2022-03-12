from fastapi import FastAPI
from deta import Deta
import time
import sandbox

app = FastAPI()

deta = Deta('deta_key')
db = deta.Base('base_name')

# scuffed repetetive caching code, abstract via a function later™
# add tracle online check someday™
@app.get("/homepage/")
def homepage():
    currentcache = db.get("homepage-cached")
    if not currentcache:
        homepage = sandbox.get_homepage()
        db.put([homepage,time.time() + 3600],"homepage-cached")
    if currentcache['value'][1] > time.time():
        homepage = currentcache['value'][0]
    else:
        homepage = sandbox.get_homepage()
        db.put([homepage,time.time() + 3600],"homepage-cached")

    return homepage

@app.get('/video/')
def video(video_id):
    currentcache = db.get("video-{}".format(video_id))
    if not currentcache:
        cachedvideo = sandbox.get_video(video_id)
        db.put([cachedvideo,time.time() + 3600],"video-{}".format(video_id))
    elif currentcache['value'][1] > time.time():
        cachedvideo = currentcache['value'][0]
    else:
        cachedvideo = sandbox.get_video(video_id)
        db.put([cachedvideo,time.time() + 3600],"video-{}".format(video_id))

    return cachedvideo

@app.get('/userpage/')
def userpage(creator_id):
    currentcache = db.get("user-{}".format(creator_id))
    if not currentcache:
        cacheduser = sandbox.get_user_profile(creator_id)
        db.put([cacheduser,time.time() + 3600],"user-{}".format(creator_id))
    elif currentcache['value'][1] > time.time():
        cacheduser = currentcache['value'][0]
    else:
        cacheduser = sandbox.get_user_profile(creator_id)
        db.put([cacheduser,time.time() + 3600],"user-{}".format(creator_id))

    return cacheduser
