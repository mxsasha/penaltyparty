from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail

from penaltyparty.pp.models import TestGroup, TestAttempt, TestAttemptAnswer, Question
from .factories import QuestionFactory, AnswerFactory, TestGroupFactory, TestAttemptFactory, TestAttemptAnswerFactory


class IndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_shows_random_question(self):
        question = QuestionFactory()

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("random_question", response.context)
        self.assertEqual(response.context["random_question"].id, question.id)


@override_settings(TEST_GROUP_QUESTION_AMOUNT=5)
class TestGroupCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_view_creates_group_and_sends_email(self):
        for _ in range(5):
            QuestionFactory()

        data = {
            "group_name": "Testers",
            "owner_email": "owner@example.com",
            "info_for_test_takers": "Info",
        }
        create_response = self.client.post(reverse("test_group_create"), data)
        self.assertEqual(create_response.status_code, 302)

        test_group = TestGroup.objects.get(owner_email="owner@example.com")
        self.assertEqual(test_group.questions.count(), 5)

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn("owner@example.com", sent.to)
        self.assertTrue(sent.subject)
        self.assertIn("Testers", sent.body)

    def test_create_view_fails_when_not_enough_active_questions(self):
        for _ in range(2):
            QuestionFactory(status=Question.STATUS.active)

        data = {
            "group_name": "FewQuestions",
            "owner_email": "owner@example.com",
            "info_for_test_takers": "",
        }
        response = self.client.post(reverse("test_group_create"), data)
        self.assertEqual(response.status_code, 500)

    def test_create_view_invalid_form_shows_errors(self):
        QuestionFactory()
        data = {
            "group_name": "NoEmail",
            "info_for_test_takers": "Missing email",
        }
        response = self.client.post(reverse("test_group_create"), data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertIn("owner_email", form.errors)


class TestGroupTakeViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_take_view_creates_attempt_and_redirects(self):
        question = QuestionFactory()
        test_group = TestGroupFactory(questions=[question])

        url = reverse("test_group_take", kwargs={"group_token": test_group.token_test_taker})
        take_response = self.client.post(url, {"participant_name": "Alice"})
        self.assertEqual(take_response.status_code, 302)

        test_attempt = TestAttempt.objects.get(test_group=test_group, participant_name="Alice")
        self.assertIsNotNone(test_attempt)

    def test_take_view_404_for_invalid_group_token(self):
        response = self.client.get(reverse("test_group_take", kwargs={"group_token": "nope"}))
        self.assertEqual(response.status_code, 404)


class TestAttemptEnterAnswerViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_enter_answer_get_and_post_creates_attempt_answer(self):
        question = QuestionFactory()
        answer_correct = AnswerFactory(question=question, is_correct=True)
        AnswerFactory(question=question, is_correct=False)
        test_group = TestGroupFactory(questions=[question])
        attempt = TestAttemptFactory(test_group=test_group)

        url = reverse("test_attempt_enter_answer", kwargs={"token": attempt.token, "question": question.pk})
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(url, {"answer": str(answer_correct.id)})
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(TestAttemptAnswer.objects.filter(attempt=attempt, answer=answer_correct).exists())

    def test_enter_answer_post_with_invalid_answer_id_returns_404(self):
        question = QuestionFactory()
        AnswerFactory(question=question, is_correct=True)
        test_group = TestGroupFactory(questions=[question])
        attempt = TestAttemptFactory(test_group=test_group)

        url = reverse("test_attempt_enter_answer", kwargs={"token": attempt.token, "question": question.pk})
        response = self.client.post(url, {"answer": "999999"})
        self.assertEqual(response.status_code, 404)

    def test_enter_answer_redirects_if_question_already_answered(self):
        question = QuestionFactory()
        answer = AnswerFactory(question=question, is_correct=True)
        test_group = TestGroupFactory(questions=[question])
        attempt = TestAttemptFactory(test_group=test_group)

        TestAttemptAnswerFactory(attempt=attempt, answer=answer)

        url = reverse("test_attempt_enter_answer", kwargs={"token": attempt.token, "question": question.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TestAttemptNextQuestionViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_next_question_redirects_to_enter_answer_when_questions_remain(self):
        question = QuestionFactory()
        test_group = TestGroupFactory(questions=[question])
        attempt = TestAttemptFactory(test_group=test_group)

        url = reverse("test_attempt_next_question", kwargs={"token": attempt.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        target = reverse("test_attempt_enter_answer", kwargs={"token": attempt.token, "question": question.pk})
        self.assertTrue(response["Location"].endswith(target))

    def test_next_question_marks_done_when_no_questions_remain(self):
        questions = [QuestionFactory() for _ in range(2)]
        test_group = TestGroupFactory(questions=questions)
        attempt = TestAttemptFactory(test_group=test_group)

        for question in questions:
            answer = AnswerFactory(question=question, is_correct=True)
            self.client.post(
                reverse("test_attempt_enter_answer", kwargs={"token": attempt.token, "question": question.pk}),
                {"answer": str(answer.id)},
            )

        done_response = self.client.get(reverse("test_attempt_next_question", kwargs={"token": attempt.token}))
        self.assertEqual(done_response.status_code, 302)

        done_url = reverse("test_attempt_done", kwargs={"token": attempt.token})
        self.assertTrue(done_response["Location"].endswith(done_url))
