from django.urls import path

from . import views
from .views import (
    TestAttemptDoneView,
    TestAttemptEnterAnswerView,
    TestAttemptNextQuestionView,
    TestGroupCreateView,
    TestGroupOwnerView,
    TestGroupTakeView,
)

urlpatterns = [
    path("", views.index, name="index"),
    path("group/new/", TestGroupCreateView.as_view(), name="test_group_create"),
    path("group/owner/<str:token>/", TestGroupOwnerView.as_view(), name="test_group_owner"),
    path("test/take/<str:group_token>/", TestGroupTakeView.as_view(), name="test_group_take"),
    path("answer/<str:token>/", TestAttemptNextQuestionView.as_view(), name="test_attempt_next_question"),
    path("answer/<str:token>/done/", TestAttemptDoneView.as_view(), name="test_attempt_done"),
    path(
        "answer/<str:token>/<str:question>/",
        TestAttemptEnterAnswerView.as_view(),
        name="test_attempt_enter_answer",
    ),
]
