import re
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from slm_app.models import AttendanceReport, CustomUser, Course, LeaveReportStaff, SessionYearModel, Subject, Staff, Student, Attendance, FeedBackStaff
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
# from rest_framework import serializers
from django.core import serializers
from django.contrib import messages
import json

def staff_home(request):
    subjects=Subject.objects.filter(staff_id=request.user.id)
    course_id_list=[]
    for subject in subjects:
        course=Course.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)

    final_course=[]
    # remove duplicate courses
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count=Student.objects.filter(course_id__in=final_course).count()
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()
    
    staff=Staff.objects.get(admin=request.user.id)
    leave_count=LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
    subjects_count=subjects.count()

    # fetch attendance
    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance=Student.objects.filter(course_id__in=final_course)
    student_list=[]
    student_list_attendance_present=[]
    student_list_attendance_absent=[]
    for student in students_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count" : students_count,
        "attendance_count" : attendance_count,
        "leave_count" : leave_count,
        "subjects_count" : subjects_count,
        "subject_list" : subject_list,
        "attendance_count1" : attendance_count1,
        "attendance_list" : attendance_list,
        "student_list" : student_list,
        "present_list" : student_list_attendance_present,
        "absent_list" : student_list_attendance_absent,
    }
    return render(request, "staff_templates/staff_home_template.html", context)

# fetch student data according to subject fist
#fetch the course ID from subject then pass the course into subject
#create SessionYearModel object and pass into student
def staff_take_attendance(request):
    subjects=Subject.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.objects.all()

    context={
        "subjects" : subjects,
        "session_years" : session_years,
    }
    return render(request, "staff_templates/staff_take_attendance.html", context)

@csrf_exempt
def get_students(request):
    # pass
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subject.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year)
    students=Student.objects.filter(course_id=subject.course_id, session_year_id=session_model)
    student_data=serializers.serialize("python",students)
    list_data=[]
 
    for student in students:
        data_small={
            "id":student.admin.id,
            "name": student.admin.first_name+" "+student.admin.last_name }
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    # else:
    #     return HttpResponse("No students found for this period")
    # return HttpResponse(students, safe=False)
    # return JsonResponse(student_data, content_type="application/json", safe=False)

@csrf_exempt
def save_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    subject_id=request.POST.get("subject_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")
    # print(student_ids)
    subject_model=Subject.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year_id)
    # data=json.loads(student_ids)
    json_sstudents=json.loads(student_ids) #loads s for string
    # print(data[0]['id'])
    try:
        attendance=Attendance(subject_id=subject_model, attendance_date=attendance_date, session_year_id=session_model)
        attendance.save()

        for stud in json_sstudents:
            student=Student.objects.get(admin=stud['id'])
            attendance_report=AttendanceReport(
                student_id=student,
                attendance_id=attendance, 
                status=stud['status']
                )
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Something went wrong")


@csrf_exempt
def staff_update_attendance(request):
    subjects=Subject.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    context={
        "subjects" : subjects,
        "session_year_id" : session_year_id,
    }
    return render(request,"staff_templates/staff_update_attendance.html",context)

@csrf_exempt
def get_attendance_dates(request):
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
def get_attendance_student(request):   
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
def save_updateattendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)
    json_sstudents=json.loads(student_ids) #loads s for string
  
    try:
        for stud in json_sstudents:
            student=Student.objects.get(admin=stud['id'])
            attendance_report=AttendanceReport.objects.get(
                student_id=student,
                attendance_id=attendance
                )
            attendance_report.status=stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Something went wrong")

@csrf_exempt
def staff_apply_leave(request):
    staff_obj=Staff.objects.get(admin=request.user.id)
    leave_data=LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context={
        "leave_data" : leave_data
    }
    return render(request, "staff_templates/staff_apply_leave.html", context)

# @csrf_exempt
def staff_apply_leave_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse('staff_apply_leave'))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")
        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStaff(staff_id=staff_obj,leave_date=leave_date,leave_message=leave_msg, leave_status=0)
            leave_report.save()
            messages.success(request,"Application for leave submitted.")
            # return HttpResponse("OK")
            return HttpResponseRedirect(reverse("staff_apply_leave"))

        except:
            messages.error(request,"Failed to submit application for leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))

# @csrf_exempt
def staff_feedback(request):
    staff_id=Staff.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaff.objects.filter(staff_id=staff_id)
    return render(request, "staff_templates/staff_feedback.html", {"feedback_data":feedback_data})

# @csrf_exempt
def staff_feedback_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse('staff_feedback'))
    else:
        feedback_msg=request.POST.get("feedback_msg")
        
        staff_obj=Staff.objects.get(admin=request.user.id)
        try:
            leave_report=FeedBackStaff(staff_id=staff_obj,feedback=feedback_msg, feedback_reply="")
            leave_report.save()
            messages.success(request,"Application for leave submitted.")
            # return HttpResponse("OK")
            return HttpResponseRedirect(reverse("staff_feedback"))

        except:
            messages.error(request,"Failed to send feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))

@csrf_exempt
def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staff.objects.get(admin=user)
    return render(request, "staff_templates/staff_profile.html", {"user":user, "staff":staff})

@csrf_exempt
def staff_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_profile"))
    else:
        first_name=request.POST.get("first_name") 
        last_name=request.POST.get("last_name") 
        password=request.POST.get("password")
        address=request.POST.get("address")
        password=request.POST.get("password")

        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name

            if password !=None and password !="":
                customuser.set_password(password)
            customuser.save()
            staff=Staff.objects.get(admin=customuser.id)
            staff.address=address
            staff.save()

            messages.success(request,"Profile successfully updated")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request,"Failed to edit profile")
            return HttpResponseRedirect(reverse("staff_profile"))