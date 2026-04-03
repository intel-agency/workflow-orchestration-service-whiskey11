"""Tests for src.models.work_item — model creation, validation, serialization, enums, scrub_secrets."""

import pytest
from datetime import datetime, timezone

from src.models.work_item import (
    TaskType,
    WorkItemStatus,
    WorkItem,
    scrub_secrets,
)
from src.models import (
    WorkItem as WorkItemFromInit,
    TaskType as TaskTypeFromInit,
    WorkItemStatus as WorkItemStatusFromInit,
    scrub_secrets as scrub_secrets_from_init,
)


# ---------------------------------------------------------------------------
# TaskType enum
# ---------------------------------------------------------------------------


class TestTaskType:
    """Test the TaskType enum values and behavior."""

    def test_existing_plan_value(self):
        assert TaskType.PLAN == "PLAN"
        assert TaskType.PLAN.value == "PLAN"

    def test_existing_implement_value(self):
        assert TaskType.IMPLEMENT == "IMPLEMENT"

    def test_existing_bugfix_value(self):
        assert TaskType.BUGFIX == "BUGFIX"

    def test_new_pull_request_value(self):
        assert TaskType.PULL_REQUEST == "PULL_REQUEST"

    def test_new_review_value(self):
        assert TaskType.REVIEW == "REVIEW"

    def test_new_workflow_dispatch_value(self):
        assert TaskType.WORKFLOW_DISPATCH == "WORKFLOW_DISPATCH"

    def test_new_other_value(self):
        assert TaskType.OTHER == "OTHER"

    def test_total_enum_members(self):
        assert len(TaskType) == 7

    def test_from_string_value(self):
        assert TaskType("PLAN") == TaskType.PLAN
        assert TaskType("OTHER") == TaskType.OTHER

    def test_string_comparison(self):
        """TaskType inherits from str, so comparisons work directly."""
        assert TaskType.PLAN == "PLAN"
        assert TaskType.OTHER == "OTHER"

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            TaskType("INVALID")


# ---------------------------------------------------------------------------
# WorkItemStatus enum
# ---------------------------------------------------------------------------


class TestWorkItemStatus:
    """Test the WorkItemStatus enum — both legacy label-based and generic values."""

    def test_existing_queued(self):
        assert WorkItemStatus.QUEUED == "agent:queued"

    def test_existing_in_progress(self):
        assert WorkItemStatus.IN_PROGRESS == "agent:in-progress"

    def test_existing_reconciling(self):
        assert WorkItemStatus.RECONCILING == "agent:reconciling"

    def test_existing_success(self):
        assert WorkItemStatus.SUCCESS == "agent:success"

    def test_existing_error(self):
        assert WorkItemStatus.ERROR == "agent:error"

    def test_existing_infra_failure(self):
        assert WorkItemStatus.INFRA_FAILURE == "agent:infra-failure"

    def test_existing_stalled_budget(self):
        assert WorkItemStatus.STALLED_BUDGET == "agent:stalled-budget"

    def test_new_pending(self):
        assert WorkItemStatus.PENDING == "PENDING"

    def test_new_completed(self):
        assert WorkItemStatus.COMPLETED == "COMPLETED"

    def test_new_failed(self):
        assert WorkItemStatus.FAILED == "FAILED"

    def test_new_cancelled(self):
        assert WorkItemStatus.CANCELLED == "CANCELLED"

    def test_total_enum_members(self):
        # 7 legacy + 4 generic = 11
        assert len(WorkItemStatus) == 11

    def test_generic_and_legacy_values_dont_collide(self):
        """Generic string values should differ from all legacy label values."""
        generic_values = {
            WorkItemStatus.PENDING.value,
            WorkItemStatus.COMPLETED.value,
            WorkItemStatus.FAILED.value,
            WorkItemStatus.CANCELLED.value,
        }
        legacy_values = {
            WorkItemStatus.QUEUED.value,
            WorkItemStatus.IN_PROGRESS.value,
            WorkItemStatus.RECONCILING.value,
            WorkItemStatus.SUCCESS.value,
            WorkItemStatus.ERROR.value,
            WorkItemStatus.INFRA_FAILURE.value,
            WorkItemStatus.STALLED_BUDGET.value,
        }
        assert generic_values.isdisjoint(legacy_values)


# ---------------------------------------------------------------------------
# WorkItem model
# ---------------------------------------------------------------------------


