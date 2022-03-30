from ast import Sub
import json
import re
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from slm_app.forms import AddStudentForm, EditStudentForm
from django.urls import reverse
from slm_app.models import (
                            Attendance, 
                            AttendanceReport, 
                            CustomUser, 
                            Course, 
                            FeedBackStaff,
                            FeedBackStudent, 
                            LeaveReportStudent, 
                            Subject, 
                            Staff, 
                            Student, 
                            SessionYearModel, 
                            LeaveReportStaff
                            )
from django.views.decorators.csrf import csrf_exempt


def admin_home(request):
    student_count1=Student.objects.all().count()
    staff_count=Staff.objects.all().count()
    subject_count=Subject.objects.all().count()
    course_count=Course.objects.all().count()

    course_all=Course.objects.all()
    course_name_list=[]
    subject_count_list=[]
    student_count_list_in_course=[]
    for course in course_all:
        course = Course.objects.get(id=course.id)
        subjects=Subject.objects.filter(course_id=course.id).count()
        students=Student.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subjects_all=Subject.objects.all()
    subject_list=[]
    student_count_list_in_subject=[]
    for subject in subjects_all:
        course=Course.objects.get(id=subject.course_id.id)
        student_count=Student.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs=Staff.objects.all()
    attendance_present_list_staff=[]
    attendance_absent_list_staff=[]
    staff_name_list=[]
    for staff in staffs:
        subject_ids=Subject.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all=Student.objects.all()
    attendance_present_list_student=[]
    attendance_absent_list_student=[]
    student_name_list=[]
    for student in students_all:
        attendance=AttendanceReport.objects.filter(student_id=student.id,status=True).count()
        absent=AttendanceReport.objects.filter(student_id=student.id,status=False).count()
        leaves=LeaveReportStudent.objects.filter(student_id=student.id,leave_status=1).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves+absent)
        student_name_list.append(student.admin.username)

    context={
        "student_count" : student_count1,
        "staff_count" : staff_count,
        "subject_count" : subject_count,
        "course_count" : course_count,
        "course_name_list" : course_name_list,
        "subject_count_list" : subject_count_list,
        "student_count_list_in_course" : student_count_list_in_course,
        "course" : course,
        
        "subject_list" :  subject_list,
        "student_count_list_in_subject" : student_count_list_in_subject,
        "staff_name_list":staff_name_list,
        "attendance_present_list_staff":attendance_present_list_staff,
        "attendance_absent_list_staff":attendance_absent_list_staff,
        "student_name_list":student_name_list,
        "attendance_present_list_student":attendance_present_list_student,
        "attendance_absent_list_student":attendance_absent_list_student,
    }

    return render(request, 'hod_templates/admin_home.html', context)

def add_staff(request):
    return render(request, 'hod_templates/add_staff_template.html')

def add_staff_save(request):
    if request.method !="POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        address=request.POST.get('address')

        try:
            user=CustomUser.objects.create_user(
                username=username, 
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                # address=address,
                user_type=2)
            user.staff.address=address
            user.save()
            messages.success(request, "Staff successfully added")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request, "Failed to add staff")
            return HttpResponseRedirect(reverse("add_staff"))
  
def add_student(request): # Forms
    form=AddStudentForm()
    context={
        "form" : form,
    }
    return render(request,"hod_templates/add_student_template.html", context)

# def add_student(request): # HTML form
#     courses =Course.objects.all()
#     return render(request, 'hod_templates/add_student_template.html', {"courses":courses })


