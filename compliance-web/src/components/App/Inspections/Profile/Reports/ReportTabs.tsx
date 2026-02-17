import { Box, Tabs, Tab } from "@mui/material";
import { useEffect, useState, useMemo, useRef } from "react";
import ReportPanel from "./ReportPanel";
import { BCDesignTokens } from "epic.theme";
import Overview from "./ReportTabContents/IROverview/Overview";
import { useReportStore } from "./reportStore";
import { useParams } from "@tanstack/react-router";
import InspectionSummary from "./ReportTabContents/InspectionSummary";
import ActionsRequired from "./ReportTabContents/ActionsRequired";
import InspectionDates from "./ReportTabContents/InspectionDates";
import IREnforcementSummary from "./ReportTabContents/IREnforcementSummary";
import IRAppendices from "./ReportTabContents/IRAppendices";
import { useInspectionByNumber } from "@/hooks/useInspections";
import {
  useInspectionRequirementImages,
  useInspectionRequirementsData,
} from "@/hooks/useInspectionRequirements";
import {
  convertRequirementImagesArrToMap,
  REQUIREMENT_TYPE_ID,
} from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import IRRequirement from "./ReportTabContents/IRRequirement";
import IRRegulatoryConsideration from "./ReportTabContents/IRRegulatoryConsideration";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import ReportTopSection from "./ReportTopSection";
import { useRequirementStore } from "@/components/App/Inspections/Profile/Requirements/requirementStore";

export default function ReportTabs() {
  const { inspectionNumber } = useParams({ strict: false });
  const [value, setValue] = useState(0);
  const { setInspectionData, setCaseFileData, proponentLabel } =
    useReportStore();
  const {
    requirementsList,
    setRequirementsList,
    setRequirementPhotos,
    setRequirementFigures,
  } = useRequirementStore();
  const tabsContainerRef = useRef<HTMLDivElement>(null);

  const { data: inspectionData } = useInspectionByNumber(inspectionNumber);
  const { data: caseFileData } = useCaseFileByNumber(
    inspectionData?.case_file.case_file_number || ""
  );
  const { data: inspectionRequirementsData } = useInspectionRequirementsData(
    inspectionData?.id || 0
  );
  const { data: inspectionRequirementImages } = useInspectionRequirementImages(
    inspectionData?.id || 0
  );

  useEffect(() => {
    if (inspectionData && caseFileData) {
      setInspectionData(inspectionData);
      setCaseFileData(caseFileData);
      setRequirementsList(inspectionRequirementsData ?? []);
      setRequirementPhotos(
        convertRequirementImagesArrToMap(
          inspectionRequirementImages?.photos ?? []
        )
      );
      setRequirementFigures(
        convertRequirementImagesArrToMap(
          inspectionRequirementImages?.figures ?? []
        )
      );
    }
  }, [
    inspectionData,
    caseFileData,
    inspectionRequirementsData,
    inspectionRequirementImages,
    setInspectionData,
    setCaseFileData,
    setRequirementsList,
    setRequirementPhotos,
    setRequirementFigures,
  ]);

  const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const tabItems = useMemo(() => {
    // Base tabs that are always present
    const baseTabs = [
      { title: "IR Overview", component: <Overview /> },
      { title: "Inspection Summary", component: <InspectionSummary /> },
    ];

    // Dynamic requirement tabs based on inspectionRequirements
    const requirementTabs =
      requirementsList
        .filter((req) => req.req_type?.id === REQUIREMENT_TYPE_ID)
        ?.map((req: InspectionRequirement, index) => ({
          title: `#${index + 1}. ${req.summary}`,
          component: (
            <IRRequirement requirement={req} requirementIndex={index} />
          ),
        })) ?? [];

    // Remaining static tabs
    const remainingTabs = [
      {
        title: `Actions Required by ${proponentLabel} and Additional Comments`,
        component: <ActionsRequired />,
      },
      { title: "Enforcement Summary", component: <IREnforcementSummary /> },
      {
        title: "Regulatory Consideration",
        component: <IRRegulatoryConsideration />,
      },
      { title: "Inspection Version Dates", component: <InspectionDates /> },
      { title: "Appendices", component: <IRAppendices /> },
    ];

    return [...baseTabs, ...requirementTabs, ...remainingTabs];
  }, [requirementsList, proponentLabel]);

  useEffect(() => {
    const tabsContainer = tabsContainerRef.current;
    if (!tabsContainer) return;

    const calculateTabsPosition = () => {
      const rect = tabsContainer.getBoundingClientRect();
      document.documentElement.style.setProperty(
        "--ir-tabs-container-top-position",
        `${rect.top + 22}px`
      );
    };

    // Calculate on initial render and window resize
    calculateTabsPosition();

    // Detect layout changes
    const resizeObserver = new ResizeObserver(() => {
      calculateTabsPosition();
    });

    resizeObserver.observe(tabsContainer.parentElement || tabsContainer);

    window.addEventListener("resize", calculateTabsPosition);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener("resize", calculateTabsPosition);
    };
  }, [inspectionRequirementsData, value, tabItems]);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", pt: 2 }}>
      <ReportTopSection />
      <Box
        ref={tabsContainerRef}
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "row",
          width: "100%",
          gap: 2,
          height: "calc(100vh - var(--ir-tabs-container-top-position))",
          position: "relative",
        }}
      >
        <Tabs
          orientation="vertical"
          variant="scrollable"
          scrollButtons={false}
          value={value}
          onChange={handleChange}
          TabIndicatorProps={{
            sx: {
              backgroundColor: "transparent",
            },
          }}
          aria-label="preliminary ir tabs"
          sx={{
            width: "30%",
            height: "100%",
            "& .MuiTabs-flexContainer": {
              gap: 2,
            },
            "& .MuiTab-root": {
              borderRadius: 1,
              border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
              height: "40px",
              py: 0,
              minHeight: "unset",
            },
            "& .Mui-selected": {
              borderColor: BCDesignTokens.surfaceColorBorderActive,
              color: BCDesignTokens.themePrimaryBlue,
              backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
            },
          }}
        >
          {tabItems.map((item, index) => (
            <Tab
              key={`tab-${index}`}
              label={
                <Box
                  sx={{
                    width: "100%",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    display: "inline-block",
                    textAlign: "start",
                  }}
                >
                  {item.title}
                </Box>
              }
              id={`ir-tab-${index}`}
              aria-controls={`ir-tabpanel-${index}`}
              sx={{ width: "100%" }}
            />
          ))}
        </Tabs>
        {tabItems.map((item, index) => (
          <ReportPanel key={`panel-${index}`} value={value} index={index}>
            {item.component}
          </ReportPanel>
        ))}
      </Box>
    </Box>
  );
}
