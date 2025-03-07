import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from polls.models import Question

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for future-time Question
        """
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for Questions that are more than a day old.
        """
        old_time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=old_time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for Questions published within one day.
        """
        recent_time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=recent_time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Creates a Question with the given `question_text`.
    Its posting date is either (positive) or (negative) days after or before the current time `days`.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If there are no problems, the index page should display the appropriate message.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Issues posted in the past should be displayed on the index page.
        """
        question = create_question("Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Issues for future releases should not be displayed on the index page.
        """
        create_question("Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        If there are both past and future issues, only the past issues should be displayed on the index page.
        """
        past_question = create_question("Past question.", days=-30)
        create_question("Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question])

    def test_two_past_questions(self):
        """
        The Index page should be able to display multiple past issues.
        """
        question1 = create_question("Past question 1.", days=-30)
        question2 = create_question("Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question2, question1])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Visiting the details page of an issue posted by future should return a 404 error.
        """
        future_question = create_question("Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The details page for past issues posted should display the issue content normally.
        """
        past_question = create_question("Past question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