def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddStudentForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]
            date_joined=form.cleaned_data["date_joined"]
            session_year_id=form.cleaned_data["session_year_id"]
            course_id=form.cleaned_data["course"]
            gender=form.cleaned_data["gender"]

            if request.FILES.get('profile_pic', False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name, profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None

            try:
                user=CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    last_name=last_name,
                    first_name=first_name,
                    user_type=3
                    )
                user.student.address=address
                course_obj=Course.objects.get(id=course_id)
                user.student.course_id=course_obj
                session_year=SessionYearModel.objects.get(id=session_year_id)
                user.student.session_year_id=session_year
                    # user.student.session_start_year=session_start
                    # user.student.session_end_year=session_end
                user.student.date_joined=date_joined
                user.student.gender=gender
                user.student.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except:
                messages.error(request,"Failed to Add Student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form=AddStudentForm(request.POST)
            return render(request, "hod_templates/add_student_template.html", {"form": form})

def add_course(request):
    return render(request,"hod_templates/add_course_template.html")

def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course=request.POST.get("course")
        try:
            course_model=Course(course_name=course)
            course_model.save()
            messages.success(request,"Course Successfully Added")
            return HttpResponseRedirect(reverse("add_course"))
        except:
            messages.error(request,"Failed To Add Course")
            return HttpResponseRedirect(reverse("add_course"))
    
 
def add_subject(request):
    courses = Course.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request,
        "hod_templates/add_subject_template.html", 
        {"staffs":staffs, "courses":courses})

def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course = Course.objects.get(id=course_id)
        staff_id = request.POST.get("staff") # This is from the 'name' in form-control
        staff = CustomUser.objects.get(id=staff_id)
        # return HttpResponse("hey!")
        try:
            subject=Subject(
                subject_name=subject_name, 
                course_id=course, 
                staff_id=staff
                )
            subject.save()
            messages.success(request,"Course Successfully Added")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request,"Failed To Add Course")
            return HttpResponseRedirect(reverse("add_subject"))
@csrf_exempt
def add_session(request):
    sessions=SessionYearModel.objects.all()
    session_start_year=request.POST.get("session_start")
    session_end_year=request.POST.get("session_end")
    return render(request,
        "hod_templates/add_session_template.html", 
        {"session_start_year":session_start_year, "session_end_year":session_end_year, "sessions" : sessions})

@csrf_exempt
def add_session_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse('manage_sessions'))
    else:    
        # session=SessionYearModel.objects.get(id=session_id)
        # session_year_id=SessionYearModel.objects.get("session")
        session_start_year=request.POST.get("session_start")
        session_end_year=request.POST.get("session_end")

        try:
            session_year = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            session_year.save()
            messages.success(request,"Session Successfully Added")
        # HttpResponse("OK")
            return HttpResponseRedirect(reverse("manage_sessions"))
        except:
            messages.error(request,"Failed To Add Session")
            return HttpResponseRedirect(reverse("add_session"))
 

def manage_staff(request):
    staffs = Staff.objects.all()
    return render(request, "hod_templates/manage_staff_template.html", {"staffs":staffs})


def manage_students(request):
    students = Student.objects.all()
    return render(request, "hod_templates/manage_students_template.html", {"students":students})

def manage_courses(request):
    courses = Course.objects.all()
    return render(request, "hod_templates/manage_courses_template.html", {"courses":courses})

def manage_subjects(request):
    subjects = Subject.objects.all()
    staffs=Staff.objects.all()
    return render(request, "hod_templates/manage_subjects_template.html", {"subjects":subjects})

def manage_sessions(request):
    sessions = SessionYearModel.objects.all()
    return render(request, "hod_templates/manage_sessions_template.html", {"sessions":sessions})

@csrf_exempt
def edit_session(request, session_year_id):
    session=SessionYearModel.objects.get(id=session_year_id)
    # session_id = request.POST.get(session)
    session_start=request.POST.get("session_start_year")
    session_end=request.POST.get("session_end_year")
    context={
        "session" : session,
        "id" : session_year_id,
        "session_start" : session_start,
        "session_end_year" : session_end,
    }

    return render(request, "hod_templates/edit_session_template.html", context)

