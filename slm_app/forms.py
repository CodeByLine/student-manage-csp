from django import forms
from slm_app.models import Course, Subject, Student, Staff, SessionYearModel

class DateInput(forms.DateInput):
    input_type = "date"

class AddStudentForm(forms.Form):
    email=forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    password=forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    first_name=forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name=forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    username=forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={'class':'form-control', 'autocomplete':'off'}))
    address=forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    # session_year_id=SessionYearModel.objects.all()
    courses=Course.objects.all()
    course_list=[]
    
    try:
        for course in courses:
            sml_course = (course.id, course.course_name)
            course_list.append(sml_course)
    except: 
        course_list=[]


    session_list=[]
    try:          
        sessions=SessionYearModel.objects.all()           
        for ses in sessions:
            sml_session = (ses.id, str(ses.session_start_year)+" TO "+str(ses.session_end_year))
            session_list.append(sml_session)
    except:
        session_list=[]

    gender_choice=(
        ("Male", "Male"),
        ("Female", "Female"),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say')
    )

    course=forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={"class":"form-control"}))
    gender=forms.ChoiceField(label="Gender",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id=forms.ChoiceField(label="Session Year", choices=session_list, widget=forms.Select(attrs={"class":"form-control"}) )
    # session_start=forms.DateField(label="Session Start",widget=DateInput(attrs={"class":"form-control"}))
    # session_end=forms.DateField(label="Session End",widget=DateInput(attrs={"class":"form-control"}))
    date_joined=forms.DateField(label="Date Joined",widget=DateInput(attrs={"class":"form-control"}))
    profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}), required=False)
    note=forms.CharField(label="Note", max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}),required=False)


class EditStudentForm(forms.Form):
    email=forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name=forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name=forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    username=forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
    address=forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={'class':'form-control'}))
   
    courses=Course.objects.all()
    course_list=[]
    try:
        for course in courses:
            sml_course = (course.id, course.course_name)
            course_list.append(sml_course)
    except: 
        course_list=[]

    sessions=SessionYearModel.objects.all() 
    session_list=[]
    try:               
        for ses in sessions:
            sml_ses = (ses.id, str(ses.session_start_year)+" TO "+str(ses.session_end_year))
            session_list.append(sml_ses)
            
    except:
        session_list=[]

    gender_choice=(
        ("Male", "Male"),
        ("Female", "Female"),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say')
    )
    
    course=forms.ChoiceField(label="Course", choices=course_list, widget=forms.Select(attrs={'class':'form-control'}))
    gender=forms.ChoiceField(label="Gender", choices=gender_choice, widget=forms.Select(attrs={'class':'form-control'}))
    session_year_id=forms.ChoiceField(label="Session Year", choices=session_list, widget=forms.Select(attrs={"class":"form-control"}))
    # session_start=forms.DateField(label="Session Start",widget=DateInput(attrs={"class":"form-control"}))
    # session_end=forms.DateField(label="Session End",widget=DateInput(attrs={"class":"form-control"}))
    date_joined=forms.DateField(label="Date Joined",widget=DateInput(attrs={"class":"form-control"}))
    profile_pic=forms.FileField(label="Profile Pic", widget=forms.FileInput(attrs={"class":"form-control"}),required=False)
    note=forms.CharField(label="Note", max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}),required=False)

class EditResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.staff_id=kwargs.pop("staff_id")
        super().__init__()
        subject_list=[]
        try:
            subjects=Subject.objects.filter(staff_id=self.staff_id)
            for subject in subjects:
                subject_single=(subject.id,subject.subject_name)
                subject_list.append(subject_single)
        except:
            subject_list=[]
        
        session_list=[]
        try:
            sessions=SessionYearModel.objects.all()
            for session in sessions:
                session_single=(session.id,session.session_start_year+" TO "+session.session_end_year)
                session_list.append(session_single)
        except:
            session_list=[]
        
        self.subject_id=forms.ChoiceField(lable="Subject",choices=subject_list,widget=forms.Select(attrs={"class":"form-control"}))
        self.session_id=forms.ChoiceField(lable="Session Year",choices=subject_list,widget=forms.Select(attrs={"class":"form-control"}))
        self.student_id=forms.ChoiceField(lable="Student",widget=forms.Select(attrs={"class":"form-control"}))
        self.assignment_marks=forms.CharField(lable="Assignment Marks",widget=forms.TextInput(attrs={"class":"form-control"}))
        self.exam_marks=forms.CharField(lable="Exam Marks",widget=forms.TextInput(attrs={"class":"form-control"}))

