import random

from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField, UrlsafeTokenField
from model_utils.models import TimeStampedModel


class Question(TimeStampedModel):
    STATUS = Choices("active", "inactive")
    question_text = models.TextField(unique=True)
    status = StatusField()
    rule_section = models.CharField(max_length=250, null=True, blank=True)
    rule_scenario = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.question_text

    def answers_random(self):
        answers = list(self.answer_set.all())
        random.shuffle(answers)
        return answers

    def correct_answer(self):
        return self.answer_set.get(is_correct=True)


class Answer(TimeStampedModel):
    STATUS = Choices("active", "inactive")
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    status = StatusField()

    def __str__(self):
        return self.answer_text


class TestGroup(TimeStampedModel):
    token_owner = UrlsafeTokenField(editable=False, max_length=32, unique=True)
    token_test_taker = UrlsafeTokenField(editable=False, max_length=32, unique=True)
    group_name = models.CharField(max_length=255, help_text="E.g. 'Rookies 2024' or 'ERD rules checkup'")
    owner_email = models.EmailField(verbose_name="Your email")
    info_for_test_takers = models.TextField(
        verbose_name="Anything you want to share with people taking your test (optional)",
        help_text="Any test taker will see this before beginning their test.",
        null=True,
        blank=True,
    )
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.group_name

    def completed_attempts(self):
        return self.testattempt_set.filter(final_answered__isnull=False)


class TestAttempt(TimeStampedModel):
    token = UrlsafeTokenField(editable=False, max_length=32, unique=True)
    participant_name = models.CharField(max_length=255, verbose_name="Your name")
    answers = models.ManyToManyField(Answer, through="TestAttemptAnswer")
    test_group = models.ForeignKey(TestGroup, on_delete=models.PROTECT)
    final_correct = models.PositiveIntegerField(null=True, blank=True)
    final_answered = models.PositiveIntegerField(null=True, blank=True)

    def next_question(self):
        answered_question_ids = [answer.question.id for answer in self.answers.all()]
        remaining_questions = self.test_group.questions.exclude(id__in=answered_question_ids)

        if not remaining_questions.exists():
            return None

        # Pick a random unanswered question
        return random.choice(remaining_questions)

    def set_final_score(self):
        self.final_answered = self.answers.count()
        self.final_correct = self.answers.filter(is_correct=True).count()

    def correct_percentage(self):
        return int(self.final_correct * 100 / self.final_answered)

    def correct_answers(self):
        return self.answers.filter(is_correct=True)

    def incorrect_answers(self):
        return self.answers.filter(is_correct=False)


class TestAttemptAnswer(TimeStampedModel):
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT)
    attempt = models.ForeignKey(TestAttempt, on_delete=models.PROTECT)
    question_text = models.TextField()
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = (("answer", "attempt"),)