@csrf_exempt
def edit_session_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        session_year_id = request.POST.get("session_year_id")  
        session=request.POST.get(session_year_id)

        try:

            session=SessionYearModel.objects.get(id=session_year_id)
            session_start_year=request.POST.get("session_start")
            session_end_year=request.POST.get("session_end")
            
            
            # return HttpResponse('ok')
            context={
                "session" : session,
                "session_year_id" : session_year_id,
                "session_start" : session_start_year,
                "session_end" : session_end_year,
            }
            session.save()
            messages.success(request,"Session detail successfully updated")
            return HttpResponseRedirect(reverse("manage_sessions"), context)    

        except:
            messages.error(request,"Failed To edit session")
            return HttpResponseRedirect(reverse("edit_session", kwargs={"session_year_id" : session_year_id}))

 


def edit_staff(request, staff_id):
    staff=Staff.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_templates/edit_staff_template.html", context)

def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id=request.POST.get("staff_id")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        username=request.POST.get("username")
        address=request.POST.get("address")

        try:
            user=CustomUser.objects.get(id=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()

            staff_model=Staff.objects.get(admin=staff_id)
            staff_model.address=address
            staff_model.save()

            messages.success(request,"Staff detail Successfully Edited")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id" : staff_id}))

        except:
            messages.error(request,"Failed To Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id" : staff_id}))

# import pdb; pdb.set_trace()

def edit_student(request, student_id):
    request.session['student_id']=student_id
    student=Student.objects.get(admin=student_id)
    courses=Course.objects.all()
    form=EditStudentForm()
    form.fields['email'].initial = student.admin.email
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['username'].initial = student.admin.username
    form.fields['address'].initial = student.address
    form.fields['course'].initial = student.course_id.id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id
    form.fields['date_joined'].initial=student.date_joined
    # form.fields['session_start'].initial = student.session_start_year
    # form.fields['session_end'].initial = student.session_end_year
    form.fields['note'].initial = student.note
    
    context = {
        "form" : form,
        "id" : student_id,
        "username" : student.admin.username,
    }
    return render(request, "hod_templates/edit_student_template.html", context)


# import pdb; pdb.set_trace()

def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id=request.session.get("student_id")
        if student_id==None:
            return HttpResponseRedirect(reverse("manage_students"))

        form=EditStudentForm(request.POST, request.FILES)

        if form.is_valid():                
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            address=form.cleaned_data["address"]
            course_id = form.cleaned_data["course"]
            session_year_id=form.cleaned_data["session_year_id"]
            gender=form.cleaned_data["gender"]
            date_joined=form.cleaned_data['date_joined']
            note=form.cleaned_data["note"]

            if request.FILES.get('profile_pic', False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name, profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None

            try:
                user=CustomUser.objects.get(id=student_id)
                user.first_name=first_name
                user.last_name=last_name
                user.username=username
                user.email=email      
                user.save()

                student=Student.objects.get(admin=student_id)
                student.address=address            
                session_year=SessionYearModel.objects.get(id=session_year_id)
                student.session_year_id=session_year
                                   
                course = Course.objects.get(id=course_id)
                student.course_id = course
                student.gender = gender
                student.date_joined=date_joined
                student.note = note
                if profile_pic_url != None:
                    student.profile_pic=profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request,"Student detail Successfully Edited")                
                return redirect("manage_students")

            except:
                messages.error(request,"Failed To Edit Student")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id" : student_id}))

        else:
            form=EditStudentForm(request.POST)
            student=Student.objects.get(admin=student_id)
            context = {
                "form" : form,
                "id" : student_id,
                "username" : student.admin.username,
                }
            return render(request, "hod_templates/edit_student_template.html", context)

# import pdb; pdb.set_trace()

def edit_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    courses = Course.objects.all()
    staffs = CustomUser.objects.filter(user_type=2 )

    context = {
        "subject": subject, 
        "staffs": staffs, 
        "courses": courses, 
        "id": subject_id,
        } 
    
    return render(request, "hod_templates/edit_subject_template.html", context )

