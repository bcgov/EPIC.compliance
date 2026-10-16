"""Tests for reopening an issued inspection record."""
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from compliance_api.models import IRApprovalStatusEnum, IRProgressEnum
from compliance_api.models.inspection_record import IRStatusEnum
from compliance_api.services.inspection_record import inspection_record_approval as module
from compliance_api.services.inspection_record.inspection_record_approval import InspectionRecordApprovalService


@contextmanager
def _fake_session_scope():
    yield "session"


@pytest.mark.parametrize(
    "is_history, expected_progress, deactivates_approval",
    [
        (True, IRProgressEnum.FINAL_APPROVED, False),
        (False, IRProgressEnum.FINALIZING_RECORD, True),
    ],
)
def test_reopen_final_ir(is_history, expected_progress, deactivates_approval):
    """Historical IRs skip DDO approval on reopen; regular IRs return to finalizing."""
    approval = SimpleNamespace(id=7, approval_status=IRApprovalStatusEnum.APPROVED)
    with patch.object(module, "ServiceUtils") as service_utils, patch.object(
        module, "InspectionRecordModel"
    ) as ir_model, patch.object(
        module, "InspectionRecordApprovalModel"
    ) as approval_model, patch.object(
        module, "session_scope", _fake_session_scope
    ):
        service_utils.inspection_exist_check.return_value = SimpleNamespace(is_history=is_history)
        service_utils.inspection_record_exist_check.return_value = SimpleNamespace(
            ir_status_id=IRStatusEnum.FINAL.value
        )
        approval_model.get_latest_approval_by_ir.return_value = approval

        InspectionRecordApprovalService.reopen(1, 2, 7)

        ir_model.update_inspection_record.assert_called_once_with(
            inspection_record_id=2,
            ir_update_data={"ir_progress": expected_progress, "date_issued": None},
            session="session",
        )
        assert approval_model.update_approval.called is deactivates_approval
