from django.shortcuts import render,redirect
import datetime
from django.contrib.auth.decorators import login_required
import random

from .models import PostModel, CategoryModel,CommentModel
from userapp.models import UserModel
from django.contrib.auth.models import User

from .forms import AddPostForm,AddCommentForm



def get_featured_post(posts):
    if len(posts)==0:
        return None
    else:
        num_of_posts=len(posts)
        featured_post_index= random.randint(0,num_of_posts-1)
        return posts[featured_post_index]


def index(request):
    posts = PostModel.objects.all().order_by('posted_on','title','posted_by')[:10]
    categories = CategoryModel.objects.all()[:5]
    context = {
        'posts' : posts,
        'categories': categories,
        'featured_post': get_featured_post(posts) if len(posts) > 0 else None
    }
    return render(request, 'newsapp/index.html', context)

def detail(request, id):
    post = PostModel.objects.filter(id=id).first()
    categories = CategoryModel.objects.all()[:5]
    context = {
        'post': post,
        'categories': categories
    }
    return render(request, 'newsapp/detail.html', context)

def categorynews(request, id):
    category = CategoryModel.objects.filter(id=id).first()
    if category:
        posts = PostModel.objects.filter(category=category)
        categories = CategoryModel.objects.all()[:5]
        context = {
            'posts': posts,
            'categories': categories,
            'featured_post' : posts[0] if len(posts) > 0 else None,
            'current_category_id':id
        }
        return render(request, 'newsapp/index.html', context)
    else:
        return render(request, 'newsapp/error404.html')


@login_required
def add_post_view(request):
    if request.method=='POST':
        form=AddPostForm(request.POST,request.FILES)
        if form.is_valid():
            #now add logic to add the form
            post=form.save(commit=False)
            django_user=User.objects.filter(id=request.user.id).first()
            current_user=UserModel.objects.filter(auth=django_user).first()
            post.posted_by=current_user
            post.save()
            return redirect('index')
        else:
            #this means the form as errors
            return render(request,'newsapp/add_post.html',{'form':form})
    else:
        form=AddPostForm()
        categories = CategoryModel.objects.all()[:5]
        context={
            'categories': categories,
            'form':form
        }
        return render(request,'newsapp/add_post.html',context)

@login_required
def delete_post_view(request,id):
    post=PostModel.objects.filter(id=id).first()
    if post:
        logged_in_user_id=request.user.id 
        post_user_id=post.posted_by.auth.id
        if logged_in_user_id==post_user_id:
            #to delete the post
            post.delete()
            return redirect('index')

    else:
        #theres no post with that id
        return render(request,'newsapp/error404.html')


@login_required
def edit_post_view(request,id):
    if request.method=='POST':
            form=AddPostForm(request.POST,request.FILES)
            post=PostModel.objects.filter(id=id).first()
            if post:
                current_user_id=request.user.id 
                post_user_id=post.posted_by.auth.id
                if current_user_id==post_user_id:
                    form=AddPostForm(request.POST,files=request.FILES,instance=post)
                    if form.is_valid():
                        form.save()
                        return redirect('detail',post.id)
                    else:
                        return render(request,'newsapp/edit_post.html',{'form':form})
                else:
                    return render(request,'newsapp/error404.html')
            else:
                 return render(request,'newsapp/error404.html')
    else:
            post = PostModel.objects.filter(id=id).first()
            if post:
                form=AddPostForm(instance=post)
                return render(request,'newsapp/edit_post.html',{'form':form})
            else:
                return render(request,'newsapp/error404.html')


def search_view(request):
    query=request.GET.get('query')
    resultsintitle=PostModel.objects.filter(title__icontains=query)
    resultsincontent=PostModel.objects.filter(content__icontains=query)
    results=(resultsintitle|resultsincontent).distinct()
    context={
        'posts':results,
        'search_query':query
    }
    return render(request,'newsapp/search_results.html',context)

@login_required
def add_comment_view(request,id):
    if request.method=='POST':
        form=AddCommentForm(request.POST,request.FILES)
        post=PostModel.objects.filter(id=id).first()
        if form.is_valid():
            #now add logic to add the form
            comment=form.save(commit=False)
            django_user=User.objects.filter(id=request.user.id).first()
            current_user=UserModel.objects.filter(auth=django_user).first()
            comment.commented_by=current_user
            comment.parent_post=PostModel.objects.filter(id=id).first()
            comment.save()
            return redirect('detail',post.id)
        else:
            #this means the form as errors
            return render(request,'newsapp/add_comment.html',{'form':form})
    else:
        form=AddCommentForm()
        
        context={
            'form':form
        }
        return render(request,'newsapp/add_comment.html',context)
        

@login_required
def delete_comment_view(request,id):
    comment=CommentModel.objects.filter(id=id).first()
    if comment:
        logged_in_user_id=request.user.id 
        comment_user_id=comment.commented_by.auth.id
        if logged_in_user_id==comment_user_id:
            #to delete the post
            comment.delete()
            return redirect('detail',comment.parent_post.id)

    else:
        #theres no post with that id
        return render(request,'newsapp/error404.html')
        
@login_required
def edit_comment_view(request,id):
    if request.method=='POST':
            form=AddCommentForm(request.POST,request.FILES)
            comment=CommentModel.objects.filter(id=id).first()
            post = PostModel.objects.filter(id=id).first()
            if comment:
                current_user_id=request.user.id 
                comment_user_id=comment.commented_by.auth.id
                if current_user_id==comment_user_id:
                    form=AddCommentForm(request.POST,files=request.FILES,instance=comment)
                    if form.is_valid():
                        form.save()
                        return redirect('detail',comment.parent_post.id)
                    else:
                        return render(request,'newsapp/edit_comment.html',{'form':form})
                else:
                    return render(request,'newsapp/error404.html')
            else:
                 return render(request,'newsapp/error404.html')
    else:
            comment= CommentModel.objects.filter(id=id).first()
            if comment:
                form=AddCommentForm(instance=comment)
                return render(request,'newsapp/edit_comment.html',{'form':form})
            else:
                return render(request,'newsapp/error404.html')

            
        
       
     
              
