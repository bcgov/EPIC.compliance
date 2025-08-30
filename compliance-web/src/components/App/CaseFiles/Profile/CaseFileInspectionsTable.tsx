import { useInspectionOrderByNumber } from "@/hooks/useInspectionOrders";
import {
  useInspectionsData,
  useInspectionsMoreDetailsByCaseFileId,
} from "@/hooks/useInspections";
import { CaseFile } from "@/models/CaseFile";
import {
  Inspection,
  InspectionMoreDetailsEnforcementAction,
} from "@/models/Inspection";
import { InspectionOrder } from "@/models/InspectionOrder";
import {
  DRAWER_WIDTHS,
  EnforcementActionEnum,
  INITIATION,
  OrderProgressEnum,
  WarningLetterProgressEnum,
} from "@/utils/constants";
import { ChevronRight, ExpandLessRounded } from "@mui/icons-material";
import {
  Link,
  Chip,
  Accordion,
  AccordionSummary,
  Box,
  Typography,
  AccordionDetails,
  Grid,
  Tooltip,
} from "@mui/material";
import { Link as RouterLink } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { Fragment, useMemo, useState } from "react";
import OrderDrawer from "@/components/App/Inspections/Profile/Enforcements/Orders/OrderDrawer";
import { useDrawer } from "@/store/drawerStore";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useFetchWarningLetterByNumber } from "@/hooks/useInspectionWarningLetters";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import WarningLetterDrawer from "@/components/App/Inspections/Profile/Enforcements/WarningLetters/WarningLetterDrawer";
import EnforcementStatusFlag from "@/components/App/Inspections/Profile/Enforcements/EnforcementStatusFlag";

const styleOverFlowClipped = {
  whiteSpace: "nowrap",
  textOverflow: "ellipsis",
  overflow: "hidden",
};

