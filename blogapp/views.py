from django.shortcuts import render,HttpResponse,get_object_or_404,redirect,Http404
from .models import author,category,article,comment
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
from .forms import CreateForm,RegisterForm,AuthorForm,CommentForm,CategoryForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from .token import activation_token
# Create your views here.

class index(View):
    def get(self,request):
        post = article.objects.all()
        search = request.GET.get('q')
        if search:
            post = post.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search) |
                Q(category__name__icontains=search)

            )

        paginator = Paginator(post, 4)
        pa = request.GET.get('page')
        total_article = paginator.get_page(pa)
        context = {"post": total_article}
        return render(request, "index.html", context)



class getauthor(View):
    template="profile.html"
    def get(self,request,name):
        post_author = get_object_or_404(User, username=name)
        auth = get_object_or_404(author, name=post_author.id)
        post = article.objects.filter(article_author=auth.id)
        context = {"auth": auth, "post": post}
        return render(request,self.template, context)


class getsingle(View):
    def get(self,request,id):
        post = get_object_or_404(article, pk=id)
        first = article.objects.first()
        last = article.objects.last()
        related = article.objects.filter(category=post.category).exclude(id=id)[:4]
        comments = comment.objects.filter(post=id)
        form = CommentForm
        context = {"post": post, "first": first, "last": last, "related": related, "form": form, "comments": comments}
        return render(request, "single.html", context)

    def post(self,request,id):
        post = get_object_or_404(article, pk=id)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.post = post
            instance.save()
            return redirect("blog:single_post",id=id)



class getTopic(View):
    def get(self, request, name):
        cat = get_object_or_404(category,name=name)
        post = article.objects.filter(category=cat.id)
        context={"post":post,"cat":cat}
        return render(request,"category.html",context)

class getLogin(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("blog:index")
        else:
            return render(request,"login.html")


    def post(self,request):
        user = request.POST.get("user")
        password = request.POST.get("pass")
        auth = authenticate(request, username=user, password=password)
        if auth is not None:
            login(request, auth)
            return redirect("blog:index")
        else:
            messages.add_message(request, messages.ERROR, "Username or password mismatch.")
            return redirect("blog:login")



class getLogout(View):
    def get(self, request):
        logout(request)
        return redirect("blog:index")

class getCreate(View):
    def get(self, request):
        if request.user.is_authenticated:
            u = get_object_or_404(author,name=request.user.id)
            form = CreateForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.article_author = u
                instance.save()
                return redirect('index')

            return render(request, "create.html", {"form": form})
        return redirect('login')

class getProfile(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User,id=request.user.id)
            author_profile = author.objects.filter(name=user.id)
            if author_profile:
                authoruser = get_object_or_404(author,name=request.user.id)
                post = article.objects.filter(article_author=authoruser.id)
                return render(request, 'loged_in_profile.html', {"post": post, "auth": authoruser})

            else:
                form = AuthorForm(request.POST or None,request.FILES or None)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.name = user
                    instance.save()
                    return redirect('profile')
                return render(request,'createauthor.html',{"form":form})

        return redirect(request,'login')

class getUpdate(View):
    def get(self, request, upid):
        if request.user.is_authenticated:
            u = get_object_or_404(author,name=request.user.id)
            post = get_object_or_404(article,id=upid)
            form = CreateForm(request.POST or None, request.FILES or None,instance=post)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.article_author = u
                instance.save()
                return redirect('profile')

            return render(request, "create.html", {"form": form})
        return redirect('login')

class getDelete(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            post = get_object_or_404(article,id=upid)
            post.delete()
            return redirect("profile")
        return redirect('login')

def getRegister(request):

        form = RegisterForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_active = False
            instance.save()
            site = get_current_site(request)
            mail_subject = "Confirmation message for blog"
            message = render_to_string('confirm_email.html',{
                "user":instance,
                "domain":site.domain,
                "uid":instance.id,
                "token":activation_token.make_token(instance)
            })
            to_email = form.cleaned_data.get("email")
            to_list = [to_email]
            from_email = settings.EMAIL_HOST_USER
            send_mail(mail_subject,message,from_email,to_list,fail_silently=True)
            return HttpResponse("<h2>thank you for your registration.A confirmation link was sent to your email</h2>")
        return render(request,'register.html',{"form":form})

class getCategory(View):
    def get(self, request):
        query = category.objects.all()
        return render(request,"topics.html",{"topics":query})

class createTopic(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                form = CategoryForm(request.POST or None)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.save()
                    messages.success(request, "Topic is created")
                    return redirect('blog:category')
                return render(request, "create_category.html", {"form": form})
            else:
                raise Http404("You are not authorized to access to this page")
        else:
            return redirect("blog:login")


def activate(request,uid,token):
    try:
        user = get_object_or_404(User,pk=uid)
    except:
        raise Http404("No user found")
    if user is not None and activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        return HttpResponse("<h2>Account is now activeted .you can login now</h2>")
    else:
        return HttpResponse("Invalid activation link")


