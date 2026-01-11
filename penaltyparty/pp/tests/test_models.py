from django.test import TestCase
from django.db import IntegrityError

from penaltyparty.pp.models import Question, Answer, TestGroup, TestAttempt, TestAttemptAnswer
from .factories import (
    QuestionFactory,
    AnswerFactory,
    TestGroupFactory,
    TestAttemptFactory,
    TestAttemptAnswerFactory,
)


class QuestionModelTests(TestCase):
    def test_answers_random_and_correct(self):
        question = QuestionFactory()
        answers_list = [AnswerFactory(question=question, is_correct=(i == 0)) for i in range(4)]

        random_answers = question.answers_random()
        self.assertCountEqual([a.id for a in random_answers], [a.id for a in answers_list])

        self.assertEqual(question.correct_answer().id, answers_list[0].id)

    def test_correct_answer_raises_when_no_correct_exists(self):
        question = QuestionFactory()
        AnswerFactory(question=question, is_correct=False)
        AnswerFactory(question=question, is_correct=False)

        with self.assertRaises(Answer.DoesNotExist):
            question.correct_answer()

    def test_active_manager_returns_only_active_questions(self):
        active_question = QuestionFactory(status=Question.STATUS.active)
        QuestionFactory(status=Question.STATUS.inactive)

        qs = Question.active.all()
        self.assertIn(active_question, qs)
        self.assertEqual(qs.count(), 1)


class TestAttemptModelTests(TestCase):
    def test_next_question_and_final_score(self):
        questions = [QuestionFactory() for _ in range(3)]
        test_group = TestGroupFactory(questions=questions)
        attempt = TestAttemptFactory(test_group=test_group)

        chosen_question = attempt.next_question()
        self.assertIn(chosen_question.id, [q.id for q in questions])

        for question in questions:
            answer = AnswerFactory(question=question, is_correct=(question == questions[0]))
            TestAttemptAnswerFactory(attempt=attempt, answer=answer)

        self.assertIsNone(attempt.next_question())

        attempt.set_final_score()
        self.assertEqual(attempt.final_answered, attempt.answers.count())
        self.assertIsNotNone(attempt.final_correct)

        if attempt.final_answered:
            percent = attempt.correct_percentage()
            self.assertIsInstance(percent, int)

    def test_test_attempt_answer_unique_together_violated_raises_integrity_error(self):
        question = QuestionFactory()
        answer = AnswerFactory(question=question)
        test_group = TestGroupFactory(questions=[question])
        attempt = TestAttemptFactory(test_group=test_group)

        TestAttemptAnswerFactory(attempt=attempt, answer=answer)

        with self.assertRaises(IntegrityError):
            TestAttemptAnswer.objects.create(
                attempt=attempt,
                answer=answer,
                question_text=answer.question.question_text,
                answer_text=answer.answer_text,
                is_correct=answer.is_correct,
            )

    def test_correct_percentage_raises_on_zero_answered(self):
        test_group = TestGroupFactory()
        attempt = TestAttemptFactory(test_group=test_group)

        attempt.set_final_score()
        self.assertEqual(attempt.final_answered, 0)

        with self.assertRaises(ZeroDivisionError):
            attempt.correct_percentage()
