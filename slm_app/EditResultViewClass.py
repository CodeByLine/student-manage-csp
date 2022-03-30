from django.shortcuts import render
from django.views import View

from slm_app.forms import EditResultForm

class EditResultViewClass(View):
    def get(self,request,*args,**kwargs):
        staff_id=request.user.id
        edit_result_form=EditResultForm()
        context={
            "form" : edit_result_form,
        }
       
        return render(request, "edit_student_result.html", context)

    def post(self,request,*args,**kwargs):
        pass