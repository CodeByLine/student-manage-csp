import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from slm_app.models import Attendance, AttendanceReport, CustomUser, Course, Subject, Staff, Student, LeaveReportStudent, FeedBackStudent
from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


def student_home(request):
    student_obj=Student.objects.get(admin=request.user.id)
    course=Course.objects.get(id=student_obj.course_id.id)
    subjects=Subject.objects.filter(course_id=course).count()
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    subject_name=[]
    data_present=[]
    data_absent=[]
    data_total=[]
    subject_data=Subject.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True, student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False, student_id=student_obj.id).count()
        attendance_total_count=AttendanceReport.objects.filter(student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
        data_total.append(attendance_total_count)

    context={
        "attendance_total":attendance_total,
        "attendance_present" : attendance_present,
        "attendance_absent" : attendance_absent,
        "subjects" : subjects,
        "data_name" : subject_name,
        "data1" : data_total,
        "data2" : data_present,
        "data3" : data_absent,
    }
    return render(request, "student_templates/student_home_template.html", context)

def student_view_attendance(request):
    student=Student.objects.get(admin=request.user.id)
    course=Course.objects.get(id=student.course_id.id)
    subjects=Subject.objects.filter(course_id=course)
    context={
        "subjects" : subjects,
    }
    return render(request, "student_templates/student_view_attendance.html", context)

def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    start_date_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subject.objects.get(id=subject_id)
    user_object=CustomUser.objects.get(id=request.user.id)
    stud_obj=Student.objects.get(admin=user_object)
    
    attendance=Attendance.objects.filter(attendance_date__range=(start_date_parse, end_date_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)
    # for attendance_report in attendance_reports:
    #     print("Date : "+str(attendance_report.attendance_id.attendance_date)," Status : "+str(attendance_report.status))
    # context={
    #     "attendance_report" : attendance_report,
    # }
    # return HttpResponse("OK")
    return render(request, "student_templates/student_attendance_data.html", {"attendance_reports" : attendance_reports,})

@csrf_exempt
def student_apply_leave(request):
    student_obj=Student.objects.get(admin=request.user.id)
    leave_data=LeaveReportStudent.objects.filter(student_id=student_obj)
    context={
        "leave_data" : leave_data
    }
    return render(request, "student_templates/student_apply_leave.html", context)

# @csrf_exempt
def student_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse('student_apply_leave'))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")
        student_obj=Student.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStudent(student_id=student_obj,leave_date=leave_date,leave_message=leave_msg, leave_status=0)
            leave_report.save()
            messages.success(request,"Application for leave submitted.")
            # return HttpResponse("OK")
            return HttpResponseRedirect(reverse("student_apply_leave"))

        except:
            messages.error(request,"Failed to submit application for leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))

# @csrf_exempt
def student_feedback(request):
    student_id=Student.objects.get(admin=request.user.id)
    feedback_data = FeedBackStudent.objects.filter(student_id=student_id)
    return render(request, "student_templates/student_feedback.html", {"feedback_data":feedback_data})

# @csrf_exempt
def student_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse('student_feedback'))
    else:
        feedback_msg=request.POST.get("feedback_msg")
        
        student_obj=Student.objects.get(admin=request.user.id)
        try:
            leave_report=FeedBackStudent(student_id=student_obj,feedback=feedback_msg, feedback_reply="")
            leave_report.save()
            messages.success(request,"Application for leave submitted.")
            # return HttpResponse("OK")
            return HttpResponseRedirect(reverse("student_feedback"))

        except:
            messages.error(request,"Failed to send feedback")
            return HttpResponseRedirect(reverse("student_feedback"))


@csrf_exempt
def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Student.objects.get(admin=user)
    return render(request, "student_templates/student_profile.html", {"user":user, "student":student})

@csrf_exempt
def student_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name") 
        last_name=request.POST.get("last_name") 
        password=request.POST.get("password") 
        address=request.POST.get("address")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password !=None and password !="":
                customuser.set_password(password)
            customuser.save()

            student=Student.objects.get(admin=customuser)
            student.address=address
            student.save()
            messages.success(request,"Profile successfully updated")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request,"Failed to edit profile")
            return HttpResponseRedirect(reverse("student_profile"))