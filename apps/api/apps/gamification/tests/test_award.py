from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.gamification.models import PointsLedger, UserPoints
from apps.gamification.services import award_points

User = get_user_model()


@pytest.mark.django_db
def test_award_points_increments_ledger():
    user = User.objects.create_user(email="gamer@example.com", password="pass12345")
    points = award_points(user, 25, "test_award", ref="unit")
    assert points.balance == 25
    assert points.lifetime == 25
    assert PointsLedger.objects.filter(user=user, delta=25).count() == 1
    award_points(user, 10, "test_award_2")
    points = UserPoints.objects.get(user=user)
    assert points.balance == 35
    assert PointsLedger.objects.filter(user=user).count() == 2
