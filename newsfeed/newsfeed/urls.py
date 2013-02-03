from django.conf.urls.defaults import patterns

urlpatterns = patterns('newsfeed.views',
	(r'^$', 'index'),
	(r'items.html$', 'items_html'),
	(r'items/$', 'items_json'),
	(r'add/$', 'add'),
)
