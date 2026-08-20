import { FC, useEffect, useState, useRef, useCallback } from "react";
import { Box, Grid, IconButton } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { EnforcementAction } from "@/models/EnforcementAction";
import { useFormContext, useWatch } from "react-hook-form";
import {
  ComplianceFindingEnum,
  formatImagesToMentionList,
} from "./RequirementUtils";
import { EditOutlined } from "@mui/icons-material";
import GridLabelValuePair from "@/components/Shared/GridLabelValuePair";
import ControlledLexicalEditor from "@/components/Shared/Controlled/ControlledLexicalEditor";
import { useRequirementStore } from "./requirementStore";
import { MentionData } from "@/components/Shared/LexicalEditor/LexicalUtils";
import {
  EnforcementActionEnum,
  OrderProgressEnum,
  WarningLetterProgressEnum,
  ViolationTicketStatus,
  AdministrativePenaltyStatus,
  ChargeRecommendationStatus,
} from "@/utils/constants";
import { useInspectionOrdersData } from "@/hooks/useInspectionOrders";
import { useInspectionWarningLettersData } from "@/hooks/useInspectionWarningLetters";
import { useAdministrativePenaltiesData } from "@/hooks/useAdministrativePenalties";
import { useViolationTicketsData } from "@/hooks/useViolationTickets";
import { useChargeRecommendationsData } from "@/hooks/useChargeRecommendations";
import { useModal } from "@/store/modalStore";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import RequirementFormLeftEditSection from "./RequirementFormLeftEditSection";
import { Inspection } from "@/models/Inspection";
import { useEnforcementActionsData } from "@/hooks/useInspectionRequirements";
import useIsDrawerConstrained from "@/hooks/useIsDrawerConstrained";
import { DRAWER_WIDTHS } from "@/utils/constants";

type RequirementFormLeftProps = {
  appHeaderHeight: number;
  isEditMode?: boolean;
  isRegulatoryConsideration?: boolean;
  requirementId: number;
  inspectionData: Inspection;
  currentEnforcementAction?: EnforcementAction;
  isRequirementEditable?: boolean;
};

