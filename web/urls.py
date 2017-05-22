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
    # url(r'^accounts/logout/$', views.logout_view(), name='logout'),
]