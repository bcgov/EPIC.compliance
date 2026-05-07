import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import {
  Box,
  Button,
  MenuItem,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  Divider,
  Stack,
} from "@mui/material";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useFirstNationsData } from "@/hooks/useFirstNations";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import { useProjectsData } from "@/hooks/useProjects";
import { BCDesignTokens } from "epic.theme";
import { ReportType } from "@/models/ReportType";
import { downloadFile } from "@/utils/appUtils";
import { ReportFormValues } from "@/models/Report";
import { useSystemReportsExport } from "@/hooks/useSystemReports";
import dateUtils from "@/utils/dateUtils";

const REPORT_TYPES = [
  // {
  //   label: "Project Compliance History Report",
  //   value: ReportType.ProjectCompliance,
  // },
  { label: "CEB Summary Report", value: ReportType.CebSummary },
  // {
  //   label: "Case File Management Report",
  //   value: ReportType.CaseFileManagement,
  // },
  { label: "First Nation Report", value: ReportType.FirstNation },
];

export const Route = createFileRoute("/_authenticated/ce-database/reports/")({
  component: ReportsTab,
});

export function ReportsTab() {
  const [dateRangeType, setDateRangeType] = useState<"none" | "range">("none");

  const methods = useForm<ReportFormValues>({
    mode: "onChange",
    defaultValues: {
      report_type: ReportType.ProjectCompliance,
      project: null,
      start_date: null,
      end_date: null,
      officers: [],
      first_nation: null,
    },
  });
  const { handleSubmit, watch, setValue } = methods;
  const { data: projects = [] } = useProjectsData();
  const { data: staffUsers = [] } = useStaffUsersData();
  const { data: firstNations = [] } = useFirstNationsData();

  const report_type = watch("report_type");
  const officers = watch("officers");
  const project = watch("project");
  const first_nation = watch("first_nation");

  const hasManuallyChangedOfficers = useRef(false);

  useEffect(() => {
    if (report_type !== ReportType.CaseFileManagement) {
      hasManuallyChangedOfficers.current = false;
    }
    setValue("start_date", null);
    setValue("end_date", null);
    setValue("project", null);
    setValue("officers", []);
    setValue("first_nation", null);
    setDateRangeType("none");
  }, [report_type, setValue]);

  useEffect(() => {
    if (
      report_type === ReportType.CaseFileManagement &&
      officers?.length === 0
    ) {
      hasManuallyChangedOfficers.current = true;
    }
  }, [report_type, officers]);

  const { mutate: downloadSystemReport, isPending } = useSystemReportsExport(
    ({ data, filename }) => {
      downloadFile(
        data,
        filename ??
          `${report_type}-${dateUtils.formatDate(new Date().toISOString(), "YYYY-MM-DD-HH-mm-ss")}.xlsx`,
      );
    },
  );

  const isFormComplete = () => {
    switch (report_type) {
      case ReportType.ProjectCompliance:
        return project !== null;
      case ReportType.CaseFileManagement:
        return officers && officers.length > 0;
      case ReportType.FirstNation:
        return first_nation !== null;
      case ReportType.CebSummary:
        return true;
      default:
        return false;
    }
  };

  return (
    <Box maxWidth={700} mx="auto" pb={8}>
      <Stack spacing={1} mb={3}>
        <Typography variant="h5" color={BCDesignTokens.typographyColorPrimary}>
          Report Generation
        </Typography>
        <Typography
          variant="body2"
          color={BCDesignTokens.typographyColorPrimary}
        >
          Select the report type and configure parameters to generate and
          download your report.
        </Typography>
        <Typography variant="body2" color={BCDesignTokens.themeGray80}>
          Until final implementation is complete, the C&E Database is
          comprehensive only from January 2025 onwards. Please keep this in mind
          when analyzing results.
        </Typography>
      </Stack>
      <Box
        sx={{
          p: 4,
          borderRadius: "4px",
          border: "1px solid #D8D8D8",
          background: "#FFF",
        }}
      >
        <FormProvider {...methods}>
          <Box
            component="form"
            onSubmit={handleSubmit((data) => {
              downloadSystemReport(data);
            })}
            display="flex"
            flexDirection="column"
            gap={1}
          >
            <ControlledTextField
              name="report_type"
              label={<span style={{ fontWeight: 700 }}>Report Type</span>}
              select
              fullWidth
              sx={{ mb: 0 }}
            >
              {REPORT_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </ControlledTextField>
            {report_type === ReportType.ProjectCompliance && (
              <>
                <Typography variant="body2" color={BCDesignTokens.themeGray80}>
                  View all inspection, enforcement and compliant data for a
                  selected project.
                </Typography>
                <Box mt={2}>
                  <ControlledAutoComplete
                    name="project"
                    label="Project"
                    options={projects}
                    getOptionLabel={(option) => option.name}
                    isOptionEqualToValue={(option, value) =>
                      option.id === value.id
                    }
                    placeholder="Select a project"
                    fullWidth
                    isRequired
                  />
                </Box>
                <Box>
                  <RadioGroup
                    value={dateRangeType}
                    onChange={(e) => {
                      setDateRangeType(e.target.value as "none" | "range");
                      setValue("start_date", null);
                      setValue("end_date", null);
                    }}
                  >
                    <FormControlLabel
                      value="none"
                      control={<Radio />}
                      label="No Date Range"
                    />
                    <FormControlLabel
                      value="range"
                      control={<Radio />}
                      label="Select Date Range"
                    />
                  </RadioGroup>
                </Box>
                {dateRangeType === "range" && (
                  <Box display="flex" gap={2}>
                    <ControlledDateField
                      name="start_date"
                      label="Start Date"
                      width="100%"
                    />
                    <ControlledDateField
                      name="end_date"
                      label="End Date"
                      width="100%"
                    />
                  </Box>
                )}
              </>
            )}
            {report_type === ReportType.CebSummary && (
              <>
                <Typography variant="body2" color={BCDesignTokens.themeGray80}>
                  View CEB activities, including inspection, enforcement and
                  complaint summary data across projects.
                </Typography>
                <Box>
                  <RadioGroup
                    value={dateRangeType}
                    onChange={(e) => {
                      setDateRangeType(e.target.value as "none" | "range");
                      setValue("start_date", null);
                      setValue("end_date", null);
                    }}
                  >
                    <FormControlLabel
                      value="none"
                      control={<Radio />}
                      label="No Date Range"
                    />
                    <FormControlLabel
                      value="range"
                      control={<Radio />}
                      label="Select Date Range"
                    />
                  </RadioGroup>
                </Box>
                {dateRangeType === "range" && (
                  <Box display="flex" gap={2}>
                    <ControlledDateField
                      name="start_date"
                      label="Start Date"
                      width="100%"
                    />
                    <ControlledDateField
                      name="end_date"
                      label="End Date"
                      width="100%"
                    />
                  </Box>
                )}
              </>
            )}
            {report_type === ReportType.CaseFileManagement && (
              <>
                <Typography variant="body2" color={BCDesignTokens.themeGray80}>
                  View CEB case file management data and statistics.
                </Typography>
                <Box mt={2}>
                  <ControlledAutoComplete
                    name="officers"
                    label="Officer"
                    options={staffUsers}
                    getOptionLabel={(option) => option.name}
                    isOptionEqualToValue={(option, value) =>
                      option.id === value.id
                    }
                    placeholder="Select officers"
                    fullWidth
                    multiple={true}
                    isRequired={true}
                    showAllSelectedText={true}
                    showSelectAllOption
                    defaultAllSelected
                  />
                </Box>
              </>
            )}
            {report_type === ReportType.FirstNation && (
              <>
                <Typography variant="body2" color={BCDesignTokens.themeGray80}>
                  View attended inspections and received complaints for a
                  selected First Nation or First Nation Alliance across
                  projects.
                </Typography>
                <Box mt={2}>
                  <ControlledAutoComplete
                    name="first_nation"
                    label="First Nation/Alliance"
                    options={firstNations}
                    getOptionLabel={(option) => option.name}
                    isOptionEqualToValue={(option, value) =>
                      option.id === value.id
                    }
                    placeholder="Select First Nation or Alliance"
                    fullWidth
                    isRequired
                  />
                </Box>
              </>
            )}
            <Divider sx={{ my: 1 }} />
            <Box display="flex" justifyContent="flex-start">
              <Button
                type="submit"
                variant={isPending || !isFormComplete() ? "outlined" : "contained"}
                color="primary"
                disabled={isPending || !isFormComplete()}
              >
                <Typography
                  variant="body2"
                  color={isPending || !isFormComplete() 
                    ? BCDesignTokens.themeGray70 
                    : BCDesignTokens.themeGrayWhite
                  }
                >
                  Generate & Download Report
                </Typography>
              </Button>
            </Box>
            <Typography variant="body2" color={BCDesignTokens.themeGray80}>
              The report will be downloaded and formatted into an Excel file
              (.xlsx) with all relevant data.
            </Typography>
          </Box>
        </FormProvider>
      </Box>
    </Box>
  );
}

export default ReportsTab;
