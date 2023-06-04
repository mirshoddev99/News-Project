from django import forms
from .models import Contact, News, Comment


class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 600px;'}))

    class Meta:
        model = Comment
        fields = ['body']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ""


class CreatingNewsForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    title_uz = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    title_en = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    body_uz = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    body_en = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = News
        fields = ['title', 'title_uz', 'title_en', 'body', 'body_uz', 'body_en', 'image', 'category', 'status']


class UpdateFormView(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = News
        fields = ['title', 'body', 'image', 'category']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'body']
