import GridLabelValuePair from "@/components/Shared/GridLabelValuePair";
import { AddRounded } from "@mui/icons-material";
import { Box, Grid, Typography, Link, Button } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import MailingAddressPopover from "./MailingAddressPopover";
import PreparedByPopover from "./PreparedByPopover";
import { usePopover } from "@/store/popoverStore";
import { useEffect, useState } from "react";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import {
  formatAuthorization,
  renderStaffNameWithPosition,
} from "@/utils/appUtils";
import { useUpdateInspectionRecord } from "@/hooks/useInspectionReports";
import { notify } from "@/store/snackbarStore";
import { InspectionRecord } from "@/models/InspectionRecord";
import { IRProgressEnum } from "@/utils/constants";
import { StaffUser } from "@/models/Staff";

const ProjectOverview = () => {
  const {
    inspectionData,
    caseFileData,
    inspectionReportsData,
    irApprovalsData,
    isReportsReadOnly,
    setInspectionReportsData,
  } = useReportStore();
  const { setOpen, setClose } = usePopover();
  const [mailingAddress, setMailingAddress] = useState("");
  const [recordPreparedBy, setRecordPreparedBy] = useState<StaffUser | null>(
    null
  );

  useEffect(() => {
    setMailingAddress(inspectionReportsData?.mailing_address ?? "");
    const recordPreparedBy = inspectionReportsData?.record_prepared_by;
    if (recordPreparedBy) {
      recordPreparedBy.position =
        inspectionReportsData?.record_prepared_by_position;
    }
    setRecordPreparedBy(recordPreparedBy ?? null);
  }, [inspectionReportsData]);

  const handleOnSuccess = (data: InspectionRecord) => {
    notify.success("Record updated");
    setInspectionReportsData(data);
    setClose();
  };

  const { mutate: updateInspectionRecord, isPending: isSaving } =
    useUpdateInspectionRecord(handleOnSuccess);

  const updateMailingAddress = (mailingAddress: string) => {
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: "mailing_address",
        value: mailingAddress,
      },
    });
  };

  const updatePrimaryOfficer = (primaryOfficerId: number) => {
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: "record_prepared_by_id",
        value: primaryOfficerId.toString(),
      },
    });
  };

  const addMailingAddress = (event: React.MouseEvent<HTMLButtonElement>) => {
    setOpen({
      anchorEl: event.currentTarget,
      content: <MailingAddressPopover onSubmit={updateMailingAddress} />,
      width: "440px",
    });
  };

  const editMailingAddress = (
    event: React.MouseEvent<HTMLAnchorElement>,
    mailingAddress: string
  ) => {
    setOpen({
      anchorEl: event.currentTarget,
      content: (
        <MailingAddressPopover
          onSubmit={updateMailingAddress}
          mailingAddress={mailingAddress}
        />
      ),
      width: "440px",
    });
  };

  const editPreparedBy = (
    event: React.MouseEvent<HTMLAnchorElement>,
    primaryOfficer: StaffUser
  ) => {
    setOpen({
      anchorEl: event.currentTarget,
      content: (
        <PreparedByPopover
          onSubmit={updatePrimaryOfficer}
          currentPrimaryOfficer={primaryOfficer}
        />
      ),
      width: "440px",
    });
  };

  const getApprovedBy = () => {
    const isApproved = [
      IRProgressEnum.PRELIMINARY_APPROVED,
      IRProgressEnum.HOLDER_PRELIMINARY_REVIEW,
      IRProgressEnum.FINAL_APPROVED,
      IRProgressEnum.ISSUED,
    ].includes(inspectionReportsData?.ir_progress?.id as IRProgressEnum);
    if (isApproved) {
      const approvedBy = irApprovalsData?.[0]?.approved_by;
      const approvedByPosition = irApprovalsData?.[0]?.approved_by_position;
      return `${approvedBy?.name}, ${approvedByPosition?.name}`;
    }
    return "";
  };

  return (
    <Box
      sx={{
        border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        py: 2,
        px: 3,
        borderRadius: 1,
        mb: 1,
      }}
    >
      <Grid container spacing={1}>
        <GridLabelValuePair
          label="Project"
          value={caseFileData?.project?.name}
        />
        <GridLabelValuePair
          label="Inspection No."
          value={inspectionData?.ir_number}
          gridProps={{ xs: 6 }}
        />
        <GridLabelValuePair
          label="IR Status"
          value={inspectionReportsData?.ir_status?.name}
          gridProps={{ xs: 6 }}
        />
        <GridLabelValuePair
          label="Regulated Party"
          value={caseFileData?.regulated_party}
          gridProps={{ xs: 6 }}
        />
        <GridLabelValuePair
          label="EA Certificate #"
          value={formatAuthorization(caseFileData?.authorization)}
          gridProps={{ xs: 6 }}
        />
        <Grid item xs={12}>
          <Typography
            variant="body2"
            color={BCDesignTokens.typographyColorPlaceholder}
          >
            Mailing Address
          </Typography>
          {mailingAddress ? (
            <Link
              sx={{
                display: "flex",
                gap: 0.75,
                cursor: !isReportsReadOnly ? "pointer" : "default",
                "&:hover": {
                  textDecoration: !isReportsReadOnly ? "underline" : "none",
                },
              }}
              underline="none"
              onClick={(e) =>
                !isReportsReadOnly && editMailingAddress(e, mailingAddress)
              }
            >
              {mailingAddress}
            </Link>
          ) : (
            !isReportsReadOnly && (
              <Button
                variant="text"
                color="secondary"
                disabled={isSaving}
                size="small"
                onClick={addMailingAddress}
                startIcon={<AddRounded />}
                sx={{
                  backgroundColor: "transparent",
                  px: 0,
                  height: "auto",
                  "& .MuiButton-startIcon": {
                    mr: 0,
                  },
                }}
              >
                Add Mailing Address
              </Button>
            )
          )}
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="body2"
            color={BCDesignTokens.typographyColorPlaceholder}
          >
            Record Prepared By
          </Typography>
          {recordPreparedBy && (
            <Link
              sx={{
                display: "flex",
                gap: 0.75,
                cursor: !isReportsReadOnly ? "pointer" : "default",
                "&:hover": {
                  textDecoration: !isReportsReadOnly ? "underline" : "none",
                },
              }}
              underline="none"
              onClick={(e) =>
                !isReportsReadOnly && editPreparedBy(e, recordPreparedBy)
              }
            >
              {renderStaffNameWithPosition(recordPreparedBy)}
            </Link>
          )}
        </Grid>
        <GridLabelValuePair
          label="Record Approved By"
          value={getApprovedBy()}
        />
      </Grid>
    </Box>
  );
};

export default ProjectOverview;
