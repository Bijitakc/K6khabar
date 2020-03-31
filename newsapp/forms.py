from django.forms import ModelForm
from .models import PostModel,CommentModel


class AddPostForm(ModelForm):
    class Meta:
        model=PostModel
        fields=['title','content','header_image','category']

class AddCommentForm(ModelForm):
    class Meta:
        model=CommentModel
        fields=['content']
        