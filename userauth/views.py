from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Notification


# ----------------------------------------------------
# Helper Function: Create Notification
# ----------------------------------------------------
def create_notification(sender, user, notification_type, post=None, text_preview=''):
    # Prevent notifying yourself
    if sender != user:
        Notification.objects.create(
            sender=sender,
            user=user,
            notification_type=notification_type,
            post=post,
            text_preview=text_preview
        )


# ----------------------------------------------------
# Auth Views
# ----------------------------------------------------

# 1. Signup View
def signup(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        emailid = request.POST.get('emailid')
        pwd = request.POST.get('pwd')

        # Check if username already exists
        if User.objects.filter(username=fnm).exists():
            invalid = "User Already Exists"
            return render(request, 'signup.html', {'invalid': invalid})

        try:
            # Create user and profile
            my_user = User.objects.create_user(username=fnm, email=emailid, password=pwd)
            Profile.objects.create(user=my_user, id_user=my_user.id)
            
            # Auto login after signup
            auth_login(request, my_user)
            return redirect('/')
        except Exception as e:
            return render(request, 'signup.html', {'invalid': 'An error occurred during signup.'})

    return render(request, 'signup.html')


# 2. Login View
def login_view(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        pwd = request.POST.get('pwd')

        user = authenticate(request, username=fnm, password=pwd)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            invalid = "Invalid Username or Password"
            return render(request, 'login.html', {'invalid': invalid})

    return render(request, 'login.html')


# 3. Logout View
def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ----------------------------------------------------
# Main Feed & Features
# ----------------------------------------------------

# 4. Home View (Renders main.html)
@login_required(login_url='login')
def home(request):
    # Retrieve logged-in user profile
    user_profile = Profile.objects.filter(user=request.user).first()
    
    # Retrieve all posts in descending order (newest first)
    posts = Post.objects.all().order_by('-created_at')

    return render(request, 'main.html', {
        'profile': user_profile,
        'posts': posts
    })


# 5. Upload Post View
@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption')

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    return redirect('/')


# 6. Like Post View (Includes Notification Trigger)
@login_required(login_url='login')
def like_post(request, post_id):
    username = request.user.username
    post = get_object_or_404(Post, id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username)

    if not like_filter.exists():
        # Add Like
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()

        # Send Notification to Post Owner
        post_owner = User.objects.filter(username=post.user).first()
        if post_owner:
            create_notification(
                sender=request.user,
                user=post_owner,
                notification_type=1,  # 1 = Like
                post=post
            )
    else:
        # Remove Like (Unlike)
        like_filter.delete()
        post.no_of_likes = max(0, post.no_of_likes - 1)
        post.save()

    return redirect(f'/#{post_id}')


# 7. Notifications Page View
@login_required(login_url='login')
def notifications_view(request):
    # Fetch notifications for current user
    notifications = Notification.objects.filter(user=request.user).order_by('-date')
    
    # Mark unread notifications as seen
    Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)

    return render(request, 'notifications.html', {'notifications': notifications})


# 8. User Search View
@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        username_object = User.objects.filter(username__icontains=username)

        username_profile_list = []
        for user in username_object:
            profile = Profile.objects.filter(user=user).first()
            if profile:
                username_profile_list.append(profile)

        return render(request, 'search_results.html', {'username_profile_list': username_profile_list, 'query': username})
    return redirect('/')


# 9. Profile View & Follow Toggle
@login_required(login_url='login')
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = Profile.objects.filter(user=user_object).first()
    user_posts = Post.objects.filter(user=pk).order_by('-created_at')
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    # Check if logged-in user is already following this user
    is_following = FollowersCount.objects.filter(follower=follower, user=user).exists()

    if request.method == 'POST':
        if not is_following:
            # Follow User
            FollowersCount.objects.create(follower=follower, user=user)
            create_notification(
                sender=request.user,
                user=user_object,
                notification_type=3  # 3 = Follow
            )
        else:
            # Unfollow User
            FollowersCount.objects.filter(follower=follower, user=user).delete()

        return redirect(f'/profile/{pk}')

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'is_following': is_following,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

# 10. Explore View (Displays public feed/all posts)
@login_required(login_url='login')
def explore(request):
    # Retrieve all posts ordered by newest first
    posts = Post.objects.all().order_by('-created_at')
    
    # Retrieve logged-in user's profile
    user_profile = Profile.objects.filter(user=request.user).first()

    return render(request, 'explore.html', {
        'posts': posts,
        'profile': user_profile
    })
    
# views.py
@login_required(login_url='login')
def edit_profile(request):
    user_profile = Profile.objects.filter(user=request.user).first()

    if request.method == 'POST':
        # Check if a new profile image was uploaded
        if request.FILES.get('image'):
            user_profile.profileimg = request.FILES.get('image')
        
        # Get bio and location from the form
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')

        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect(f'/profile/{request.user.username}')

    return redirect('/')

import os
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from django.db.models import Q
from .models import DirectMessage

@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Backend ownership check
    if post.user == request.user.username:
        # Optionally delete image file from storage
        if post.image:
            if os.path.isfile(post.image.path):
                os.remove(post.image.path)
                
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this post.")

    # Redirect back to referring page or home
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='login')
def inbox(request):
    all_messages = DirectMessage.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')

    chat_users = []
    for msg in all_messages:
        other_user = msg.recipient if msg.sender == request.user else msg.sender
        if other_user not in chat_users:
            chat_users.append(other_user)

    return render(request, 'inbox.html', {'chat_users': chat_users})


@login_required(login_url='login')
def chat_detail(request, username):
    recipient = get_object_or_404(User, username=username)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            DirectMessage.objects.create(sender=request.user, recipient=recipient, body=body)
            return redirect('chat-detail', username=username)

    messages_list = DirectMessage.objects.filter(
        (Q(sender=request.user) & Q(recipient=recipient)) |
        (Q(sender=recipient) & Q(recipient=request.user))
    ).order_by('timestamp')

    messages_list.filter(recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'chat.html', {
        'recipient': recipient,
        'messages': messages_list,
    })
