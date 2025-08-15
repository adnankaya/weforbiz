from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

# internals




class Rating(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class FeedbackQuestion(models.Model):
    text = models.CharField(max_length=255)

    class Meta:
        db_table = "t_feedback_question"


class FeedbackResponse(models.Model):
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=Rating.choices, default=Rating.THREE)
    # NOTE adding extra fields? example -> answer = models.CharField(max_length=255)

    class Meta:
        db_table = "t_feedback_response"


class Feedback(models.Model):
    contract = models.ForeignKey("jobs.Contract", on_delete=models.CASCADE)
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    responses = models.ManyToManyField(FeedbackResponse)

    class Meta:
        db_table = "t_feedback"
        unique_together = [["contract", "created_by"]]

    @property
    def avg_rating(self):
        return self.responses.aggregate(average=Avg("rating", default=0))["average"]
