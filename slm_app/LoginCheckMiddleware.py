from django.urls import reverse
# from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.deprecation import MiddlewareMixin



class LoginCheckMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):

        modulename=view_func.__module__   #moduelname is name of file where request is sent to
        print(modulename)
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "slm_app.HodViews":
                    pass
                elif modulename == "slm_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('admin_home'))

            elif user.user_type == "2":
                if modulename == "slm_app.StaffViews":
                    pass
                elif modulename == "slm_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('staff_home'))
            
            elif user.user_type == "3":
                if modulename == "slm_app.StudentViews":
                    pass
                elif modulename == "slm_app.views" or modulename == "diango.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('student_home'))
        else: 
            if request.path == reverse("show_login") or request.path == reverse("dologin") or modulename == "django.contrib.auth.views":
                pass
            else:
                return HttpResponseRedirect(reverse('show_login'))