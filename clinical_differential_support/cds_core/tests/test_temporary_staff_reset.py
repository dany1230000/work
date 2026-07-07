import hashlib
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


def _token_hash(token):
    return "sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest()


class TemporaryStaffResetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.token = "valid-test-reset-token"
        self.patchers = [
            mock.patch("cds_core.views.TEMP_STAFF_RESET_TOKEN_HASH", _token_hash(self.token)),
            mock.patch("cds_core.views.TEMP_STAFF_RESET_EXPIRES_AT", timezone.now() + timedelta(days=1)),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_reset_page_requires_valid_one_time_token(self):
        reset_url = reverse("cds_core:temporary_staff_password_reset")

        self.assertEqual(self.client.get(reset_url).status_code, 404)
        self.assertEqual(self.client.get(reset_url, {"token": "wrong-token"}).status_code, 404)

        response = self.client.get(reset_url, {"token": self.token})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-temporary-staff-reset="true"')
        self.assertContains(response, "臨時重設 staff 密碼")
        self.assertContains(response, "Temporary staff password reset")
        self.assertContains(response, "不會列印或保存密碼")

    def test_reset_creates_staff_reviewer_and_consumes_token(self):
        reset_url = reverse("cds_core:temporary_staff_password_reset")
        password = "Reset-Strong-Pass-2026-Alpha!"

        response = self.client.post(
            reset_url,
            {
                "token": self.token,
                "password1": password,
                "password2": password,
            },
        )

        self.assertRedirects(response, reverse("cds_core:review_login"))
        user = get_user_model().objects.get(username="dany1230")
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(password))

        reused = self.client.post(
            reset_url,
            {
                "token": self.token,
                "password1": "Different-Strong-Pass-2026-Alpha!",
                "password2": "Different-Strong-Pass-2026-Alpha!",
            },
        )
        user.refresh_from_db()
        self.assertEqual(reused.status_code, 404)
        self.assertTrue(user.check_password(password))

    def test_reset_rejects_mismatched_password_without_creating_user(self):
        reset_url = reverse("cds_core:temporary_staff_password_reset")

        response = self.client.post(
            reset_url,
            {
                "token": self.token,
                "password1": "Reset-Strong-Pass-2026-Alpha!",
                "password2": "Reset-Strong-Pass-2026-Beta!",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "兩次密碼不一致", status_code=400)
        self.assertFalse(get_user_model().objects.filter(username="dany1230").exists())
