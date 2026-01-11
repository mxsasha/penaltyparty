import factory
from factory import post_generation
from factory.django import DjangoModelFactory

from penaltyparty.pp import models


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = models.Question

    question_text = factory.Sequence(lambda n: f"Question {n}")
    status = models.Question.STATUS.active


class AnswerFactory(DjangoModelFactory):
    class Meta:
        model = models.Answer

    question = factory.SubFactory(QuestionFactory)
    answer_text = factory.Sequence(lambda n: f"Answer {n}")
    is_correct = False
    status = models.Answer.STATUS.active


class TestGroupFactory(DjangoModelFactory):
    class Meta:
        model = models.TestGroup

    group_name = factory.Sequence(lambda n: f"Group{n}")
    owner_email = factory.LazyAttribute(lambda o: f"{o.group_name.lower()}@example.com")
    info_for_test_takers = ""

    @post_generation
    def questions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.questions.set(extracted)
        else:
            qs = models.Question.objects.all()[:5]
            if qs:
                self.questions.set(qs)


class TestAttemptFactory(DjangoModelFactory):
    class Meta:
        model = models.TestAttempt

    participant_name = factory.Sequence(lambda n: f"Participant{n}")
    test_group = factory.SubFactory(TestGroupFactory)


class TestAttemptAnswerFactory(DjangoModelFactory):
    class Meta:
        model = models.TestAttemptAnswer

    attempt = factory.SubFactory(TestAttemptFactory)
    answer = factory.SubFactory(AnswerFactory)
    question_text = factory.SelfAttribute("answer.question.question_text")
    answer_text = factory.SelfAttribute("answer.answer_text")
    is_correct = factory.SelfAttribute("answer.is_correct")
