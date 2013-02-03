from django.db import models

class NewsFeed(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return u"%d, %s" % (self.pk, self.name)

class NewsItem(models.Model):
	feed = models.ForeignKey(NewsFeed)
	title = models.CharField(max_length=255)
	link = models.CharField(max_length=255)
	date = models.DateTimeField(db_index=True)
	summary = models.TextField()

	def __unicode__(self):
		return u"%d, %s" % (self.pk, self.title)

	def to_json(self):
		out = dict()
		out["id"] = str(self.id)
		out["title"] = self.title
		out["date"] = self.date.isoformat()
		if self.link:
			out["link"] = self.link
		if self.summary:
			out["summary"] = self.summary
		return out
