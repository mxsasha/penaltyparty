import random

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, FormView, RedirectView
from honeypot.decorators import check_honeypot
from penaltyparty.pp.models import (
    Answer,
    Question,
    TestAttempt,
    TestAttemptAnswer,
    TestGroup,
)

TEST_GROUP_QUESTION_AMOUNT = 40


def index(request):
    pks = Question.objects.values_list("pk", flat=True)
    if pks:
        random_pk = random.choice(pks)
        random_question = Question.objects.get(pk=random_pk)
    else:
        random_question = None
    return render(request, template_name="index.html", context={"random_question": random_question})


@method_decorator(check_honeypot, name="post")
class TestGroupCreateView(CreateView):
    model = TestGroup
    fields = ["group_name", "owner_email", "info_for_test_takers"]
    template_name = "test_group_create.html"

    def form_valid(self, form):
        pks = Question.objects.values_list("pk", flat=True)
        random_pk = random.sample(list(pks), TEST_GROUP_QUESTION_AMOUNT)
        self.object = form.save()
        self.object.questions.set(Question.objects.filter(pk__in=random_pk))

        mail_context = {"test_group": self.object, "request": self.request}
        subject = render_to_string("test_group_created_subject.txt", mail_context).strip()
        body = render_to_string("test_group_created_body.txt", mail_context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [self.object.owner_email])

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("test_group_owner", kwargs={"token": self.object.token_owner})


class TestGroupOwnerView(DetailView):
    model = TestGroup
    template_name = "test_group_owner.html"
    context_object_name = "test_group"
    slug_url_kwarg = "token"
    slug_field = "token_owner"


class TestGroupTakeView(CreateView):
    model = TestAttempt
    fields = ["participant_name"]
    template_name = "test_attempt_start.html"

    def dispatch(self, request, *args, **kwargs):
        self.test_group = get_object_or_404(TestGroup, token_test_taker=self.kwargs.get("group_token"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["test_group"] = self.test_group
        return context

    def form_valid(self, form):
        form.instance.test_group = self.test_group
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("test_attempt_next_question", kwargs={"token": self.object.token})


class TestAttemptNextQuestionView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        test_attempt = get_object_or_404(TestAttempt, token=self.kwargs.get("token"))
        question = test_attempt.next_question()
        if not question:
            test_attempt.set_final_score()
            test_attempt.save()
            return reverse("test_attempt_done", kwargs={"token": test_attempt.token})
        return reverse(
            "test_attempt_enter_answer", kwargs={"token": test_attempt.token, "question": question.pk}
        )


class TestAttemptDoneView(DetailView):
    model = TestAttempt
    template_name = "test_attempt_done.html"
    context_object_name = "test_attempt"
    slug_url_kwarg = "token"
    slug_field = "token"


class AnswerForm(forms.Form):
    answer = forms.ChoiceField(widget=forms.RadioSelect, label="Your answer")

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(answer.id, answer.answer_text) for answer in question.answers_random()]
        self.fields["answer"].choices = choices


class TestAttemptEnterAnswerView(FormView):
    template_name = "test_attempt_enter_answer.html"
    form_class = AnswerForm
    question = None

    def dispatch(self, request, *args, **kwargs):
        self.test_attempt = get_object_or_404(TestAttempt, token=self.kwargs.get("token"))
        self.question = get_object_or_404(Question, pk=self.kwargs.get("question"))
        if self.question in [answer.question for answer in self.test_attempt.answers.all()]:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"question": self.question})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.question
        return context

    def form_valid(self, form):
        answer = get_object_or_404(Answer, id=form.cleaned_data["answer"])

        # Create a new TestAttemptAnswer record
        TestAttemptAnswer.objects.create(
            attempt=self.test_attempt,
            answer=answer,
            question_text=answer.question.question_text,
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("test_attempt_next_question", kwargs={"token": self.test_attempt.token})
