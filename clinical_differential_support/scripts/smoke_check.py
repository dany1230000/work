import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    name: str
    url: str
    expected_status: int
    expected_text: str = ""
    expected_json_status: str = ""
    expected_location: str = ""


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def normalize_base_url(base_url):
    return base_url.rstrip("/")


def build_check_plan(base_url):
    base = normalize_base_url(base_url)
    return [
        Check(
            name="health",
            url=f"{base}/health/",
            expected_status=200,
            expected_json_status="ok",
        ),
        Check(
            name="home",
            url=f"{base}/",
            expected_status=200,
            expected_text="Clinical Differential Support",
        ),
        Check(
            name="launch_guide",
            url=f"{base}/launch/",
            expected_status=200,
            expected_text="Local Control Panel",
        ),
        Check(
            name="completion_gate",
            url=f"{base}/completion/",
            expected_status=200,
            expected_text="Final Project Gate",
        ),
        Check(
            name="deployment_status",
            url=f"{base}/deployment/",
            expected_status=200,
            expected_text="Deployment Operations Center",
        ),
        Check(
            name="chest_pain",
            url=f"{base}/chest-pain/",
            expected_status=200,
            expected_text="Chest Pain Intake",
        ),
        Check(
            name="abdominal_pain",
            url=f"{base}/abdominal-pain/",
            expected_status=200,
            expected_text="Abdominal Pain Intake",
        ),
        Check(
            name="dyspnea",
            url=f"{base}/dyspnea/",
            expected_status=200,
            expected_text="Dyspnea Intake",
        ),
        Check(
            name="review_login",
            url=f"{base}/review/login/",
            expected_status=200,
            expected_text="Reviewer Login",
        ),
        Check(
            name="review_queue",
            url=f"{base}/review/queue/",
            expected_status=200,
            expected_text="Reviewer Queue",
        ),
        Check(
            name="protected_source_create",
            url=f"{base}/review/sources/new/",
            expected_status=302,
            expected_location="/review/login/?next=/review/sources/new/",
        ),
        Check(
            name="protected_handoff_report",
            url=f"{base}/review/exports/handoff-report.md",
            expected_status=302,
            expected_location="/review/login/?next=/review/exports/handoff-report.md",
        ),
        Check(
            name="protected_handoff_bundle",
            url=f"{base}/review/exports/handoff-bundle.zip",
            expected_status=302,
            expected_location="/review/login/?next=/review/exports/handoff-bundle.zip",
        ),
        Check(
            name="protected_next_actions",
            url=f"{base}/review/next-actions/",
            expected_status=302,
            expected_location="/review/login/?next=/review/next-actions/",
        ),
        Check(
            name="protected_next_actions_json",
            url=f"{base}/review/exports/next-actions.json",
            expected_status=302,
            expected_location="/review/login/?next=/review/exports/next-actions.json",
        ),
        Check(
            name="protected_coverage_depth",
            url=f"{base}/review/coverage-depth/",
            expected_status=302,
            expected_location="/review/login/?next=/review/coverage-depth/",
        ),
        Check(
            name="protected_coverage_depth_json",
            url=f"{base}/review/exports/coverage-depth.json",
            expected_status=302,
            expected_location="/review/login/?next=/review/exports/coverage-depth.json",
        ),
        Check(
            name="protected_source_freshness",
            url=f"{base}/review/source-freshness/",
            expected_status=302,
            expected_location="/review/login/?next=/review/source-freshness/",
        ),
        Check(
            name="protected_source_freshness_json",
            url=f"{base}/review/exports/source-freshness.json",
            expected_status=302,
            expected_location="/review/login/?next=/review/exports/source-freshness.json",
        ),
        Check(
            name="protected_final_verification",
            url=f"{base}/review/final-verification/",
            expected_status=302,
            expected_location="/review/login/?next=/review/final-verification/",
        ),
        Check(
            name="protected_final_verification_json",
            url=f"{base}/review/exports/final-verification.json",
            expected_status=302,
            expected_location="/review/login/?next=/review/exports/final-verification.json",
        ),
    ]


def open_without_redirects(url, timeout):
    opener = urllib.request.build_opener(NoRedirectHandler)
    request = urllib.request.Request(url, headers={"User-Agent": "cds-smoke-check"})
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        return error


def run_check(check, timeout):
    response = open_without_redirects(check.url, timeout)
    status = response.getcode()
    body = response.read().decode("utf-8", errors="replace")
    if status != check.expected_status:
        return False, f"{check.name}: expected HTTP {check.expected_status}, got {status}"
    if check.expected_text and check.expected_text not in body:
        return False, f"{check.name}: missing expected text {check.expected_text!r}"
    if check.expected_json_status:
        payload = json.loads(body)
        if payload.get("status") != check.expected_json_status:
            return False, f"{check.name}: expected status={check.expected_json_status!r}, got {payload.get('status')!r}"
    if check.expected_location:
        location = response.headers.get("Location", "")
        if location != check.expected_location:
            return False, f"{check.name}: expected Location {check.expected_location!r}, got {location!r}"
    return True, f"{check.name}: ok"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Smoke-check the local CDS MVP.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args(argv)

    all_ok = True
    for check in build_check_plan(args.base_url):
        ok, message = run_check(check, args.timeout)
        print(message)
        all_ok = all_ok and ok
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
