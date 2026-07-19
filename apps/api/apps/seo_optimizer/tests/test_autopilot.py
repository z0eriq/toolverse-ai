from __future__ import annotations

import pytest

from apps.seo_optimizer.autopilot import apply_page_issue, scan_seo_autopilot
from apps.seo_optimizer.models import SeoHealthScore, SeoPageIssue
from apps.tools_registry.models import Category, Tool


@pytest.mark.django_db
def test_scan_creates_issues():
    SeoHealthScore.objects.create(
        path="tools/pdf/merge",
        metadata=30.0,
        schema=40.0,
        internal_links=40.0,
        content_quality=40.0,
        keyword_coverage=40.0,
        performance=50.0,
        overall=35.0,
    )
    run = scan_seo_autopilot()
    assert run.status == "success"
    assert run.issues_created >= 1
    assert SeoPageIssue.objects.filter(path="tools/pdf/merge").exists()


@pytest.mark.django_db
def test_apply_works_on_tool_path():
    category = Category.objects.create(
        slug="pdf",
        name={"en": "PDF"},
        description={"en": "PDF tools"},
    )
    tool = Tool.objects.create(
        tool_id="pdf-merge",
        slug="merge",
        category=category,
        name={"en": "PDF Merge"},
        description={"en": "Merge PDF files"},
        seo_title={"en": "Short"},
        seo_description={"en": "Too short"},
        is_active=True,
    )
    issue = SeoPageIssue.objects.create(
        path="tools/pdf/merge",
        issue_type=SeoPageIssue.IssueType.META,
        severity=SeoPageIssue.Severity.HIGH,
        suggestion="Improve meta",
        status=SeoPageIssue.Status.OPEN,
        evidence={},
    )
    applied = apply_page_issue(issue)
    assert applied.status == SeoPageIssue.Status.APPLIED
    tool.refresh_from_db()
    assert "ToolVerse" in str(tool.seo_title.get("en", ""))
    assert issue.apply_logs.count() == 1
