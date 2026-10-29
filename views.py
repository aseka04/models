from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Course, Choice, Submission


def course_list(request):
    courses = Course.objects.all()
    return render(request, "onlinecourse/course_list.html", {"course_list": courses})


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


@require_POST
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    questions = course.questions.prefetch_related("choices").all()
    submission = Submission.objects.create(course=course)
    score = 0
    max_score = 0

    for question in questions:
        max_score += question.grade
        selected_id = request.POST.get(f"question_{question.id}")
        if not selected_id:
            continue
        try:
            selected = question.choices.get(pk=int(selected_id))
        except (Choice.DoesNotExist, ValueError, TypeError):
            continue
        submission.selected_choices.add(selected)
        if selected.is_correct:
            score += question.grade

    submission.score = score
    submission.max_score = max_score
    submission.save()
    return redirect("show_exam_result", submission_id=submission.pk)


def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("course").prefetch_related(
            "selected_choices__question__choices"
        ),
        pk=submission_id,
    )
    selected_by_question = {
        choice.question_id: choice for choice in submission.selected_choices.all()
    }
    results = []
    for question in submission.course.questions.prefetch_related("choices").all():
        selected = selected_by_question.get(question.id)
        correct = next((choice for choice in question.choices.all() if choice.is_correct), None)
        results.append({
            "question": question,
            "selected": selected,
            "correct": correct,
            "is_correct": bool(selected and selected.is_correct),
        })
    return render(request, "onlinecourse/exam_result.html", {
        "submission": submission,
        "results": results,
    })
