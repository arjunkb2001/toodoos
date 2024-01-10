from django.shortcuts import render,redirect

from reminder.models import Todos
from django.views.generic import View
from reminder.forms import UserForm,LoginForm,TodoForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages


from django.utils.decorators import method_decorator


# Create your views here.
def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session")
            return redirect("login")
        else:
            return fn(request,*args,**kwargs)
    return wrapper


def owner_permission_required(fn):
    def wrappper(request,*args, **kwargs):
        id=kwargs.get("pk")
        todo_object=Todos.objects.get(id=id)
        if todo_object.user != request.user:
            return redirect("signin")
        else:
            return fn(request,*args, **kwargs)
    return wrappper


decs=[signin_required,owner_permission_required]

class SignupView(View):
    def get(self,request,*args, **kwargs):
        form=UserForm()
        return render(request,"register.html",{'form':form})
    def post(self,request,*args, **kwargs):
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
            print("account created")
            return redirect("register")
        else:
            print("failed")
            return render(request,"register.html",{'form':form})
        


class SiginView(View):
    def get(self,request,*args, **kwargs):
        form=LoginForm()
        return render(request,"login.html",{'form':form})
    def post(self,request,*args, **kwargs):
        form=LoginForm(request.POST)

        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=uname,password=pwd)
            if user_object:
                login(request,user_object)
                print("login successfully")
                return redirect("index")
        print("invalid credential")
        return render(request,"login.html",{'form':form})
    
@method_decorator(signin_required,name="dispatch")
class IndexView(View):
    def get(self,request,*args, **kwargs):
        form=TodoForm()
        qs=Todos.objects.filter(user=request.user).order_by("status")
        return render(request,"index.html",{"form":form,"data":qs} )
    def post(self,request,*args, **kwargs):
        form=TodoForm(request.POST)
        if form.is_valid():
            form.instance.user=request.user
            form.save()
            return redirect("index")
        else:
            return render(request,"index.html",{"form":form} )
        
@method_decorator(decs,name="dispatch")
class TodoDeleteView(View):
    def get(self,request,*args, **kwargs):
        id=kwargs.get("pk")
        Todos.objects.filter(id=id).delete()
        return redirect("index")
    
@method_decorator(signin_required,name="dispatch")
class TodoChangeView(View):
    def get(self,request,*args, **kwargs):
        id=kwargs.get("pk")
        todo_object=Todos.objects.get(id=id)
        if todo_object.status==True:
            todo_object.status=False
            todo_object.save()
        else:
            todo_object.status=True
            todo_object.save()
        # Todos.objects.filter(id=id).update(status=True)
        return redirect("index")

    

class SignOutView(View):
    def get(self,request,*args, **kwargs):
        logout(request)
        return redirect("signin")