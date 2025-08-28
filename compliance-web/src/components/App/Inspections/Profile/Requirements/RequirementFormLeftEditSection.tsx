import { FC, useEffect, useMemo, useRef } from "react";
import { Alert, Stack, Typography } from "@mui/material";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import ControlledCheckbox from "@/components/Shared/Controlled/ControlledCheckbox";
import { useFormContext, useWatch } from "react-hook-form";
import ControlledToggleButtonGroup from "@/components/Shared/Controlled/ControlledToggleButtonGroup";
import { EnforcementActionEnum } from "@/utils/constants";
import {
  useComplianceFindingsData,
  useEnforcementActionsData,
} from "@/hooks/useInspectionRequirements";
import { useAgenciesData } from "@/hooks/useAgencies";
import { useTopicsData } from "@/hooks/useTopics";
import { Inspection } from "@/models/Inspection";

type RequirementFormLeftEditSectionProps = {
  isRegulatoryConsideration?: boolean;
  disableEnforcementAction?: boolean;
  inspectionData: Inspection;
};

const RequirementFormLeftEditSection: FC<
  RequirementFormLeftEditSectionProps
> = ({
  isRegulatoryConsideration = false,
  disableEnforcementAction = false,
  inspectionData,
}) => {
  const { control } = useFormContext();
  const summaryInputRef = useRef<HTMLInputElement>(null);

  const { data: enforcementActionsList } = useEnforcementActionsData();
  const { data: complianceFindingsList } = useComplianceFindingsData();
  const { data: topicsList } = useTopicsData();
  const { data: agenciesList } = useAgenciesData();

  const enforcementActions = useMemo(() => {
    // No need to show RESTORATIVE JUSTICE in the list of enforcement actions
    const filteredEnforcementActions =
      enforcementActionsList?.filter(
        (enforcementAction) =>
          enforcementAction.id !== EnforcementActionEnum.RESTORATIVE_JUSTICE
      );
    return inspectionData?.is_history
      ? filteredEnforcementActions
      : filteredEnforcementActions?.filter(
          (enforcementAction) =>
            enforcementAction.id !== EnforcementActionEnum.ADVISORY &&
            enforcementAction.id !== EnforcementActionEnum.WARNING
        );
  }, [enforcementActionsList, inspectionData]);

  const inputFocus = (inputRef: HTMLInputElement | null) => {
    if (inputRef) {
      inputRef.focus();
      const textLength = inputRef.value?.length || 0;
      inputRef.setSelectionRange(textLength, textLength);
    }
  };

  useEffect(() => {
    if (
      document.activeElement === null ||
      document.activeElement === document.body
    ) {
      inputFocus(summaryInputRef.current);
    }
  }, []);

  const isReferredToAnotherAgency = useWatch({
    control,
    name: "isReferredToAnotherAgency",
  });

  const enforcementAction = useWatch({
    control,
    name: "enforcementAction",
  });

  return (
    <>
      <ControlledTextField
        name="requirementSummary"
        label={isRegulatoryConsideration ? "Summary" : "Requirement Summary"}
        placeholder="e.g installing and maintaining erosion and sediment control measures"
        fullWidth
        inputRef={summaryInputRef}
        inputProps={{ "data-cy": "requirement-summary-input" }}
        multiline
        isRequired={true}
      />
      <ControlledAutoComplete
        name="topic"
        label="Topic"
        options={topicsList ?? []}
        getOptionLabel={(option) => option.name}
        getOptionKey={(option) => option.id}
        isOptionEqualToValue={(option, value) =>
          option.id.toString() === value.id.toString()
        }
        fullWidth
        isRequired={true}
      />
      {isRegulatoryConsideration && (
        <ControlledCheckbox
          name="isReferredToAnotherAgency"
          label="Mark if issue was referred to another Agency"
        />
      )}
      {!isRegulatoryConsideration && (
        <>
          <Stack direction="row" gap={2}>
            <ControlledAutoComplete
              name="complianceFinding"
              label="Compliance Finding"
              options={complianceFindingsList ?? []}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              isRequired={true}
              disabled={disableEnforcementAction}
            />
            <ControlledAutoComplete
              name="enforcementAction"
              label="Enforcement Action"
              options={enforcementActions ?? []}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) =>
                option.id.toString() === value.id.toString()
              }
              fullWidth
              sx={{ marginBottom: "-0.5rem" }}
              isRequired={true}
              disabled={disableEnforcementAction}
              renderOptionBadge={(option) => {
                // Define which enforcement action IDs are considered historical
                const historicalEnforcementActionIds = [
                  EnforcementActionEnum.ADVISORY,
                  EnforcementActionEnum.WARNING,
                ];

                if (
                  historicalEnforcementActionIds.includes(
                    option.id as EnforcementActionEnum
                  )
                ) {
                  return {
                    label: "Historical",
                    color: "warning",
                  };
                }
                return null;
              }}
            />
          </Stack>
          {enforcementAction?.id === EnforcementActionEnum.ORDER && (
            <Stack
              direction="row"
              gap={1}
              alignItems="baseline"
              justifyContent="flex-end"
            >
              <Typography variant="body2" sx={{ mb: 1 }}>
                Select if relevant:
              </Typography>
              <ControlledToggleButtonGroup
                name="enforcementActionExtra"
                size="small"
                disabled={disableEnforcementAction}
                options={[
                  {
                    id: EnforcementActionEnum.AP_RECOMMENDATION,
                    name: "AP Recommendation",
                  },
                  {
                    id: EnforcementActionEnum.CHARGE_RECOMMENDATION,
                    name: "Charge Recommendation",
                  },
                  {
                    id: EnforcementActionEnum.VIOLATION_TICKET,
                    name: "Violation Ticket",
                  },
                ]}
              />
            </Stack>
          )}
          {disableEnforcementAction && (
            <Alert
              severity="warning"
              sx={{ fontSize: "0.75rem", mb: 1, mt: -0.5 }}
            >
              An enforcement document has already been inprogress or issued. The
              Enforcement Action can no longer be changed.
            </Alert>
          )}
        </>
      )}
      {(isReferredToAnotherAgency ||
        enforcementAction?.id ===
          EnforcementActionEnum.REFER_TO_ANOTHER_AGENCY) && (
        <ControlledAutoComplete
          name="agency"
          label="Agency"
          options={agenciesList ?? []}
          getOptionLabel={(option) => option.name}
          getOptionKey={(option) => option.id}
          isOptionEqualToValue={(option, value) =>
            option.id.toString() === value.id.toString()
          }
          fullWidth
        />
      )}
    </>
  );
};

export default RequirementFormLeftEditSection;
