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
import { partitionEnforcementsByOrigin, prepNonProceededRequirements } from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { useAdministrativePenaltiesData } from "@/hooks/useAdministrativePenalties";
import { useChargeRecommendationsData } from "@/hooks/useChargeRecommendations";
import { useViolationTicketsData } from "@/hooks/useViolationTickets";
import { useRestorativeJusticeByInspection } from "@/hooks/useRestorativeJustice";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";
import { KC_USER_GROUPS, useCurrentLoggedInUser, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { StaffUser } from "@/models/Staff";
import { useStaffUsersData } from "@/hooks/useStaff";

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
  const { data: staffData } = useStaffUsersData();
  const currentUser = useCurrentLoggedInUser();
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
  // Memoize the current user's staff ID
  const currentUserStaffId = useMemo(
    () =>
      staffData?.find(
        (staff: StaffUser) => staff.auth_user_guid === currentUser?.preferred_username
      )?.id ?? 0,
    [staffData, currentUser]
  );
  const isSuperUser = useIsRolesAllowed([KC_USER_GROUPS.SUPERUSER]);
  const isPrimaryOfficerOrSuperUser = useMemo(() => {
    return (
      inspectionData.primary_officer_id === currentUserStaffId ||
      isSuperUser
    );
  }, [inspectionData.primary_officer_id, currentUserStaffId, isSuperUser]);
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

  const sortedInspectionOrdersData = useMemo(() => {
    if (!inspectionOrdersData) return [];
    return partitionEnforcementsByOrigin(
      inspectionOrdersData.filter((order) => order.inspection_id !== undefined) as Array<InspectionOrder & { inspection_id: number }>,
      inspectionData.id
    );
  }, [inspectionOrdersData, inspectionData.id]);

  const sortedAdministrativePenaltiesData = useMemo(() => {
    if (!inspectionAdministrativePenaltiesData) return [];
    return partitionEnforcementsByOrigin(
      inspectionAdministrativePenaltiesData.filter(
        (penalty) => penalty.inspection_id !== undefined
      ) as Array<AdministrativePenalty & { inspection_id: number }>,
      inspectionData.id
    );
  }, [inspectionAdministrativePenaltiesData, inspectionData.id]);

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
  // All requirements marked for Order for which no orders created yet
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

  // All requirements marked for Order for which orders created or not
  const allRequirementsForOrder = useMemo(() => {
    if (!requirementEnforcements) return [];
    return requirementEnforcements
      .filter((requirement) =>
        requirement.enforcement_action_data?.some(
          (enforcement) => enforcement.id === EnforcementActionEnum.ORDER
        )
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements]);

  // All requirements marked for Warning Letter for which no warning letters created yet
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

  // All requirements marked for Warning Letter for which warning letters created or not
  const allRequirementsForWarningLetter = useMemo(() => {
    if (!requirementEnforcements) return [];
    return requirementEnforcements
      .filter((requirement) =>
        requirement.enforcement_action_data?.some(
          (enforcement) => enforcement.id === EnforcementActionEnum.WARNING_LETTER
        )
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements]);

  // All requirements marked for AP Recommendation for which no AP recommendations created yet
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

  // All requirements marked for AP Recommendation for which AP recommendations created or not
  const allRequirementsForAP = useMemo(() => {
    if (!requirementEnforcements) return [];
    return requirementEnforcements
      .filter((requirement) =>
        requirement.enforcement_action_data?.some(
          (enforcement) =>
            enforcement.id === EnforcementActionEnum.AP_RECOMMENDATION
        )
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements]);

  // All requirements marked for Charge Recommendation for which no charge recommendations created yet
  const nonProceededChargeRecommendationRequirements = useMemo(() => {
    if (!requirementEnforcements) return [];
    const chargeRecommendationReqIds = inspectionChargeRecommendationsData?.map(
      (chargeRecommendation) =>
        chargeRecommendation.charge_recommendation_requirement_maps?.map(
          (map) => map.inspection_requirement_id
        )
    );

    return prepNonProceededRequirements({
      requirements: requirementEnforcements,
      reqIds: chargeRecommendationReqIds,
      enforcementActionType: EnforcementActionEnum.CHARGE_RECOMMENDATION,
    });
  }, [requirementEnforcements, inspectionChargeRecommendationsData]);

  // All requirements marked for Charge Recommendation for which charge recommendations created or not
  const allRequirementsForChargeRecommendation = useMemo(() => {
    if (!requirementEnforcements) return [];

    return requirementEnforcements
      .filter((requirement) =>
        requirement.enforcement_action_data?.some(
          (enforcement) =>
            enforcement.id === EnforcementActionEnum.CHARGE_RECOMMENDATION
        )
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements]);

  // All requirements marked for Violation Ticket for which no violation tickets created yet
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
  // All requirements marked for Violation Ticket for which violation tickets created or not
  const allRequirementsForViolationTicket = useMemo(() => {
    if (!requirementEnforcements) return [];
    return requirementEnforcements
      .filter((requirement) =>
        requirement.enforcement_action_data?.some(
          (enforcement) =>
            enforcement.id === EnforcementActionEnum.VIOLATION_TICKET
        )
      )
      .map((requirement) => ({
        ...requirement,
        enforcement_action_data: requirement.enforcement_action_data || [],
      }));
  }, [requirementEnforcements]);

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
            requirementsList={allRequirementsForOrder}
            requirement={requirement}
            enforcementAction={modelType}
            nonProceededRequirements={nonProceededOrderRequirements}
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
            requirementsList={allRequirementsForWarningLetter}
            requirement={requirement}
            enforcementAction={modelType}
            nonProceededRequirements={nonProceededWarningLetterRequirements}
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
            requirementsList={allRequirementsForAP}
            requirement={requirement}
            isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
            enforcementAction={modelType}
            nonProceededRequirements={nonProceededAPRequirements}
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
            enforcementAction={modelType}
            isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
            nonProceededRequirements={nonProceededChargeRecommendationRequirements}
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
            requirementsList={allRequirementsForViolationTicket}
            nonProceededRequirements={nonProceededVTRequirements}
            enforcementAction={modelType}
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
            enforcementAction={modelType}
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
      // prevents the drawer from opening for linked orders
      if (order.type === 'OrderLink') {
        return;
      }
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
          isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
          onSuccess={() => {
            // Refresh the administrative penalties data
            queryClient.invalidateQueries({
              queryKey: [
                "inspection-administrative-penalties",
                inspectionData.id,
              ],
            });
          }}
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
          isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
          onSubmit={() => {
            // Refresh the charge recommendations data
            queryClient.invalidateQueries({
              queryKey: ["charge-recommendations", inspectionData.id],
            });
          }}
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
          isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
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
          isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
          onSuccess={() => {
            // Refresh the restorative justice data
            queryClient.invalidateQueries({
              queryKey: ["inspection-restorative-justice", inspectionData.id],
            });
          }}
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
          {sortedAdministrativePenaltiesData?.map((penality: AdministrativePenalty) => (
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
          {sortedInspectionOrdersData?.map((order: InspectionOrder) => (
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
        </>
      )}
    </DynamicHeightBox>
  );
};

export default InspectionEnforcements;