const CaseFileInspectionsTable = ({ caseFile }: { caseFile: CaseFile }) => {
  const { setOpen, setClose } = useDrawer();
  const { data: detailedInspections } = useInspectionsMoreDetailsByCaseFileId(
    caseFile.id
  );
  const { data: inspectionsListData } = useInspectionsData();
  const inspectionsList = useMemo(() => {
    return inspectionsListData?.items;
  }, [inspectionsListData]);
  const { data: staffUsersList } = useStaffUsersData();

  const [expandedInspections, setExpandedInspections] = useState<Set<number>>(
    new Set()
  );

  const handleAccordionChange = (inspectionId: number, expanded: boolean) => {
    setExpandedInspections((prev) => {
      const newSet = new Set(prev);
      if (expanded) {
        newSet.add(inspectionId);
      } else {
        newSet.delete(inspectionId);
      }
      return newSet;
    });
  };

  const isEnforcementActionLink = (
    enforcementAction: InspectionMoreDetailsEnforcementAction | undefined
  ): boolean => {
    if (!enforcementAction?.number) return false;

    const progressId = enforcementAction.progress?.id;

    switch (enforcementAction.id) {
      case EnforcementActionEnum.ORDER:
        return progressId === OrderProgressEnum.ISSUED;
      case EnforcementActionEnum.WARNING_LETTER:
        return progressId === WarningLetterProgressEnum.ISSUED;
      default:
        return false;
    }
  };

  const onOrderSuccess = (order: InspectionOrder) => {
    const inspection = inspectionsList?.find(
      (inspection) => inspection.id === order.inspection_id
    );
    setOpen({
      content: (
        <OrderDrawer
          onSubmit={() => {
            setClose();
          }}
          inspection={inspection as Inspection}
          enforcementOrder={order}
          staffUsersList={staffUsersList || []}
          isReadonlyMode={true}
        />
      ),
      width: DRAWER_WIDTHS.ENFORCEMENT_DRAWER,
    });
  };

  const { mutate: fetchInspectionOrder } =
    useInspectionOrderByNumber(onOrderSuccess);

  const onWarningLetterSuccess = (warningLetter: InspectionWarningLetter) => {
    const inspection = detailedInspections?.find(
      (inspection) => inspection.id === warningLetter.inspection_id
    );
    setOpen({
      content: (
        <WarningLetterDrawer
          onSubmit={() => {
            setClose();
          }}
          inspection={inspection as Inspection}
          warningLetter={warningLetter}
          staffUsersList={staffUsersList || []}
          isReadonlyMode={true}
        />
      ),
      width: DRAWER_WIDTHS.ENFORCEMENT_DRAWER,
    });
  };

  const { mutate: fetchWarningLetter } = useFetchWarningLetterByNumber(
    onWarningLetterSuccess
  );

  const handleEnforcementActionClick = async (
    enforcementAction: InspectionMoreDetailsEnforcementAction | undefined
  ) => {
    if (!enforcementAction?.number) return;
    if (enforcementAction.id === EnforcementActionEnum.ORDER) {
      fetchInspectionOrder(enforcementAction.number);
    } else if (enforcementAction.id === EnforcementActionEnum.WARNING_LETTER) {
      fetchWarningLetter(enforcementAction.number);
    }
  };

  return (
    (caseFile.initiation.id === INITIATION.INSPECTION_ID ||
      (detailedInspections && detailedInspections?.length > 0)) && (
      <>
        <Typography variant="h6" mt={2} mb={1}>
          Inspections
        </Typography>
        {detailedInspections && detailedInspections.length > 0 ? (
          detailedInspections.map((inspection, index) => {
            const isExpanded = expandedInspections.has(inspection.id);

            return (
              <Accordion
                key={inspection.id}
                expanded={isExpanded}
                onChange={(_, expanded) => {
                  handleAccordionChange(inspection.id, expanded);
                }}
                sx={{
                  marginY: "0.5rem",
                  border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
                  borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
                  "&.Mui-expanded": {
                    marginY: "0.5rem",
                  },
                  "&:before": {
                    display: "none",
                  },
                }}
              >
                <AccordionSummary
                  aria-controls={`panel${index}-content`}
                  id={`inspection-panel${index}-header`}
                  sx={{
                    backgroundColor:
                      BCDesignTokens.surfaceColorBackgroundLightGray,
                    borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
                    "&.Mui-expanded": {
                      minHeight: "48px",
                      padding: "0.875rem 1rem",
                      borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
                      "& .MuiAccordionSummary-content": {
                        margin: "0",
                      },
                    },
                    "& .MuiAccordionSummary-content": {
                      display: "flex",
                      justifyContent: "space-between",
                      gap: "1rem",
                    },
                  }}
                >
                  <Box display={"flex"} alignItems={"center"} gap={0.5}>
                    {isExpanded ? <ExpandLessRounded /> : <ChevronRight />}
                    <Link
                      component={RouterLink}
                      to="/ce-database/inspections/$inspectionNumber"
                      params={{
                        inspectionNumber: inspection.ir_number,
                      }}
                      underline="hover"
                    >
                      {inspection.ir_number}
                    </Link>
                    <Chip
                      label={inspection.inspection_status}
                      data-testid="status-chip"
                      color={
                        inspection.inspection_status?.toLowerCase() === "open"
                          ? "success"
                          : "error"
                      }
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                  <Box display={"flex"} alignItems={"center"} gap={0.5}>
                    <Typography
                      variant="body2"
                      color={BCDesignTokens.typographyColorPlaceholder}
                      mr={0.25}
                    >
                      Primary:
                    </Typography>
                    <Typography variant="body2">
                      {inspection.primary_officer?.name || "N/A"}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ padding: "1rem" }}>
                  <Grid container spacing={1}>
                    <Grid item xs={4}>
                      <Typography
                        variant="body2"
                        color={BCDesignTokens.typographyColorPlaceholder}
                      >
                        Requirement Summary
                      </Typography>
                    </Grid>
                    <Grid item xs={2}>
                      <Typography
                        variant="body2"
                        color={BCDesignTokens.typographyColorPlaceholder}
                      >
                        #
                      </Typography>
                    </Grid>
                    <Grid item xs={2}>
                      <Typography
                        variant="body2"
                        color={BCDesignTokens.typographyColorPlaceholder}
                      >
                        Source
                      </Typography>
                    </Grid>
                    <Grid item xs={2}>
                      <Typography
                        variant="body2"
                        sx={{
                          ...styleOverFlowClipped,
                          color: BCDesignTokens.typographyColorPlaceholder,
                        }}
                      >
                        Enforcement Action
                      </Typography>
                    </Grid>
                    <Grid item xs={2}>
                      <Typography
                        variant="body2"
                        color={BCDesignTokens.typographyColorPlaceholder}
                      >
                        Enf. Status
                      </Typography>
                    </Grid>
                    {inspection.requirement_details?.map(
                      (requirement, index) => (
                        <Fragment key={index}>
                          <Grid item xs={4}>
                            <Tooltip title={requirement.requirement_summary}>
                              <Typography
                                variant="body2"
                                sx={{ ...styleOverFlowClipped }}
                              >
                                #{requirement.requirement_sort_order}.{" "}
                                {requirement.requirement_summary}
                              </Typography>
                            </Tooltip>
                          </Grid>
                          <Grid item xs={2} sx={{ ...styleOverFlowClipped }}>
                            {requirement.requirement_source_name?.toLowerCase() ===
                            "order" ? (
                              <Tooltip title={requirement.requirement_number}>
                                <Link
                                  underline="hover"
                                  sx={{ cursor: "pointer" }}
                                  onClick={() =>
                                    fetchInspectionOrder(
                                      requirement.requirement_number
                                    )
                                  }
                                >
                                  {(requirement.requirement_number ?? "")
                                    .split("_")
                                    .slice(1)
                                    .join("_")}
                                </Link>
                              </Tooltip>
                            ) : (
                              <Typography variant="body2">
                                {requirement.requirement_number}
                              </Typography>
                            )}
                          </Grid>
                          <Grid item xs={2}>
                            <Typography
                              variant="body2"
                              sx={{ ...styleOverFlowClipped }}
                            >
                              {requirement.requirement_source_name}
                            </Typography>
                          </Grid>
                          <Grid item xs={2} sx={{ ...styleOverFlowClipped }}>
                            {isEnforcementActionLink(
                              requirement.enforcement_action
                            ) ? (
                              <Link
                                underline="hover"
                                sx={{ cursor: "pointer" }}
                                onClick={() =>
                                  handleEnforcementActionClick(
                                    requirement.enforcement_action
                                  )
                                }
                              >
                                {requirement.enforcement_action?.name}
                              </Link>
                            ) : (
                              <Typography
                                variant="body2"
                                sx={{ ...styleOverFlowClipped }}
                              >
                                {requirement.enforcement_action?.name}
                              </Typography>
                            )}
                          </Grid>
                          <Grid item xs={2}>
                            {requirement.enforcement_action && (
                              <EnforcementStatusFlag
                                enforcementActionType={
                                  requirement.enforcement_action
                                    .id as EnforcementActionEnum
                                }
                                enforcementActionDetails={
                                  requirement.enforcement_action
                                }
                              />
                            )}
                          </Grid>
                        </Fragment>
                      )
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })
        ) : (
          <Typography
            variant="body2"
            color={BCDesignTokens.typographyColorPlaceholder}
          >
            You do not have any created inspections on this file.
          </Typography>
        )}
      </>
    )
  );
};

export default CaseFileInspectionsTable;
