from django.contrib import admin

# Register your models here.
from .models import Feedback, FeedbackQuestion, FeedbackResponse

admin.site.register(FeedbackQuestion)
admin.site.register(FeedbackResponse)
admin.site.register(Feedback)