def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id=request.POST.get("subject_id")  #reading form data
        subject_name=request.POST.get("subject_name") #get("subject")
        staff_id=request.POST.get("staff")
        course_id=request.POST.get("course")

        try:
            subject=Subject.objects.get(id=subject_id)
            subject.subject_name = subject_name
            staff=CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            course=Course.objects.get(id=course_id)
            subject.course_id = course
            subject.save()
            messages.success(request,"Subject detail successfully updated")
            return HttpResponseRedirect(reverse("manage_subjects"))

        except:
            messages.error(request,"Failed To Edit subject")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id" : subject_id}))


def edit_course(request, course_id):
    course = Course.objects.get(id=course_id)
    context = {
        "course": course,
        "id" : course_id,
        }
    return render(request, "hod_templates/edit_course_template.html", context )


def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id=request.POST.get("course_id")  #reading form data
        course_name=request.POST.get("course") #get("course")

        try:
            course=Course.objects.get(id=course_id)
            course.course_name=course_name
            course.save()
            messages.success(request,"Course detail successfully updated")
            return HttpResponseRedirect(reverse("manage_courses"))

        except:
            messages.error(request,"Failed To Edit course")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id" : course_id}))


@csrf_exempt
def check_email_exist(request):    
    email=request.POST.get("email")
    user_obj=CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def student_feedback_message(request):
    feedbacks=FeedBackStudent.objects.all()
    context={
        "feedbacks" : feedbacks
    }
    return render(request, "hod_templates/student_feedback_template.html", context)

@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def staff_feedback_message(request):
    feedbacks=FeedBackStaff.objects.all()
    context={
        "feedbacks" : feedbacks
    }
    return render(request, "hod_templates/staff_feedback_template.html", context)

@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id=request.POST.get("id")
    feedback_message=request.POST.get("message")

    try:
        feedback=FeedBackStaff.objects.get(id=feedback_id)
        feedback.feedback_reply=feedback_message
        feedback.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

@csrf_exempt
def student_leave_view(request):
    leaves=LeaveReportStudent.objects.all()
    context={
        "leaves" : leaves
    }
    return render(request, "hod_templates/student_leave_view.html", context)

@csrf_exempt
def student_leave_approved(request, leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))

@csrf_exempt
def student_leave_denied(request, leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


@csrf_exempt
def staff_leave_view(request):
    leaves=LeaveReportStaff.objects.all()
    context={
        "leaves" : leaves
    }
    return render(request, "hod_templates/staff_leave_view.html", context)


@csrf_exempt
def staff_leave_approved(request, leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

@csrf_exempt
def staff_leave_denied(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))

@csrf_exempt
def admin_view_attendance(request):
    subjects=Subject.objects.all()
    session_year_id=SessionYearModel.objects.all()
    context={
        "subjects" : subjects,
        "session_year_id" : session_year_id,
    }
    return render(request, "hod_templates/admin_view_attendance.html", context)

@csrf_exempt
def admin_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subject.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)        
    attendance = Attendance.objects.filter(
        subject_id=subject_obj, 
        session_year_id=session_year_obj
        )
    attendance_obj=[]

    for attendance_single in attendance:
        data={
            "id":attendance_single.id, 
            "attendance_date":str(attendance_single.attendance_date),
            "session_year_id":attendance_single.session_year_id.id,
            # "subject_id" : subject,
            }
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)

@csrf_exempt
def admin_get_attendance_student(request):   
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)
    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)

    list_data=[]
 
    for student in attendance_data:
        data_small={
            "id":student.student_id.admin.id,
            "name": student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status }
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)

@csrf_exempt
def admin_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    return render(request, "hod_templates/admin_profile.html", {"user":user})

@csrf_exempt
def admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name=request.POST.get("first_name") 
        last_name=request.POST.get("last_name") 
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name

            if password !=None and password !="":
                customuser.set_password(password)
            customuser.save()
            messages.success(request,"Profile successfully updated")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request,"Failed to edit profile")
            return HttpResponseRedirect(reverse("admin_profile"))
