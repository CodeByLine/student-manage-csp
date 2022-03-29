from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# from slm_app.forms import AddStudentForm, EditStudentForm
from slm_app.models import CustomUser, Staff, Course, Subject, Student

def showDemoPage(request):
    return render(request, 'demo.html')

def showLoginPage(request):
    return render(request,"login_page.html")

def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else: 
        user=authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=="2":
                return HttpResponseRedirect(reverse("staff_home"))
                # return HttpResponse("staff login "+str(user.user_type))  # check as string
                
            else:
                return HttpResponseRedirect(reverse("student_home"))
                # return HttpResponse("student login "+str(user.user_type))  # check as string
                
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")
    

def admin_home(request):
    return render(request,"hod_templates/home_content.html")


def add_subject(request):
    course=Course.objects.all()
    staff=CustomUser.objects.filter(user_type=2)
    return render(request,"hod_templates/add_subject_template.html",{"staff":staff,"course":course})

def add_subject_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name=request.POST.get("subject_name")
        course_id=request.POST.get("course")
        course=Course.objects.get(id=course_id)
        staff_id=request.POST.get("staff")
        staff=CustomUser.objects.get(id=staff_id)

        try:
            subject=Subject(subject_name=subject_name,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,"Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))

def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+request.user.user_type)
    else:
        return HttpResponse("Please Login first")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")

# def manage_staff(request):
#     staff=Staff.objects.all()
#     return render(request,"hod_templates/manage_staff_template.html",{"staff":staff})

# def manage_student(request):
#     student=Student.objects.all()
#     return render(request,"hod_templates/manage_student_template.html",{"student":student})

# def manage_course(request):
#     course=Course.objects.all()
#     # return render(request,"hod_templates/manage_course_template.html",{"course":course})

# def manage_subject(request):
#     subject=Subject.objects.all()
#     # return render(request,"/manage_subject_template.html",{"subject":subject})

# def edit_staff(request,staff_id):
#     staff=Staff.objects.get(admin=staff_id)
#     # return render(request,"hod_templates/edit_staff_template.html",{"staff":staff,"id":staff_id})

# def edit_staff_save(request):
#     if request.method!="POST":
#         return HttpResponse("<h2>Method Not Allowed</h2>")
#     else:
#         staff_id=request.POST.get("staff_id")
#         first_name=request.POST.get("first_name")
#         last_name=request.POST.get("last_name")
#         email=request.POST.get("email")
#         username=request.POST.get("username")
#         address=request.POST.get("address")

#         try:
#             user=CustomUser.objects.get(id=staff_id)
#             user.first_name=first_name
#             user.last_name=last_name
#             user.email=email
#             user.username=username
#             user.save()

#             staff_model=Staff.objects.get(admin=staff_id)
#             staff_model.address=address
#             staff_model.save()
#             messages.success(request,"Successfully Edited Staff")
#             return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))
#         except:
#             messages.error(request,"Failed to Edit Staff")
#             return HttpResponseRedirect(reverse("edit_staff",kwargs={"staff_id":staff_id}))

# def edit_student(request,student_id):
#     request.session['student_id']=student_id
#     student=Student.objects.get(admin=student_id)
#     form=EditStudentForm()
#     form.fields['email'].initial=student.admin.email
#     form.fields['first_name'].initial=student.admin.first_name
#     form.fields['last_name'].initial=student.admin.last_name
#     form.fields['username'].initial=student.admin.username
#     form.fields['address'].initial=student.address
#     form.fields['course'].initial=student.course_id.id
#     form.fields['sex'].initial=student.gender
#     form.fields['session_start'].initial=student.session_start_year
#     form.fields['session_end'].initial=student.session_end_year
#     return render(request,"hod_templates/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

# def edit_student_save(request):
#     if request.method!="POST":
#         return HttpResponse("<h2>Method Not Allowed</h2>")
#     else:
#         student_id=request.session.get("student_id")
#         if student_id==None:
#             return HttpResponseRedirect(reverse("manage_student"))

