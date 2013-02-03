import datetime
from base64 import b64decode
import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
import dateutil.parser
from models import NewsFeed, NewsItem
import fanout

def fanout_publish(channel, id, prev_id, http_response):
	fanout.publish(settings.FANOUT_REALM, b64decode(settings.FANOUT_REALM_KEY), channel, id prev_id, http_response)

def format_date(d):
	h = d.time().hour
	if h > 12:
		h -= 12
		suffix = "pm"
	else:
		suffix = "am"

	return "%d:%02d %s" % (h, d.time().minute, suffix)

def index(request):
	if request.method == "GET":
		feed_id = request.GET.get("feed")
		if not feed_id:
			feed_id = 1

		try:
			feed = NewsFeed.objects.get(id=feed_id)
		except NewsFeed.DoesNotExist:
			return HttpResponseNotFound("Not Found: no such feed id\n")

		items = NewsItem.objects.filter(feed=feed).order_by("-id")[:10]

		first_item = None
		citems = list()
		for i in items:
			if not first_item:
				first_item = i
			ci = dict()
			ci["title"] = i.title
			ci["date"] = format_date(i.date)
			ci["link"] = i.link
			ci["summary"] = i.summary
			citems.append(ci)
		context = dict()
		context["feed"] = "\"" + str(feed.id) + "\""
		if len(items) > 0:
			context["last_id"] = "\"" + str(first_item.id) + "\""
		else:
			context["last_id"] = "null"
		context["items"] = citems
		resp = render_to_response("newsfeed/index.html", context, context_instance=RequestContext(request))
		resp["Cache-Control"] = "no-cache"
		return resp
	else:
		return HttpResponseNotAllowed(["GET"])

def items_html(request):
	# TODO: widget template
	if request.method == "GET":
		feed_id = request.GET.get("feed")
		if not feed_id:
			return HttpResponseBadRequest("Bad Request: feed id required\n")

		try:
			feed = NewsFeed.objects.get(id=feed_id)
		except NewsFeed.DoesNotExist:
			return HttpResponseNotFound("Not Found: no such feed id\n")

		items = NewsItem.objects.filter(feed=feed).order_by("-id")[:10]

		citems = list()
		for i in items:
			ci = dict()
			ci["title"] = i.title
			ci["date"] = format_date(i.date)
			ci["link"] = i.link
			ci["summary"] = i.summary
			citems.append(ci)
		context = dict()
		context["items"] = citems
		return render_to_response("newsfeed/index.html", context, context_instance=RequestContext(request))
	else:
		return HttpResponseNotAllowed(["GET"])

def items_json(request):
	if request.method == "GET":
		feed_id = request.GET.get("feed")
		if not feed_id:
			return HttpResponseBadRequest("Bad Request: feed id required\n")

		try:
			feed = NewsFeed.objects.get(id=feed_id)
		except NewsFeed.DoesNotExist:
			return HttpResponseNotFound("Not Found: no such feed id\n")

		qmax = request.GET.get("max")
		if qmax is not None:
			try:
				qmax = int(qmax)
			except:
				return HttpResponseBadRequest("Bad Request: max must be a positive integer\n")

			if qmax <= 0:
				return HttpResponseBadRequest("Bad Request: max must be a positive integer\n")
		else:
			qmax = 10

		if qmax > 200:
			qmax = 200

		since = request.GET.get("since")
		if since is not None:
			if not since.startswith("id:"):
				return HttpResponseBadRequest("Bad Request: since position spec must be \"id\"\n")

			idstr = since[3:]
			try:
				since_id = int(idstr)
			except:
				return HttpResponseBadRequest("Bad Request: invalid since id\n")

			items = NewsItem.objects.filter(feed=feed, id__gt=since_id).order_by("id")[:qmax]
		else:
			items = NewsItem.objects.filter(feed=feed).order_by("id")[:qmax]
			since_id = None

		if len(items) > 0:
			citems = list()
			for i in items:
				citems.append(i.to_json())
			out = dict()
			out["items"] = citems
			return HttpResponse(json.dumps(out) + "\n")
		else:
			channel = dict()
			channel["name"] = "feed-" + str(feed.id)
			if since_id:
				channel["prev-id"] = str(since_id)

			hold = dict()
			hold["mode"] = "response"
			hold["channels"] = [channel]

			# this is what is released on timeout
			headers = dict()
			headers["Cache-Control"] = "no-cache"
			response = dict()
			response["headers"] = headers
			response["body"] = "{\"items\": []}\n"

			instruct = dict()
			instruct["hold"] = hold
			instruct["response"] = response

			return HttpResponse(json.dumps(instruct), content_type="application/fo-instruct")
	else:
		return HttpResponseNotAllowed(["GET"])

def add(request):
	if request.method == "POST":
		feed_id = request.POST.get("feed")
		title = request.POST.get("title")
		link = request.POST.get("link")
		summary = request.POST.get("summary")
		date = request.POST.get("date")

		if not feed_id or not title or not summary:
			return HttpResponseBadRequest("Bad Request: must include feed, title, and summary\n")

		if date:
			try:
				date = dateutil.parser.parse(date)
			except:
				return HttpResponseBadRequest("Bad Request: invalid date format\n")
		else:
			date = datetime.datetime.now()

		if not link:
			link = ""

		try:
			feed = NewsFeed.objects.get(id=feed_id)
		except NewsFeed.DoesNotExist:
			return HttpResponseNotFound("Not Found: no such feed id\n")

		item = NewsItem(feed=feed, title=title, link=link, date=date, summary=summary)
		item.save()

		# get previous item id
		try:
			prev_items = NewsItem.objects.filter(feed=feed, id__lt=item.id).order_by("-id")[:1]
			if len(prev_items) > 0:
				prev_id = prev_items[0].id)
		except:
			prev_id = None

		out = dict()
		if prev_id:
			out["prev_id"] = str(prev_id)
		out["items"] = [item.to_json()]
		hr = dict()
		hr["body"] = json.dumps(out) + "\n"

		fanout_publish("feed-" + str(feed.id), str(item.id), str(prev_id), hr)

		return HttpResponse("Posted\n")
	else:
		return HttpResponseNotAllowed(["POST"])
