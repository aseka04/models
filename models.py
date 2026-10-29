from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.name}: {self.title}"


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=500)
    grade = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="submissions")
    submitted_at = models.DateTimeField(auto_now_add=True)
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name="submissions")
    score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-submitted_at"]

    @property
    def percentage(self):
        if self.max_score == 0:
            return 0
        return round(self.score / self.max_score * 100)

    @property
    def passed(self):
        return self.percentage >= 70

    def __str__(self):
        return f"{self.course.name} submission #{self.pk}"