#         form=EditStudentForm(request.POST,request.FILES)
#         if form.is_valid():
#             first_name = form.cleaned_data["first_name"]
#             last_name = form.cleaned_data["last_name"]
#             username = form.cleaned_data["username"]
#             email = form.cleaned_data["email"]
#             address = form.cleaned_data["address"]
#             session_start = form.cleaned_data["session_start"]
#             session_end = form.cleaned_data["session_end"]
#             course_id = form.cleaned_data["course"]
#             sex = form.cleaned_data["sex"]

#             if request.FILES.get('profile_pic',False):
#                 profile_pic=request.FILES['profile_pic']
#                 fs=FileSystemStorage()
#                 filename=fs.save(profile_pic.name,profile_pic)
#                 profile_pic_url=fs.url(filename)
#             else:
#                 profile_pic_url=None


#             try:
#                 user=CustomUser.objects.get(id=student_id)
#                 user.first_name=first_name
#                 user.last_name=last_name
#                 user.username=username
#                 user.email=email
#                 user.save()

#                 student=Student.objects.get(admin=student_id)
#                 student.address=address
#                 student.session_start_year=session_start
#                 student.session_end_year=session_end
#                 student.gender=sex
#                 course=Course.objects.get(id=course_id)
#                 student.course_id=course
#                 if profile_pic_url!=None:
#                     student.profile_pic=profile_pic_url
#                 student.save()
#                 del request.session['student_id']
#                 messages.success(request,"Successfully Edited Student")
#                 return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
#             except:
#                 messages.error(request,"Failed to Edit Student")
#                 return HttpResponseRedirect(reverse("edit_student",kwargs={"student_id":student_id}))
#         else:
#             form=EditStudentForm(request.POST)
#             student=Student.objects.get(admin=student_id)
#             return render(request,"hod_templates/edit_student_template.html",{"form":form,"id":student_id,"username":student.admin.username})

# def edit_subject(request,subject_id):
#     subject=Subject.objects.get(id=subject_id)
#     course=Course.objects.all()
#     staff=CustomUser.objects.filter(user_type=2)
#     return render(request,"hod_templates/edit_subject_template.html",{"subject":subject,"staff":staff,"course":course,"id":subject_id})

# def edit_subject_save(request):
#     if request.method!="POST":
#         return HttpResponse("<h2>Method Not Allowed</h2>")
#     else:
#         subject_id=request.POST.get("subject_id")
#         subject_name=request.POST.get("subject_name")
#         staff_id=request.POST.get("staff")
#         course_id=request.POST.get("course")

#         try:
#             subject=Subject.objects.get(id=subject_id)
#             subject.subject_name=subject_name
#             staff=CustomUser.objects.get(id=staff_id)
#             subject.staff_id=staff
#             course=Course.objects.get(id=course_id)
#             subject.course_id=course
#             subject.save()

#             messages.success(request,"Successfully Edited Subject")
#             return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))
#         except:
#             messages.error(request,"Failed to Edit Subject")
#             return HttpResponseRedirect(reverse("edit_subject",kwargs={"subject_id":subject_id}))


# def edit_course(request,course_id):
#     course=Course.objects.get(id=course_id)
#     return render(request,"hod_templates/edit_course_template.html",{"course":course,"id":course_id})

# def edit_course_save(request):
#     if request.method!="POST":
#         return HttpResponse("<h2>Method Not Allowed</h2>")
#     else:
#         course_id=request.POST.get("course_id")
#         course_name=request.POST.get("course")

#         try:
#             course=Course.objects.get(id=course_id)
#             course.course_name=course_name
#             course.save()
#             messages.success(request,"Successfully Edited Course")
#             return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))
#         except:
#             messages.error(request,"Failed to Edit Course")
#             return HttpResponseRedirect(reverse("edit_course",kwargs={"course_id":course_id}))
