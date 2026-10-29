from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, blank=True)
    social_link = models.URLField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    instructors = models.ManyToManyField(
        Instructor, blank=True, related_name="courses"
    )
    learners = models.ManyToManyField(
        Learner, through="Enrollment", related_name="courses", blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    date_enrolled = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["learner", "course"],
                name="unique_learner_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.learner} - {self.course}"


class Question(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.CharField(max_length=500)
    grade = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.question_text

    def is_get_score(self, selected_ids):
        """Return True when the selected choice IDs match all correct choices."""
        if not selected_ids:
            return False

        correct_ids = set(
            self.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        selected_ids = {int(choice_id) for choice_id in selected_ids}

        return bool(correct_ids) and selected_ids == correct_ids


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="submissions"
    )
    choices = models.ManyToManyField(
        Choice, blank=True, related_name="submissions"
    )
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        if not self.max_score:
            return 0
        return round(self.score / self.max_score * 100)

    def __str__(self):
        return f"Submission #{self.pk} - {self.enrollment}"
