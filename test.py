import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from polls.models import Question


class QuestionModelTests(TestCase):
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
        recent_time = timezone.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        recent_question = Question(pub_date=recent_time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Creates a Question with the given `question_text`.
    Its posting date is either (positive) or (negative) days after or before the current time `days`.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionDetailViewTests(TestCase):
    def test_past_question(self):
        """
        The details page for past issues posted should display the issue content normally.
        """
        past_question = create_question("Past question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