const RequirementFormLeft: FC<RequirementFormLeftProps> = ({
  appHeaderHeight,
  isEditMode,
  isRegulatoryConsideration,
  requirementId,
  inspectionData,
  currentEnforcementAction,
  isRequirementEditable = true,
}) => {
  const { setOpen, setClose } = useModal();
  const { control, setValue, getValues } = useFormContext();
  const { requirementPhotos, requirementFigures } = useRequirementStore();
  const [mentionDataList, setMentionDataList] = useState<MentionData[]>([]);
  const [orderExists, setOrderExists] = useState<boolean>(false);
  const [warningLetterExists, setWarningLetterExists] =
    useState<boolean>(false);
  const [administrativePenaltyExists, setAdministrativePenaltyExists] =
    useState<boolean>(false);
  const [violationTicketExists, setViolationTicketExists] =
    useState<boolean>(false);
  const [chargeRecommendationExists, setChargeRecommendationExists] =
    useState<boolean>(false);
  const [disableEnforcementAction, setDisableEnforcementAction] =
    useState<boolean>(false);
  const [disableSecondaryEnfAction, setDisableSecondaryEnfAction] =
    useState<boolean>(false);
  const summaryInputRef = useRef<HTMLInputElement>(null);
  const [isReadOnly, setIsReadOnly] = useState(isEditMode);

  const { data: enforcementActionsList } = useEnforcementActionsData();
  const { data: inspectionOrdersData } = useInspectionOrdersData(
    inspectionData.id,
    {
      isStaleInfinate: false,
    }
  );
  const { data: inspectionWarningLettersData } =
    useInspectionWarningLettersData(inspectionData.id, {
      isStaleInfinate: false,
    });
  const { data: administrativePenaltiesData } = useAdministrativePenaltiesData(
    inspectionData.id,
    {
      isStaleInfinate: false,
    }
  );
  const { data: violationTicketsData } = useViolationTicketsData(
    inspectionData.id
  );
  const { data: chargeRecommendationsData } = useChargeRecommendationsData(
    inspectionData.id,
    {
      isStaleInfinate: false,
    }
  );

  const isDrawerConstrained = useIsDrawerConstrained(DRAWER_WIDTHS.REQUIREMENT_DRAWER);

  const inputFocus = useCallback((inputRef: HTMLInputElement | null) => {
    if (inputRef) {
      inputRef.focus();
      const textLength = inputRef.value?.length || 0;
      inputRef.setSelectionRange(textLength, textLength);
    }
  }, []);

  useEffect(() => {
    if (!isReadOnly && summaryInputRef.current !== document.activeElement) {
      setTimeout(() => {
        inputFocus(summaryInputRef.current);
      }, 0);
    }
  }, [isReadOnly, inputFocus]);

  const updateMentionList = useCallback(() => {
    const reqId = !requirementId ? NaN : requirementId;
    const mentionList = formatImagesToMentionList([
      ...(requirementPhotos.get(reqId) ?? []),
      ...(requirementFigures.get(reqId) ?? []),
    ]);
    setMentionDataList(mentionList);
  }, [requirementPhotos, requirementFigures, requirementId]);

  useEffect(() => {
    updateMentionList();
  }, [updateMentionList]);

  const enforcementAction = useWatch({
    control,
    name: "enforcementAction",
  });

  const complianceFinding = useWatch({
    control,
    name: "complianceFinding",
  });

  useEffect(() => {
    if (
      complianceFinding?.id === ComplianceFindingEnum.IN &&
      !getValues("enforcementAction")?.id
    ) {
      const notApplicableAction = enforcementActionsList?.find(
        (action) => action.id === EnforcementActionEnum.NOT_APPLICABLE
      );
      setValue("enforcementAction", notApplicableAction);
    }
  }, [complianceFinding, enforcementActionsList, setValue, getValues]);

  useEffect(() => {
    // Check if requirement exists in inspection orders
    const requirementsInOrders =
      inspectionOrdersData?.filter((order) =>
        order.order_requirement_maps?.some(
          (map) => map.inspection_requirement_id === requirementId
        )
      ) ?? [];
    setOrderExists(requirementsInOrders.length > 0);

    // Check if requirement exists in warning letters
    const requirementsInWarningLetters =
      inspectionWarningLettersData?.filter((letter) =>
        letter.warning_letter_requirement_maps?.some(
          (map) => map.inspection_requirement_id === requirementId
        )
      ) ?? [];
    setWarningLetterExists(requirementsInWarningLetters.length > 0);

    // Check if requirement exists in administrative penalties
    const requirementsInAdministrativePenalties =
      administrativePenaltiesData?.filter((penalty) =>
        penalty.administrative_penalty_requirement_maps?.some(
          (map) => map.inspection_requirement_id === requirementId
        )
      ) ?? [];
    setAdministrativePenaltyExists(requirementsInAdministrativePenalties.length > 0);

    // Check if requirement exists in violation tickets
    const requirementsInViolationTickets =
      violationTicketsData?.filter((ticket) =>
        ticket.violation_ticket_requirement_maps?.some(
          (map) => map.inspection_requirement_id === requirementId
        )
      ) ?? [];
    setViolationTicketExists(requirementsInViolationTickets.length > 0);

    // Check if requirement exists in charge recommendations
    const requirementsInChargeRecommendations =
      chargeRecommendationsData?.filter((recommendation) =>
        recommendation.charge_recommendation_requirement_maps?.some(
          (map) => map.inspection_requirement_id === requirementId
        )
      ) ?? [];
    setChargeRecommendationExists(requirementsInChargeRecommendations.length > 0);

    if (
      requirementsInOrders.length > 0 ||
      requirementsInWarningLetters.length > 0 ||
      requirementsInAdministrativePenalties.length > 0 ||
      requirementsInViolationTickets.length > 0 ||
      requirementsInChargeRecommendations.length > 0
    ) {
      const nonDraftOrders = requirementsInOrders.some(
        (order) => order.order_progress?.id !== OrderProgressEnum.DRAFTING
      );
      const nonDraftWarningLetters = requirementsInWarningLetters.some(
        (letter) => letter.progress?.id !== WarningLetterProgressEnum.DRAFTING
      );
      const nonIssuedViolationTickets = requirementsInViolationTickets.some(
        (ticket) => ticket.status?.id !== ViolationTicketStatus.ISSUED
      );
      const nonDraftAdministrativePenalties = requirementsInAdministrativePenalties.some(
        (penalty) =>
          penalty.referral_status?.id !== AdministrativePenaltyStatus.PREPARING_REFERRAL_FOR_AEO &&
          // Referred to AEO is treated the same as Preparing Referral for AEO for workflow purposes
          penalty.referral_status?.id !== AdministrativePenaltyStatus.REFERRED_TO_AEO
      );
      const nonDraftChargeRecommendations = requirementsInChargeRecommendations.some(
        (charge) => charge.status?.id !== ChargeRecommendationStatus.DRAFTING
      );
      setDisableEnforcementAction(
        nonDraftOrders || 
        nonDraftWarningLetters || 
        nonIssuedViolationTickets || 
        nonDraftAdministrativePenalties || 
        nonDraftChargeRecommendations
      );
      setDisableSecondaryEnfAction(
        requirementsInAdministrativePenalties.length > 0 ||
        requirementsInViolationTickets.length > 0 ||
        requirementsInChargeRecommendations.length > 0
      );
    } else {
      setDisableEnforcementAction(false);
      setDisableSecondaryEnfAction(false);
    }
  }, [
    inspectionOrdersData, 
    inspectionWarningLettersData, 
    administrativePenaltiesData,
    violationTicketsData,
    chargeRecommendationsData,
    requirementId
  ]);

  useEffect(() => {
    // Only show confirmation modal when in edit mode and not readonly
    if (currentEnforcementAction && !isReadOnly) {
      const hasEnforcementActionChanged =
        currentEnforcementAction?.id !== enforcementAction?.id;

      if (
        [
          EnforcementActionEnum.ORDER,
          EnforcementActionEnum.WARNING_LETTER,
          EnforcementActionEnum.AP_RECOMMENDATION,
          EnforcementActionEnum.VIOLATION_TICKET,
          EnforcementActionEnum.CHARGE_RECOMMENDATION,
        ].includes(currentEnforcementAction?.id as EnforcementActionEnum) &&
        hasEnforcementActionChanged &&
        (orderExists || warningLetterExists || administrativePenaltyExists || violationTicketExists || chargeRecommendationExists)
      ) {
          const getDescription = () => {
    if (currentEnforcementAction?.id === EnforcementActionEnum.AP_RECOMMENDATION) {
      return `A document already exists for the previous enforcement action (Referral to Administrative Penalty). 

Changing it will delete the existing document so you can create a new one`;
    } else {
      return `A document already exists for the previous enforcement action(${currentEnforcementAction?.name}). 
      Changing it will delete the existing document so you can create a new one`;
    }
  };

        setOpen({
          content: (
            <ConfirmationModal
              title="Change Enforcement Action?"
              description={getDescription()}
              confirmButtonText="Proceed"
              onConfirm={() => {
                setClose();
              }}
              onCancel={() => {
                setClose();
                setValue("enforcementAction", currentEnforcementAction);
              }}
            />
          ),
        });
      }
    }
  }, [
    currentEnforcementAction,
    enforcementAction,
    orderExists,
    warningLetterExists,
    administrativePenaltyExists,
    violationTicketExists,
    chargeRecommendationExists,
    setClose,
    setOpen,
    setValue,
    isReadOnly,
  ]);

  const ReadOnlySection = () => {
    const { getValues } = useFormContext();
    const agencyName = getValues("agency")?.name;
    return (
      <Box
        sx={{
          borderRadius: "4px",
          border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
          background: BCDesignTokens.surfaceColorBackgroundWhite,
          display: "flex",
          padding: "1rem",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: "0.5rem",
          alignSelf: "stretch",
          mb: "1.5rem",
        }}
      >
        {isRequirementEditable && (
          <IconButton
            aria-label="edit"
            onClick={() => setIsReadOnly(false)}
            size="small"
            sx={{ marginBottom: "-1rem", marginTop: "-0.5rem" }}
            data-cy="editable-requirement-button"
          >
            <EditOutlined sx={{ fontSize: "1.25rem" }} />
          </IconButton>
        )}
        <Grid container spacing={1}>
          <GridLabelValuePair
            label="Requirement Summary"
            value={getValues("requirementSummary")}
            multiline
          />
          <GridLabelValuePair label="Topic" value={getValues("topic")?.name} />
          {!isRegulatoryConsideration && (
            <>
              <GridLabelValuePair
                label="Compliance Finding"
                value={getValues("complianceFinding")?.name}
                gridProps={{ xs: 4 }}
              />
              <GridLabelValuePair
                label="Enforcement Action"
                value={[
                  getValues("enforcementAction")?.name,
                  getValues("enforcementActionExtra")?.name,
                ]
                  .filter(Boolean)
                  .join(", ")}
                gridProps={{ xs: agencyName ? 4 : 8 }}
              />
            </>
          )}
          {agencyName && (
            <GridLabelValuePair
              label="Agency"
              value={agencyName}
              gridProps={{ xs: 4 }}
            />
          )}
        </Grid>
      </Box>
    );
  };

  return (
    <Box
      sx={{
        background: BCDesignTokens.surfaceColorBackgroundLightGray,
        padding: "0.5rem 1rem 1rem 1.5rem",
        width: isDrawerConstrained ? "auto" : "730px",
        overflow: isDrawerConstrained ? "unset" : "auto",
        boxSizing: "border-box",
        paddingRight: isDrawerConstrained ? 4 : "1.5rem",
      }}
    >
      {isReadOnly ? (
        <ReadOnlySection />
      ) : (
        <RequirementFormLeftEditSection
          inspectionData={inspectionData}
          isRegulatoryConsideration={isRegulatoryConsideration}
          disableEnforcementAction={disableEnforcementAction}
          disableSecondaryEnfAction={disableSecondaryEnfAction}
        />
      )}
      <ControlledLexicalEditor
        label="Inspection Details"
        name="findings"
        placeholder="Enter Inspection Details..."
        height={ isDrawerConstrained ? "auto" : `calc(100vh - ${appHeaderHeight + 363}px)`}
        isAdvanced
        mentionsList={mentionDataList}
        disabled={!isRequirementEditable}
      />
    </Box>
  );
};

export default RequirementFormLeft;
