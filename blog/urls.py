from django.urls import path

from blog import views


# refer to these urls using app_name in the include
app_name = 'blog'

urlpatterns = [
    # post views
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>', views.post_detail,
         name='post_detail'),
]
