from .models import News, Category


def latest_news(request):
    last_news = News.published.all().order_by('-published_time')[:6]
    contex = {"last_news": last_news}
    return contex


def categories(request):
    categories = Category.objects.all()
    contex = {'categories': categories}
    return contex
