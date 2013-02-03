import time
import json
import urllib2
import threading
import jwt

def make_api_token(realm, key):
    claim = { "iss": realm, "exp": int(time.time()) + 600 }
    return jwt.encode(claim, key)

def publish(realm, key, channel, id, prev_id, value):
    url = "http://api.fanout.io/realm/%s/publish/%s/" % (realm, channel)

    headers = dict()
    headers["Authorization"] = "Bearer %s" % make_api_token(realm, key)
    headers["Content-Type"] = "application/json"

    item = dict()
    item["id"] = id
    if prev_id:
        item["prev-id"] = prev_id
    item["http-response"] = value
    content = dict()
    content["items"] = [item]
    content_raw = json.dumps(content).encode("utf-8")

    try:
        urllib2.urlopen(urllib2.Request(url, content_raw, headers))
    except Exception as e:
        print "warning: failed to publish: " + e.message

def publish_async(realm, key, channel, value):
    thread = threading.Thread(target=publish, args=(realm, key, channel, value))
    thread.daemon = True
    thread.start()
