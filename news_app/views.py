from django.contrib.auth.models import User
from django.db.models import Q
from django.http import request
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DeleteView
from news_app.models import News, Category, Comment
from .forms import ContactForm, UpdateFormView, CreatingNewsForm, CommentForm
from config.custom_mixins import DispatchMixin
from config.custom_permissions import OnlyLoggedSuperUser
from hitcount.models import HitCount
from hitcount.views import HitCountMixin


class HomeView(View):
    def get(self, request):
        categories = Category.objects.all()
        news_list = News.published.all().order_by("-published_time")[:5]
        local_news = News.published.all().filter(category__name='Local').order_by("-published_time")[:6]
        abroad_news = News.published.all().filter(category__name='Abroad').order_by("-published_time")[:5]
        tech_news = News.published.all().filter(category__name='Technology').order_by("-published_time")[:5]
        sport_news = News.published.all().filter(category__name='Sport').order_by("-published_time")[:5]

        for new in news_list:
            if not new.image:
                News.delete(new)

        contex = {"categories": categories, "news_list": news_list, "local_news": local_news,
                  "abroad_news": abroad_news, "tech_news": tech_news, "sport_news": sport_news}
        return render(request, 'news_app/home.html', contex)


class NewsDetailView(DispatchMixin, View):
    def get(self, request, pk):
        news = get_object_or_404(News, pk=pk, status=News.Status.publish)
        contex = {}
        hit_count = HitCount.objects.get_for_object(news)
        hits = hit_count.hits
        contex['hitcount'] = {"pk": hit_count.pk}
        hit_count_response = HitCountMixin.hit_count(request, hit_count)

        if hit_count_response.hit_counted:
            hits += 1
            contex['hit_counted'] = hit_count_response.hit_counted
            contex['hit_message'] = hit_count_response.hit_message
            contex['total_hits'] = hits

        comment_form = CommentForm()
        comments = news.comments.all()
        contex = {"news": news, "comments": comments, "comment_form": comment_form,
                  "hit_count_response": hit_count_response}
        return render(request, "news_app/news_detail.html", contex)

    def post(self, request, pk):
        news = get_object_or_404(News, pk=pk, status=News.Status.publish)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.create(news=news, user=request.user, body=request.POST['body'])
            return redirect(reverse("news_detail", kwargs={"pk": news.pk}))
        return render(request, "news_detail.html", {"comment_form": comment_form, "news": news})


class ContactView(DispatchMixin, TemplateView):
    def get(self, request):
        form = ContactForm()
        contex = {"form": form}
        return render(request, 'news_app/contact.html', contex)

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_page')
        return render(request, 'news_app/contact.html', {'form': form})


class NewsMixin:
    def get_queryset(self):
        q = self.model.published.all().filter(category__name=self.category_name)
        return q


class LocalNews(NewsMixin, ListView):
    model = News
    template_name = 'news_app/local_news.html'
    context_object_name = 'local_news'
    category_name = 'Local'


class SportNews(NewsMixin, ListView):
    model = News
    template_name = 'news_app/sport_news.html'
    context_object_name = 'sport_news'
    category_name = 'Sport'


class AbroadNews(NewsMixin, ListView):
    model = News
    template_name = 'news_app/abroad_news.html'
    context_object_name = 'abroad_news'
    category_name = 'Abroad'


class TechNews(NewsMixin, ListView):
    model = News
    template_name = 'news_app/tech_news.html'
    context_object_name = 'tech_news'
    category_name = 'Technology'


class CreateNewsView(OnlyLoggedSuperUser, View):
    def get(self, request):
        creating_form = CreatingNewsForm()
        return render(request, 'crud/create.html', {"creating_form": creating_form})

    def post(self, request):
        creating_form = CreatingNewsForm(request.POST, request.FILES)
        if creating_form.is_valid():
            creating_form.save()
            return redirect('home_page')
        else:
            return render(request, 'crud/create.html', {"creating_form": creating_form})


class NewsUpdateView(OnlyLoggedSuperUser, View):
    def get(self, request, pk):
        news = get_object_or_404(News, id=pk)
        update_from = UpdateFormView(instance=news)
        contex = {"update_from": update_from, "news": news}
        return render(request, 'crud/edit.html', contex)

    def post(self, request, pk):
        news = get_object_or_404(News, id=pk)
        update_from = UpdateFormView(request.POST, request.FILES, instance=news)
        if update_from.is_valid():
            update_from.save()
            return redirect('news_detail', news.pk)
        return render(request, 'crud/edit.html', {"update_from": update_from, "news": news})


class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/delete.html'
    success_url = reverse_lazy('home_page')
    context_object_name = 'news'


class SearchNewsView(View):
    def get(self, request):
        query = request.GET.get('q')
        search_query = Q(body__icontains=query) | Q(title__icontains=query)
        news_list = News.objects.filter(search_query)
        return render(request, 'news_app/search_result.html', {"news_list": news_list})


class AdminsView(View):
    def get(self, request):
        admins = User.objects.filter(is_superuser=True)
        return render(request, 'news_app/admins.html', {"admins": admins})


def error_404_page_view(request):
    return render(request, 'news_app/404.html')
