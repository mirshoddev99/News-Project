from django.urls import path

from .views import NewsDetailView, error_404_page_view, ContactView, HomeView, LocalNews, AbroadNews, SportNews, \
    TechNews, NewsUpdateView, NewsDeleteView, CreateNewsView, AdminsView, SearchNewsView

urlpatterns = [
    path('', HomeView.as_view(), name='home_page'),
    path('news/create/', CreateNewsView.as_view(), name='creating_news'),
    path('news/<pk>/edit-news/', NewsUpdateView.as_view(), name='update_news'),
    path('news/<pk>/delete-news/', NewsDeleteView.as_view(), name='delete_news'),
    path('news/<pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('contact-us/', ContactView.as_view(), name='contact'),
    path('local-news/', LocalNews.as_view(), name='local_news'),
    path('abroad-news/', AbroadNews.as_view(), name='abroad_news'),
    path('sport-news/', SportNews.as_view(), name='sport_news'),
    path('tech-news/', TechNews.as_view(), name='tech_news'),
    path('error-page/', error_404_page_view, name='error_page'),
    path('admins-page/', AdminsView.as_view(), name='admin_pages'),
    path('search-news/', SearchNewsView.as_view(), name='searching_news'),
]

