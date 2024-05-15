
from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError

from .models import *


class AddPostForm(forms.ModelForm):
    """Форма для добавления поста"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Категория не выбрана"

    class Meta:
        model = Bike
        fields = ['title', 'content', 'photo', 'cat', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self) -> str:  # Валидация
        """Валидация поля заголовка"""

        title = self.cleaned_data['title']
        if len(title) > 20:
            raise ValidationError('Длина превышает 200 символов')
        return title


class ContactForm(forms.Form):
    """Форма обратной связи"""

    name = forms.CharField(label='Имя', max_length=255)
    email = forms.EmailField(label='Email')
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 10}))
    captcha = CaptchaField()


class AddRateForm(forms.ModelForm):
    """Форма для установки рейтинга поста авторизованным пользователем"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rate'].label = 'Оценить пост'

    class Meta:
        model = UserPostRelation
        fields = ['rate']


    def clean_rate(self) -> int:
        """Валидация поля оценки."""

        rate = self.cleaned_data['rate']
        if not rate:
            raise forms.ValidationError('Выберите оценку из списка')
        return rate