class TestWorkItem:
    """Test WorkItem model creation, validation, and serialization."""

    SAMPLE_MINIMAL = {
        "id": "12345",
        "issue_number": 42,
        "source_url": "https://github.com/org/repo/issues/42",
        "context_body": "Do the thing",
        "target_repo_slug": "org/repo",
        "task_type": TaskType.IMPLEMENT,
        "status": WorkItemStatus.QUEUED,
        "node_id": "NODE_12345",
    }

    def test_create_minimal(self):
        item = WorkItem(**self.SAMPLE_MINIMAL)
        assert item.id == "12345"
        assert item.issue_number == 42
        assert item.task_type == TaskType.IMPLEMENT
        assert item.status == WorkItemStatus.QUEUED

    def test_optional_fields_default_none(self):
        item = WorkItem(**self.SAMPLE_MINIMAL)
        assert item.title is None
        assert item.body is None
        assert item.repository is None
        assert item.created_at is None
        assert item.updated_at is None

    def test_optional_list_fields_default_empty(self):
        item = WorkItem(**self.SAMPLE_MINIMAL)
        assert item.labels == []
        assert item.assignees == []
        assert item.metadata == {}

    def test_create_with_all_fields(self):
        now = datetime.now(timezone.utc)
        item = WorkItem(
            **self.SAMPLE_MINIMAL,
            title="Test Issue",
            body="Detailed description",
            repository="org/repo",
            labels=["bug", "enhancement"],
            assignees=["alice", "bob"],
            created_at=now,
            updated_at=now,
            metadata={"priority": "high", "estimate": 5},
        )
        assert item.title == "Test Issue"
        assert item.body == "Detailed description"
        assert item.repository == "org/repo"
        assert "bug" in item.labels
        assert "alice" in item.assignees
        assert item.created_at == now
        assert item.metadata["priority"] == "high"

    def test_model_config_from_attributes(self):
        """Verify from_attributes=True is set for ORM-style usage."""
        assert WorkItem.model_config.get("from_attributes") is True

    def test_serialization_roundtrip(self):
        """Verify JSON serialization and deserialization works."""
        item = WorkItem(**self.SAMPLE_MINIMAL, title="Roundtrip Test")
        json_str = item.model_dump_json()
        restored = WorkItem.model_validate_json(json_str)
        assert restored.id == item.id
        assert restored.title == item.title
        assert restored.task_type == item.task_type

    def test_model_dump(self):
        item = WorkItem(**self.SAMPLE_MINIMAL)
        data = item.model_dump()
        assert data["id"] == "12345"
        assert data["issue_number"] == 42
        assert data["labels"] == []

    def test_task_type_from_string(self):
        """Verify string values can be used for task_type in construction."""
        data = {**self.SAMPLE_MINIMAL, "task_type": "PLAN"}
        item = WorkItem(**data)
        assert item.task_type == TaskType.PLAN

    def test_status_from_string(self):
        """Verify string values can be used for status in construction."""
        data = {**self.SAMPLE_MINIMAL, "status": "PENDING"}
        item = WorkItem(**data)
        assert item.status == WorkItemStatus.PENDING

    def test_invalid_task_type_raises(self):
        with pytest.raises(Exception):
            WorkItem(**{**self.SAMPLE_MINIMAL, "task_type": "INVALID"})

    def test_invalid_status_raises(self):
        with pytest.raises(Exception):
            WorkItem(**{**self.SAMPLE_MINIMAL, "status": "INVALID"})

    def test_missing_required_field_raises(self):
        """id is required — omitting it should raise validation error."""
        with pytest.raises(Exception):
            WorkItem(
                issue_number=1,
                source_url="http://example.com",
                context_body="test",
                target_repo_slug="org/repo",
                task_type=TaskType.PLAN,
                status=WorkItemStatus.QUEUED,
                node_id="NODE_1",
            )


# ---------------------------------------------------------------------------
# __init__.py re-exports
# ---------------------------------------------------------------------------


class TestReExports:
    """Verify that src.models.__init__ re-exports the expected names."""

    def test_workitem_reexport(self):
        assert WorkItemFromInit is WorkItem

    def test_tasktype_reexport(self):
        assert TaskTypeFromInit is TaskType

    def test_workitemstatus_reexport(self):
        assert WorkItemStatusFromInit is WorkItemStatus

    def test_scrub_secrets_reexport(self):
        assert scrub_secrets_from_init is scrub_secrets


# ---------------------------------------------------------------------------
# scrub_secrets
# ---------------------------------------------------------------------------


class TestScrubSecrets:
    """Test credential scrubbing with synthetic (non-real) patterns."""

    def test_no_secrets_unchanged(self):
        assert scrub_secrets("hello world") == "hello world"

    def test_empty_string(self):
        assert scrub_secrets("") == ""

    def test_bearer_token_redacted(self):
        """Matches 'Bearer <token>' pattern."""
        text = "Authorization: Bearer FAKE-BEARER-TOKEN-FOR-TESTING-ONLY-12345678901234567890=="
        result = scrub_secrets(text)
        assert "***REDACTED***" in result
        assert "FAKE-BEARER-TOKEN" not in result

    def test_bearer_case_insensitive(self):
        text = "auth: bearer SOMEFAKETOKEN12345678901234567890=="
        result = scrub_secrets(text)
        assert "***REDACTED***" in result

    def test_custom_replacement(self):
        text = "Authorization: Bearer FAKE-BEARER-TOKEN-FOR-TESTING-ONLY-12345678901234567890=="
        result = scrub_secrets(text, replacement="[HIDDEN]")
        assert "[HIDDEN]" in result

    def test_multiple_secrets_in_text(self):
        """Multiple patterns in one string should all be redacted."""
        text = (
            "key1: Bearer FAKE-BEARER-TOKEN-FOR-TESTING-ONLY-12345678901234567890== "
            "and key2: Bearer ANOTHER-FAKE-TOKEN-FOR-TESTING-ONLY-98765432109876543210=="
        )
        result = scrub_secrets(text)
        assert result.count("***REDACTED***") == 2
