import { useInspectionRequirementsData } from "@/hooks/useInspectionRequirements";
import { Inspection } from "@/models/Inspection";
import { Box, Typography } from "@mui/material";
import React, { useEffect, useMemo } from "react";
import RequirementLoading from "@/components/App/Inspections/Profile/Requirements/RequirementLoading";
import MenuActionDropdown from "@/components/Shared/MenuActionDropdown";
import EnforcementNotificationCard from "@/components/App/Inspections/Profile/Enforcements/EnforcementNotificationCard";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import {
  DRAWER_WIDTHS,
  EnforcementActionEnum,
  MODAL_WIDTHS,
} from "@/utils/constants";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import EnforcementCard from "@/components/App/Inspections/Profile/Enforcements/EnforcementCard";
import { useInspectionOrdersData } from "@/hooks/useInspectionOrders";
import OrderDrawer from "@/components/App/Inspections/Profile/Enforcements/Orders/OrderDrawer";
import { InspectionOrder } from "@/models/InspectionOrder";
import { useDrawer } from "@/store/drawerStore";
import { useInspectionWarningLettersData } from "@/hooks/useInspectionWarningLetters";
import WarningLetterDrawer from "@/components/App/Inspections/Profile/Enforcements/WarningLetters/WarningLetterDrawer";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { ChargeRecommendation } from "@/models/ChargeRecommendation";
import { ViolationTicket } from "@/models/ViolationTicket";
import { RestorativeJustice } from "@/models/RestorativeJustice";
import { AddRounded } from "@mui/icons-material";
import { useQueryClient } from "@tanstack/react-query";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import OrderCreateModal from "@/components/App/Inspections/Profile/Enforcements/Orders/OrderCreateModal";
import WarningLetterCreateModal from "@/components/App/Inspections/Profile/Enforcements/WarningLetters/WarningLetterCreateModal";
import AdministrativePenaltyCreateModal from "@/components/App/Inspections/Profile/Enforcements/AdministrativePenalty/AdministrativePenaltyCreateModal";
import AdministrativePenaltyUpdateModal from "@/components/App/Inspections/Profile/Enforcements/AdministrativePenalty/AdministrativePenaltyUpdateModal";
import ChargeRecommendationCreateModal from "@/components/App/Inspections/Profile/Enforcements/ChargeRecommendation/ChargeRecommendationCreateModal";
import ChargeRecommendationUpdateModal from "@/components/App/Inspections/Profile/Enforcements/ChargeRecommendation/ChargeRecommendationUpdateModal";
import ViolationTicketCreateModal from "@/components/App/Inspections/Profile/Enforcements/ViolationTicket/ViolationTicketCreateModal";
import ViolationTicketUpdateModal from "@/components/App/Inspections/Profile/Enforcements/ViolationTicket/ViolationTicketUpdateModal";
import RestorativeJusticeCreateModal from "@/components/App/Inspections/Profile/Enforcements/RestorativeJustice/RestorativeJusticeCreateModal";
import RestorativeJusticeUpdateModal from "@/components/App/Inspections/Profile/Enforcements/RestorativeJustice/RestorativeJusticeUpdateModal";
import { prepNonProceededRequirements } from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { useAdministrativePenaltiesData } from "@/hooks/useAdministrativePenalties";
import { useChargeRecommendationsData } from "@/hooks/useChargeRecommendations";
import { useViolationTicketsData } from "@/hooks/useViolationTickets";
import { useRestorativeJusticeByInspection } from "@/hooks/useRestorativeJustice";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";

interface InspectionEnforcementsProps {
  inspectionData: Inspection;
}

