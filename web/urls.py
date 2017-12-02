from django.conf.urls import url

from . import views

# urlpatterns = [
#     url(r'^$', views.index, name='index'),
# ]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^table/$', views.table, name='table'),
    url(r'^bar_graph/$', views.bar_graph, name='bar_graph'),
    url(r'^inst_graph/$', views.inst_graph, name='inst_graph'),
    url(r'^test/$', views.test_view, name='test'),
    url(r'^form/$', views.form_view, name='form'),
    url(r'^form_test/$', views.form_test_view, name='form_test'),
    # url(r'^csv/([0-9]{4})/([0-9]{2})/$', views.month_csv, name='data2csv'),
    url(r'^csv/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_csv, name='data2csv'),
    # url(r'^accounts/logout/$', views.logout_view(), name='logout'),
]