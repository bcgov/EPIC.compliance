import { useUpdateInspectionRequirementOrder } from "@/hooks/useInspectionRequirements";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { InspectionRequirementSource } from "@/models/InspectionRequirementSource";
import { notify } from "@/store/snackbarStore";
import { DragIndicatorRounded } from "@mui/icons-material";
import { Box, Grid, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { Reorder } from "framer-motion";
import React, { memo, useCallback, useState } from "react";
import {
  REGULATORY_CONSIDERATION_TYPE_ID,
  requirementCardStyles,
  requirementSourceNumberType,
} from "./RequirementUtils";
import GridLabelValuePair from "@/components/Shared/GridLabelValuePair";

interface RequirementCardProps {
  requirement: InspectionRequirement;
  index: number;
  onEdit: () => void;
  isActive: boolean;
  disabled?: boolean;
  dragDisabled?: boolean;
}

const RequirementCard: React.FC<RequirementCardProps> = memo(
  ({ requirement, index, onEdit, isActive, disabled, dragDisabled }) => {
    const [isDragging, setIsDragging] = useState(false);

    const isRegulatoryConsideration =
      requirement.req_type?.id === REGULATORY_CONSIDERATION_TYPE_ID;

    const sourceNumberType = requirementSourceNumberType(
      requirement.requirement_source_details?.[0]?.requirement_source_id.toString()
    );

    const onSuccess = useCallback(() => {
      notify.success("Requirement sort order updated");
    }, []);

    const { mutate: updateInspectionRequirementOrder } =
      useUpdateInspectionRequirementOrder(onSuccess);

    const handleDragEnd = useCallback(() => {
      if (disabled || dragDisabled) return;
      updateInspectionRequirementOrder({
        inspectionId: requirement.inspection_id,
        requirementId: requirement.id,
        sortOrder: index + 1,
      });
      setTimeout(() => setIsDragging(false), 100);
    }, [
      requirement.inspection_id,
      requirement.id,
      index,
      updateInspectionRequirementOrder,
      disabled,
      dragDisabled,
    ]);

    const handleClick = useCallback(() => {
      if (disabled || isDragging) return;
      onEdit();
    }, [isDragging, onEdit, disabled]);

    const renderRegulatoryContent = useCallback(
      () => (
        <>
          <GridLabelValuePair label="Summary" value={requirement.summary} />
          <GridLabelValuePair
            label="Topic"
            value={requirement.topic?.name ?? ""}
            gridProps={{ xs: 4 }}
          />
          <GridLabelValuePair
            label="Agency"
            value={requirement.agency?.name ?? ""}
            gridProps={{ xs: 8 }}
          />
        </>
      ),
      [requirement]
    );

    const renderRequirementContent = useCallback(
      () => (
        <>
          <GridLabelValuePair label="Topic" value={requirement.topic?.name ?? ""} />
          <GridLabelValuePair
            label="Source"
            value={
              requirement.requirement_source_details?.[0]?.requirement_source
                ?.name
            }
            gridProps={{ xs: 4 }}
          />
          <GridLabelValuePair
            label={`${sourceNumberType} #`}
            value={
              String(
                requirement.requirement_source_details?.[0]?.[
                  `${sourceNumberType.toLowerCase()}_number` as keyof InspectionRequirementSource
                ] ?? ""
              )
            }
            gridProps={{ xs: 8 }}
          />
          <GridLabelValuePair
            label="Compliance Finding"
            value={requirement.compliance_finding?.name}
            gridProps={{ xs: 4 }}
          />
          <GridLabelValuePair
            label="Enforcement Action"
            value={requirement.enforcement_action_data
              .map((action) => action.name)
              .join(", ")}
            gridProps={{ xs: 8 }}
          />
        </>
      ),
      [sourceNumberType, requirement]
    );

    const renderCardContent = useCallback(() => {
      return (
        <Box
          sx={{
            ...requirementCardStyles.card,
            ...(isActive && {
              borderColor: BCDesignTokens.surfaceColorBorderActive,
            }),
            ...(disabled && {
              cursor: "not-allowed",
              opacity: 0.7,
              "&:hover": {
                boxShadow: "none",
              },
            }),
            // When drag is disabled but card should still be clickable, maintain pointer cursor
            ...(dragDisabled &&
              !disabled && {
                cursor: "pointer",
              }),
          }}
          onClick={handleClick}
        >
          <Box sx={requirementCardStyles.header}>
            <DragIndicatorRounded
              sx={{
                mx: 0.5,
                mb: 0.25,
                fontSize: "1.125rem",
                visibility:
                  isRegulatoryConsideration || disabled || dragDisabled
                    ? "hidden"
                    : "visible",
              }}
              color="action"
              data-testid="drag-indicator"
            />
            <Typography variant="body1" data-cy="requirement-card-title">
              {isRegulatoryConsideration
                ? "Regulatory Consideration"
                : `#${index + 1}. ${requirement.summary}`}
            </Typography>
          </Box>
          <Box sx={requirementCardStyles.content}>
            <Grid container spacing={0.5}>
              {isRegulatoryConsideration
                ? renderRegulatoryContent()
                : renderRequirementContent()}
            </Grid>
          </Box>
        </Box>
      );
    }, [
      handleClick,
      index,
      isActive,
      isRegulatoryConsideration,
      renderRegulatoryContent,
      renderRequirementContent,
      requirement,
      disabled,
      dragDisabled,
    ]);

    return isRegulatoryConsideration ? (
      renderCardContent()
    ) : (
      <Reorder.Item
        key={requirement.id}
        value={requirement}
        onDragStart={() => !disabled && !dragDisabled && setIsDragging(true)}
        onDragEnd={handleDragEnd}
        disabled={disabled || dragDisabled}
      >
        {renderCardContent()}
      </Reorder.Item>
    );
  }
);

export default RequirementCard;
