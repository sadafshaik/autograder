from django.db import models

 #class User(models.Model):

        

class Question(models.Model):
    question_title = models.TextField(max_length=100000)
    setn = models.IntegerField(unique=True)
    min_score = models.IntegerField()
    max_score = models.IntegerField()

    def __str__(self):
        return str(self.setn)

class Essay(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField(max_length=100000)
    score = models.IntegerField(null=True, blank=True)