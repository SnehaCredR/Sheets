from django.conf.urls import url

from . import views

app_name = "sheets_io"

urlpatterns = [
	url(r'auth/', views.auth, name="auth"),
	url(r'home/', views.render_index, name="render_index"),
	url(r'index/', views.index, name="index")
]