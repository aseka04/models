from django.contrib import admin
from django.urls import path, include
from onlinecourse import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.course_list, name="course_list"),
    path("courses/", views.course_list, name="courses"),
    path("courses/<int:course_id>/", views.course_details, name="course_details"),
    path("courses/<int:course_id>/submit/", views.submit, name="submit"),
    path("submission/<int:submission_id>/result/", views.show_exam_result, name="show_exam_result"),
    path("", include("onlinecourse.urls_extra")),
]
