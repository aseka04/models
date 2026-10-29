from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Course, Learner, Enrollment, Submission, Choice


def course_list(request):
    courses = Course.objects.all()

    return render(
        request,
        "onlinecourse/course_list.html",
        {"course_list": courses},
    )


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


@require_POST
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if not request.user.is_authenticated:
        messages.info(request, "Please log in before taking the exam.")
        return redirect(
            f"/admin/login/?next=/course/{course_id}/"
        )

    learner, _ = Learner.objects.get_or_create(user=request.user)

    enrollment, _ = Enrollment.objects.get_or_create(
        learner=learner,
        course=course,
    )

    submission = Submission.objects.create(
        enrollment=enrollment
    )

    score = 0
    max_score = 0

    for question in course.questions.prefetch_related("choices"):
        max_score += question.grade

        # The template uses radio buttons, so each question has
        # at most one selected choice.
        selected_id = request.POST.get(f"question_{question.id}")

        if not selected_id:
            continue

        try:
            selected_choice = question.choices.get(
                pk=int(selected_id)
            )
        except (Choice.DoesNotExist, ValueError, TypeError):
            continue

        submission.choices.add(selected_choice)

        if question.is_get_score([selected_choice.id]):
            score += question.grade

    submission.score = score
    submission.max_score = max_score
    submission.save()

    return redirect(
        "show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


def show_exam_result(request, course_id, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related(
            "enrollment__learner__user"
        ).prefetch_related("choices"),
        pk=submission_id,
        enrollment__course_id=course_id,
    )

    course = submission.enrollment.course

    selected_by_question = {
        choice.question_id: choice
        for choice in submission.choices.all()
    }

    results = []

    for question in course.questions.prefetch_related("choices"):
        selected = selected_by_question.get(question.id)

        correct_choices = question.choices.filter(
            is_correct=True
        )

        correct = correct_choices.first()

        results.append({
            "question": question,
            "selected": selected,
            "correct": correct,
            "is_correct": bool(
                selected
                and question.is_get_score([selected.id])
            ),
        })

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "submission": submission,
            "course": course,
            "results": results,
        },
    )