const InspectionEnforcements: React.FC<InspectionEnforcementsProps> = ({
  inspectionData,
}) => {
  const queryClient = useQueryClient();
  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();
  const { setOpen: setDrawerOpen, setClose: setDrawerClose } = useDrawer();
  const [isDataLoading, setIsDataLoading] = React.useState<boolean>(true);
  const [requirementEnforcements, setRequirementEnforcements] = React.useState<
    InspectionRequirement[]
  >([]);

  const isEnforcementsAllowed = useMemo(
    () => inspectionData?.inspection_status?.toLowerCase() === "open",
    [inspectionData]
  );

  const { data: caseFile } = useCaseFileByNumber(
    inspectionData.case_file.case_file_number
  );

  const issuingOfficers = useMemo(
    () =>
      [caseFile?.primary_officer, ...(caseFile?.officers || [])].filter(
        (officer) => officer !== undefined
      ),
    [caseFile]
  );

  const {
    data: inspectionRequirementsData,
    isLoading: isInspectionRequirementsLoading,
  } = useInspectionRequirementsData(inspectionData.id);

  const {
    data: inspectionOrdersData,
    isLoading: isInspectionOrdersLoading,
    refetch: refetchInspectionOrders,
  } = useInspectionOrdersData(inspectionData.id);

  const {
    data: inspectionWarningLettersData,
    isLoading: isInspectionWarningLettersLoading,
    refetch: refetchInspectionWarningLetters,
  } = useInspectionWarningLettersData(inspectionData.id);

  const {
    data: inspectionAdministrativePenaltiesData,
    isLoading: isInspectionAdministrativePenaltiesLoading,
  } = useAdministrativePenaltiesData(inspectionData.id);

  const {
    data: inspectionChargeRecommendationsData,
    isLoading: isInspectionChargeRecommendationsLoading,
  } = useChargeRecommendationsData(inspectionData.id);

  const {
    data: inspectionViolationTicketsData,
    isLoading: isInspectionViolationTicketsLoading,
  } = useViolationTicketsData(inspectionData.id);

  const {
    data: inspectionRestorativeJusticeData,
    isLoading: isInspectionRestorativeJusticeLoading,
  } = useRestorativeJusticeByInspection(inspectionData.id);

  useEffect(() => {
    if (
      !isInspectionRequirementsLoading &&
      !isInspectionOrdersLoading &&
      !isInspectionWarningLettersLoading &&
      !isInspectionAdministrativePenaltiesLoading &&
      !isInspectionChargeRecommendationsLoading &&
      !isInspectionViolationTicketsLoading &&
      !isInspectionRestorativeJusticeLoading
    ) {
      setIsDataLoading(false);
    }
  }, [
    isInspectionRequirementsLoading,
    isInspectionOrdersLoading,
    isInspectionWarningLettersLoading,
    isInspectionAdministrativePenaltiesLoading,
    isInspectionChargeRecommendationsLoading,
    isInspectionViolationTicketsLoading,
    isInspectionRestorativeJusticeLoading,
  ]);

  useEffect(() => {
    if (inspectionRequirementsData) {
      // filter requirements with enforcement actions as order, warning letter, administrative penalty, or violation ticket
      const filteredRequirements = inspectionRequirementsData.filter(
        (requirement) =>
          requirement.enforcement_action_data?.length &&
          requirement.enforcement_action_data.some((enforcement) =>
            [
              EnforcementActionEnum.WARNING_LETTER,
              EnforcementActionEnum.ORDER,
              EnforcementActionEnum.AP_RECOMMENDATION,
              EnforcementActionEnum.CHARGE_RECOMMENDATION,
              EnforcementActionEnum.VIOLATION_TICKET,
              EnforcementActionEnum.RESTORATIVE_JUSTICE,
            ].includes(enforcement.id as EnforcementActionEnum)
          )
      );
      setRequirementEnforcements(filteredRequirements);
    }
  }, [inspectionRequirementsData]);

  const nonProceededOrderRequirements = useMemo(() => {
    if (!requirementEnforcements) return [];
    const orderReqIds = inspectionOrdersData?.map((order) =>
      order.order_requirement_maps?.map((map) => map.inspection_requirement_id)
    );
    return prepNonProceededRequirements({
      requirements: requirementEnforcements,
      reqIds: orderReqIds,
      enforcementActionType: EnforcementActionEnum.ORDER,
    });
  }, [requirementEnforcements, inspectionOrdersData]);

  const nonProceededWarningLetterRequirements = useMemo(() => {
    if (!requirementEnforcements) return [];
    const warningLetterReqIds = inspectionWarningLettersData?.map(
      (warningLetter) =>
        warningLetter.warning_letter_requirement_maps?.map(
          (map) => map.inspection_requirement_id
        )
    );
    return prepNonProceededRequirements({
      requirements: requirementEnforcements,
      reqIds: warningLetterReqIds,
      enforcementActionType: EnforcementActionEnum.WARNING_LETTER,
    });
  }, [requirementEnforcements, inspectionWarningLettersData]);

  const nonProceededAPRequirements = useMemo(() => {
    if (!requirementEnforcements) return [];
    const apReqIds = inspectionAdministrativePenaltiesData?.map(
      (administrativePenalty) =>
        administrativePenalty.administrative_penalty_requirement_maps?.map(
          (map) => map.inspection_requirement_id
        )
    );
    return prepNonProceededRequirements({
      requirements: requirementEnforcements,
      reqIds: apReqIds,
      enforcementActionType: EnforcementActionEnum.AP_RECOMMENDATION,
    });
  }, [requirementEnforcements, inspectionAdministrativePenaltiesData]);

  const nonProceededChargeRecommendationRequirements = useMemo(() => {
    if (!requirementEnforcements) return [];

    const chargeRecommendationReqIds = inspectionChargeRecommendationsData?.map(
      (chargeRecommendation) =>
        chargeRecommendation.charge_recommendation_requirement_maps?.map(
          (map) => map.inspection_requirement_id
        )
    );

    return requirementEnforcements
      .filter(
        (requirement) =>
          requirement.enforcement_action_data?.some(
            (enforcement) =>
              enforcement.id === EnforcementActionEnum.CHARGE_RECOMMENDATION
          ) && !chargeRecommendationReqIds?.flat().includes(requirement.id)
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements, inspectionChargeRecommendationsData]);

  const allRequirementsForChargeRecommendation = useMemo(() => {
    if (!requirementEnforcements) return [];

    return requirementEnforcements.map((requirement) => ({
      ...requirement,
      enforcement_action_data: requirement.enforcement_action_data || [],
    }));
  }, [requirementEnforcements]);

  const nonProceededVTRequirements = useMemo(() => {
    if (!requirementEnforcements) return [];
    const vtReqIds = inspectionViolationTicketsData?.map((violationTicket) =>
      violationTicket.violation_ticket_requirement_maps?.map(
        (map) => map.inspection_requirement_id
      )
    );
    return prepNonProceededRequirements({
      requirements: requirementEnforcements,
      reqIds: vtReqIds,
      enforcementActionType: EnforcementActionEnum.VIOLATION_TICKET,
    });
  }, [requirementEnforcements, inspectionViolationTicketsData]);

  const allRequirementsForRestorativeJustice = useMemo(() => {
    if (!requirementEnforcements) return [];

    return requirementEnforcements
      .filter(
        (requirement) => requirement.compliance_finding?.name === "Out" // ✅ filter compliance_finding is Out
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements]);

  const openEnforcementModal = (
    modelType: EnforcementActionEnum,
    requirement?: InspectionRequirement
  ) => {
    let content;
    switch (modelType) {
      case EnforcementActionEnum.ORDER:
        content = (
          <OrderCreateModal
            inspectionData={inspectionData}
            requirementsList={nonProceededOrderRequirements}
            requirement={requirement}
            onSubmit={(data) => {
              openEnforcementOrderDrawer(data);
              setModalClose();
            }}
          />
        );
        break;
      case EnforcementActionEnum.WARNING_LETTER:
        content = (
          <WarningLetterCreateModal
            inspectionData={inspectionData}
            requirementsList={nonProceededWarningLetterRequirements}
            requirement={requirement}
            onSubmit={(data) => {
              openEnforcementWarningLetterDrawer(data);
              setModalClose();
            }}
          />
        );
        break;
      case EnforcementActionEnum.AP_RECOMMENDATION:
        content = (
          <AdministrativePenaltyCreateModal
            inspectionData={inspectionData}
            requirementsList={nonProceededAPRequirements}
            requirement={requirement}
            onSubmit={() => {
              setModalClose();
            }}
          />
        );
        break;
      case EnforcementActionEnum.CHARGE_RECOMMENDATION:
        content = (
          <ChargeRecommendationCreateModal
            inspectionData={inspectionData}
            requirementsList={allRequirementsForChargeRecommendation}
            requirement={requirement}
            onSubmit={() => {
              setModalClose();
            }}
          />
        );
        break;
      case EnforcementActionEnum.VIOLATION_TICKET:
        content = (
          <ViolationTicketCreateModal
            inspectionData={inspectionData}
            requirementsList={nonProceededVTRequirements}
            requirement={requirement}
            onSubmit={() => {
              setModalClose();
            }}
          />
        );
        break;
      case EnforcementActionEnum.RESTORATIVE_JUSTICE:
        content = (
          <RestorativeJusticeCreateModal
            inspectionData={inspectionData}
            requirementsList={allRequirementsForRestorativeJustice}
            requirement={requirement}
            onSubmit={() => {
              setModalClose();
            }}
          />
        );
        break;
    }

    setModalOpen({
      content,
      width: "520px",
    });
  };

  const actionsList = [
    {
      text: "Warning Letter",
      onClick: () => openEnforcementModal(EnforcementActionEnum.WARNING_LETTER),
    },
    {
      text: "Order",
      onClick: () => openEnforcementModal(EnforcementActionEnum.ORDER),
    },
    {
      text: "Administrative Penalty Recommendation",
      onClick: () =>
        openEnforcementModal(EnforcementActionEnum.AP_RECOMMENDATION),
    },
    {
      text: "Charge Recommendation",
      onClick: () =>
        openEnforcementModal(EnforcementActionEnum.CHARGE_RECOMMENDATION),
    },
    {
      text: "Violation Ticket",
      onClick: () =>
        openEnforcementModal(EnforcementActionEnum.VIOLATION_TICKET),
    },
    {
      text: "Restorative Justice",
      onClick: () =>
        openEnforcementModal(EnforcementActionEnum.RESTORATIVE_JUSTICE),
    },
  ];

  const openEnforcementOrderDrawer = (order: InspectionOrder) => {
    setDrawerOpen({
      content: (
        <OrderDrawer
          onSubmit={(message, isCloseDrawer) => {
            notify.success(message);
            refetchInspectionOrders();
            queryClient.invalidateQueries({
              queryKey: [
                "inspection-orders-projectwise",
                inspectionData.case_file_id,
              ],
            });
            if (isCloseDrawer) {
              setDrawerClose();
            }
          }}
          inspection={inspectionData}
          enforcementOrder={order}
          staffUsersList={issuingOfficers || []}
          isReadonlyMode={!isEnforcementsAllowed}
          openEnforcementOrderDrawer={openEnforcementOrderDrawer}
        />
      ),
      width: DRAWER_WIDTHS.ENFORCEMENT_DRAWER,
    });
  };

  const openEnforcementWarningLetterDrawer = (
    warningLetter: InspectionWarningLetter
  ) => {
    setDrawerOpen({
      content: (
        <WarningLetterDrawer
          onSubmit={(message, isCloseDrawer) => {
            notify.success(message);
            refetchInspectionWarningLetters();
            if (isCloseDrawer) {
              setDrawerClose();
            }
          }}
          inspection={inspectionData}
          warningLetter={warningLetter}
          staffUsersList={issuingOfficers || []}
          isReadonlyMode={!isEnforcementsAllowed}
        />
      ),
      width: DRAWER_WIDTHS.ENFORCEMENT_DRAWER,
    });
  };

  const openAdministrativePenaltyUpdateModal = (
    administrativePenalty: AdministrativePenalty
  ) => {
    setModalOpen({
      content: (
        <AdministrativePenaltyUpdateModal
          administrativePenalty={administrativePenalty}
          inspectionData={inspectionData}
          onSuccess={() => {
            // Refresh the administrative penalties data
            queryClient.invalidateQueries({
              queryKey: [
                "inspection-administrative-penalties",
                inspectionData.id,
              ],
            });
          }}
          isReadonlyMode={!isEnforcementsAllowed}
        />
      ),
      width: MODAL_WIDTHS.ADMINISTRATIVE_PENALTY,
    });
  };

  const openChargeRecommendationUpdateModal = (
    chargeRecommendation: ChargeRecommendation
  ) => {
    setModalOpen({
      content: (
        <ChargeRecommendationUpdateModal
          chargeRecommendationData={chargeRecommendation}
          inspectionData={inspectionData}
          onSubmit={() => {
            // Refresh the charge recommendations data
            queryClient.invalidateQueries({
              queryKey: ["charge-recommendations", inspectionData.id],
            });
          }}
          isReadonlyMode={!isEnforcementsAllowed}
        />
      ),
      width: MODAL_WIDTHS.CHARGE_RECOMMENDATION,
    });
  };

  const openViolationTicketUpdateModal = (violationTicket: ViolationTicket) => {
    setModalOpen({
      content: (
        <ViolationTicketUpdateModal
          violationTicket={violationTicket}
          inspectionData={inspectionData}
          onSuccess={() => {
            // Refresh the violation tickets data
            queryClient.invalidateQueries({
              queryKey: ["inspection-violation-tickets", inspectionData.id],
            });
          }}
        />
      ),
      width: MODAL_WIDTHS.VIOLATION_TICKET,
    });
  };

  const openRestorativeJusticeUpdateModal = (
    restorativeJustice: RestorativeJustice
  ) => {
    setModalOpen({
      content: (
        <RestorativeJusticeUpdateModal
          restorativeJustice={restorativeJustice}
          inspectionData={inspectionData}
          onSuccess={() => {
            // Refresh the restorative justice data
            queryClient.invalidateQueries({
              queryKey: ["inspection-restorative-justice", inspectionData.id],
            });
          }}
          isReadonlyMode={!isEnforcementsAllowed}
        />
      ),
      width: MODAL_WIDTHS.RESTORATIVE_JUSTICE,
    });
  };

  return (
    <DynamicHeightBox
      display={"flex"}
      flexGrow={1}
      flexDirection={"column"}
      overflow={"auto"}
      bottomOffset={20}
    >
      <Box display={"flex"} justifyContent={"space-between"} mt={3} mb={2}>
        <Typography variant="h6">Enforcement</Typography>
        {!isDataLoading && isEnforcementsAllowed && (
          <MenuActionDropdown
            buttonText="New Enforcement"
            actions={actionsList}
            menuWidth="auto"
            menuIcon={<AddRounded />}
          />
        )}
      </Box>
      {isDataLoading ? (
        // TODO: change to enforcement loading
        <RequirementLoading />
      ) : (
        <>
          {isEnforcementsAllowed &&
            [
              ...nonProceededOrderRequirements,
              ...nonProceededWarningLetterRequirements,
              ...nonProceededAPRequirements,
              ...nonProceededChargeRecommendationRequirements,
              ...nonProceededVTRequirements,
            ].map((requirement, index) => (
              <EnforcementNotificationCard
                key={index}
                requirement={requirement}
                openEnforcementModal={openEnforcementModal}
              />
            ))}
          {inspectionOrdersData?.map((order) => (
            <Box
              key={order.id}
              onClick={() => openEnforcementOrderDrawer(order)}
            >
              <EnforcementCard
                order={order}
                requirementEnforcements={requirementEnforcements}
              />
            </Box>
          ))}
          {inspectionWarningLettersData?.map((warningLetter) => (
            <Box
              key={warningLetter.id}
              onClick={() => openEnforcementWarningLetterDrawer(warningLetter)}
            >
              <EnforcementCard
                warningLetter={warningLetter}
                requirementEnforcements={requirementEnforcements}
              />
            </Box>
          ))}
          {inspectionAdministrativePenaltiesData?.map((penality) => (
            <Box
              key={penality.id}
              onClick={() => openAdministrativePenaltyUpdateModal(penality)}
            >
              <EnforcementCard
                administrativePenalty={penality}
                requirementEnforcements={requirementEnforcements}
              />
            </Box>
          ))}
          {inspectionChargeRecommendationsData?.map((chargeRecommendation) => (
            <Box
              key={chargeRecommendation.id}
              onClick={() =>
                openChargeRecommendationUpdateModal(chargeRecommendation)
              }
            >
              <EnforcementCard
                chargeRecommendation={chargeRecommendation}
                requirementEnforcements={requirementEnforcements}
              />
            </Box>
          ))}
          {inspectionViolationTicketsData?.map((violationTicket) => (
            <Box
              key={violationTicket.id}
              onClick={() => openViolationTicketUpdateModal(violationTicket)}
            >
              <EnforcementCard
                violationTicket={violationTicket}
                requirementEnforcements={requirementEnforcements}
              />
            </Box>
          ))}
          {inspectionRestorativeJusticeData?.map((restorativeJustice) => (
            <Box
              key={restorativeJustice.id}
              onClick={() =>
                openRestorativeJusticeUpdateModal(restorativeJustice)
              }
            >
              <EnforcementCard
                restorativeJustice={restorativeJustice}
                requirementEnforcements={requirementEnforcements}
              />
            </Box>
          ))}
        </>
      )}
    </DynamicHeightBox>
  );
};

export default InspectionEnforcements;
