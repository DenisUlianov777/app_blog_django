from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMessage
from django.db.models import (Avg, Case, Count, Exists, OuterRef, Prefetch, Q,
                              QuerySet, When)
from django.forms import Form
from django.http import (HttpResponse, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView)

from .forms import *
from .models import *
from .utils import DataMixin, get_initial_rate


class Home(DataMixin, ListView):
    """Класс представления домашней страницы"""

    template_name = 'bike_app/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        context['cat_selected'] = 0
        return context

    def get_queryset(self) -> QuerySet:
        queryset = cache.get('home_cache')
        if not queryset:
            queryset = Bike.published.all().annotate(
                count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
                rating=Avg('userpostrelation__rate')
            ).select_related('cat').prefetch_related('tags').order_by('-created')

            if self.request.user.is_authenticated:
                queryset = queryset.annotate(
                    liked_by_user=Exists(
                        UserPostRelation.objects.filter(
                            bike=OuterRef('pk'),
                            auth_user=self.request.user,
                            like=True
                        )
                    )
                )
            cache.set('home_cache', queryset, timeout=15)
        return queryset


@login_required
def reader_like(request, pk: int) -> HttpResponseRedirect:
    """Функция представления оценки(лайка) авторизованного пользователя"""
    obj, created = UserPostRelation.objects.get_or_create(auth_user=request.user, bike_id=pk)
    if created is False:
        if obj.like is False:
            obj.like = True
        else:
            obj.like = False
    else:
        obj.like = True
    obj.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AddPost(LoginRequiredMixin, CreateView):
    """Класс представления страницы для добавления статьи авторизованным пользователем"""

    form_class = AddPostForm
    template_name = 'bike_app/addpage.html'
    login_url = reverse_lazy('users:login')
    extra_context = {
        'title': 'Добавление статьи',
    }

    def form_valid(self, form: Form) -> HttpResponse:
        obj = form.save(commit=False)
        obj.auth_user = self.request.user
        return super().form_valid(form)


class UpdatePost(UserPassesTestMixin, UpdateView):
    """Класс представления для страницы редактирования поста"""
    model = Bike
    fields = ['title', 'slug', 'content', 'photo', 'is_published', 'cat', 'tags']
    template_name = 'bike_app/updatepage.html'
    extra_context = {
        'title': 'Редактирование статьи',
    }

    def test_func(self) -> bool:
        """Проверка, является ли текущий пользователь автором поста"""

        obj = self.get_object()
        return obj.auth_user == self.request.user


class DeletePost(UserPassesTestMixin, DeleteView):
    """Класс представления для удаления поста"""
    model = Bike
    template_name = 'bike_app/deletepage.html'
    success_url = reverse_lazy('home')
    extra_context = {
        'title': 'Удаление статьи',
    }

    def test_func(self) -> bool:
        """Проверка, является ли текущий пользователь автором поста"""

        obj = self.get_object()
        return obj.auth_user == self.request.user


class ContactFormView(SuccessMessageMixin, FormView):
    """Класс для обработки формы обратной связи"""
    form_class = ContactForm
    template_name = 'bike_app/contact.html'
    extra_context = {'title': "Обратная связь"}
    success_url = reverse_lazy('home')
    success_message = 'Спасибо за обратную связь! Администратор скоро с Вами свяжется'

    def form_valid(self, form):
        email_message = EmailMessage(
            'Feedback from {}'.format(form.cleaned_data['name']),
            form.cleaned_data['message'],
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],  # Замените на свой адрес электронной почты
            reply_to=[form.cleaned_data['email']],  # Добавляем адрес отправителя в адрес для ответа
        )
        email_message.send()
        return super().form_valid(form)


class ShowPost(DetailView):
    """Класс представления страницы поста"""

    form_class = AddRateForm
    template_name = 'bike_app/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['post']
        context['default_img'] = settings.DEFAULT_POST_IMAGE
        context['rate_form'] = self.form_class(initial={'rate': get_initial_rate(self)})
        return context

    def get_object(self, queryset=None) -> Bike:
        return get_object_or_404(Bike.published, slug=self.kwargs[self.slug_url_kwarg])

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """Функция для установки оценки(рейтинга) авторизованным пользователем"""

        form = self.form_class(request.POST)
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        if form.is_valid():
            rate = form.cleaned_data["rate"]
            UserPostRelation.objects.update_or_create(
                auth_user_id=self.request.user.id,
                bike_id=form.data["post_id"],
                defaults={'rate': rate}
            )
            context['rate_form'] = self.form_class(initial={'rate': rate})
            return render(request, self.template_name, context)
        else:
            context['rate_form'] = form  # Передача формы снова в контекст
            return render(request, self.template_name, context)


class BikeCategory(DataMixin, ListView):
    """Класс представления постов отфильтровванных по категории"""

    template_name = 'bike_app/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        cat = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        context['title'] = 'Категория - ' + cat.name
        context['cat_selected'] = cat.id
        return context

    def get_queryset(self) -> QuerySet:
        queryset = Bike.published.filter(cat__slug=self.kwargs['cat_slug']).annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')
        ).select_related('cat').prefetch_related('tags').order_by('-created')

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                liked_by_user=Exists(
                    UserPostRelation.objects.filter(
                        bike=OuterRef('pk'),
                        auth_user=self.request.user,
                        like=True
                    )
                )
            )
        return queryset


class BikeTags(DataMixin, ListView):
    """Класс представления постов отфильтровванных по тегу"""

    template_name = 'bike_app/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        t_obj = get_object_or_404(Tags, slug=self.kwargs['tag_slug'])
        context['title'] = 'Тег: ' + t_obj.tag
        context['cat_selected'] = None
        return context

    def get_queryset(self) -> QuerySet:
        queryset = Bike.published.filter(tags__slug=self.kwargs['tag_slug']).annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')
        ).select_related('cat').prefetch_related('tags').order_by('-created')

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                liked_by_user=Exists(
                    UserPostRelation.objects.filter(
                        bike=OuterRef('pk'),
                        auth_user=self.request.user,
                        like=True
                    )
                )
            )
        return queryset


def page_not_found(request, exception) -> HttpResponseNotFound:
    """Функция представления несуществующей страницы"""
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
