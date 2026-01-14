// import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import { useForm, FormProvider, Controller } from "react-hook-form";
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
import { StaffUser } from "@/models/Staff";
import { ReportType } from "@/models/ReportType";

const REPORT_TYPES = [
  {
    label: "Project Compliance History Report",
    value: ReportType.ProjectCompliance,
  },
  { label: "CEB Summary Report", value: ReportType.CebSummary },
  {
    label: "Case File Management Report",
    value: ReportType.CaseFileManagement,
  },
  { label: "First Nation Report", value: ReportType.FirstNation },
];

// export const Route = createFileRoute("/_authenticated/ce-database/reports/")({
//   component: ReportsTab,
// });

interface ReportFormValues {
  reportType: ReportType;
  project: { id: number; name: string } | null;
  dateRangeType: "none" | "range";
  startDate: string | null;
  endDate: string | null;
  officers: StaffUser[];
  firstNation: { id: number; name: string } | null;
}

export function ReportsTab() {
  const methods = useForm<ReportFormValues>({
    defaultValues: {
      reportType: ReportType.ProjectCompliance,
      project: null,
      dateRangeType: "none",
      startDate: null,
      endDate: null,
      officers: [],
      firstNation: null,
    },
  });
  const { handleSubmit, watch, control, setValue } = methods;
  const { data: projects = [] } = useProjectsData();
  const { data: staffUsers = [] } = useStaffUsersData();
  const { data: firstNations = [] } = useFirstNationsData();

  const reportType = watch("reportType");
  const dateRangeType = watch("dateRangeType");
  const officers = watch("officers");

  const hasManuallyChangedOfficers = useRef(false);

  useEffect(() => {
    if (reportType !== ReportType.CaseFileManagement) {
      hasManuallyChangedOfficers.current = false;
    }
  }, [reportType]);

  useEffect(() => {
    if (
      reportType === ReportType.CaseFileManagement &&
      staffUsers.length > 0 &&
      officers.length === 0 &&
      !hasManuallyChangedOfficers.current
    ) {
      setValue("officers", staffUsers, {
        shouldValidate: true,
        shouldDirty: true,
      });
    }
  }, [reportType, staffUsers, officers, setValue]);

  useEffect(() => {
    if (reportType === ReportType.CaseFileManagement && officers.length === 0) {
      hasManuallyChangedOfficers.current = true;
    }
  }, [reportType, officers]);

  const onSubmit = (data: ReportFormValues) => {
    alert(`Generating report for ${data.reportType}`);
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
          borderRadius: '4px',
          border: '1px solid #D8D8D8',
          background: '#FFF',
        }}
      >
        <FormProvider {...methods}>
          <Box
            component="form"
            onSubmit={handleSubmit(onSubmit)}
            display="flex"
            flexDirection="column"
            gap={1}
          >
            <ControlledTextField
              name="reportType"
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
            {reportType === ReportType.ProjectCompliance && (
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
                  <Controller
                    name="dateRangeType"
                    control={control}
                    render={({ field }) => (
                      <RadioGroup {...field}>
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
                    )}
                  />
                </Box>
                {dateRangeType === "range" && (
                  <Box display="flex" gap={2}>
                    <ControlledDateField
                      name="startDate"
                      label="Start Date"
                      width="100%"
                    />
                    <ControlledDateField
                      name="endDate"
                      label="End Date"
                      width="100%"
                    />
                  </Box>
                )}
              </>
            )}
            {reportType === ReportType.CebSummary && (
              <>
                <Typography variant="body2" color={BCDesignTokens.themeGray80}>
                  View CEB activities, including inspection, enforcement and
                  complaint summary data across projects.
                </Typography>
                <Box>
                  <Controller
                    name="dateRangeType"
                    control={control}
                    render={({ field }) => (
                      <RadioGroup {...field}>
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
                    )}
                  />
                </Box>
                {dateRangeType === "range" && (
                  <Box display="flex" gap={2}>
                    <ControlledDateField
                      name="startDate"
                      label="Start Date"
                      width="100%"
                    />
                    <ControlledDateField
                      name="endDate"
                      label="End Date"
                      width="100%"
                    />
                  </Box>
                )}
              </>
            )}
            {reportType === ReportType.CaseFileManagement && (
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
                  />
                </Box>
              </>
            )}
            {reportType === ReportType.FirstNation && (
              <>
                <Typography variant="body2" color={BCDesignTokens.themeGray80}>
                  View attended inspections and received complaints for a
                  selected First Nation or First Nation Alliance across
                  projects.
                </Typography>
                <Box mt={2}>
                  <ControlledAutoComplete
                    name="firstNation"
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
              <Button type="submit" variant="contained" color="primary">
                <Typography variant="body2" color={BCDesignTokens.themeGrayWhite}>
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
