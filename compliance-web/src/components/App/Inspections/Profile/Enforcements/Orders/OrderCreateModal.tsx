import { FC, useCallback, useEffect, useMemo  } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import EnforcementModal from "@/components/App/Inspections/Profile/Enforcements/EnforcementModal";
import {
  orderSchema,
  BaseEnforcementFormType,
  getDefaultFormValues,
  ENFORCEMENT_MESSAGES,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { useCreateInspectionOrder, useLinkInspectionOrder } from "@/hooks/useInspectionOrders";
import {
  InspectionOrder,
  InspectionOrderAPIData,
} from "@/models/InspectionOrder";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import { EnforcementActionEnum } from "@/utils/constants";
import OrderCreationOptions from "./OrderCreationOptions";

const createOrderPenaltySchema = orderSchema.shape({
  orderCreationMethod: yup.string().required("Please select a creation method"),
  existingOrderId: yup.number().when("orderCreationMethod", {
    is: "link_existing",
    then: (schema) => schema.required("Please select an existing Order"),
    otherwise: (schema) => schema.notRequired(),
  }),
});

type OrderFormType = yup.InferType<typeof createOrderPenaltySchema>;

type OrderCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  enforcementAction: EnforcementActionEnum;
  nonProceededRequirements?: InspectionRequirement[];
  onSubmit: (data: InspectionOrder) => void;
};

const OrderCreateModal: FC<OrderCreateModalProps> = ({
  inspectionData,
  requirementsList,
  requirement,
  nonProceededRequirements,
  enforcementAction,
  onSubmit,
}) => {
  const queryClient = useQueryClient();
  const {  setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    return {
      ...getDefaultFormValues(requirement, false, undefined),
      manualOrderNumber: "",
      existingOrderId: undefined,
    };
  }, [requirement]);

  const methods = useForm<OrderFormType>({
    resolver: yupResolver(createOrderPenaltySchema),
    mode: "onChange",
    defaultValues,
  });

  const { reset } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSuccess = (data: InspectionOrder) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-orders", inspectionData.id],
    });
    notifyAndSubmit(data);
  };

  const notifyAndSubmit = (data: InspectionOrder) => {
    notify.success(ENFORCEMENT_MESSAGES.ORDER_CREATED(data.order_number || ""));
    onSubmit(data);
    setModalClose();
  };

  const {
    mutate: createInspectionOrder,
    isPending: isPendingOrder
  } = useCreateInspectionOrder(onSuccess);

  const {
    mutate: linkInspectionOrder,
    isPending: isPendingLink
  } = useLinkInspectionOrder(onSuccess);

  const handleBaseSubmit = useCallback(
    async ( data: BaseEnforcementFormType) => {
      const formData = methods.getValues();
      const requirementIds = (data.requirements as InspectionRequirement[]).map((requirement) => requirement.id);

      // Not historical - default to 'create_new'
      if (!inspectionData.is_history) {
        formData.orderCreationMethod = "create_new";
      }

      if (!formData.orderCreationMethod) {
        methods.setError("orderCreationMethod", {
          type: "required",
          message: "Please select a creation method.",
        });
        return;
      }
      if(formData.orderCreationMethod === 'manual_entry' && !formData.manualOrderNumber) {
        methods.setError("manualOrderNumber", {
          type: "required",
          message: "Please enter the historical Order number.",
        });
        notify.error("Please enter the historical Order number.");
        return;
      }
      if(formData.orderCreationMethod === 'link_existing' && !formData.existingOrderId) {
        methods.setError("existingOrderId", {
          type: "required",
          message: "Please select an existing Order to link.",
        });
        notify.error("Please select an existing Order to link.");
        return;
      }

      if(formData.orderCreationMethod === 'link_existing'){
        const linkData = {
          inspection_id: inspectionData.id,
          inspection_requirement_ids: requirementIds,
      };
      linkInspectionOrder({
        orderId: formData.existingOrderId!,
        link: linkData
      });
      return;
    }

      const orderData: InspectionOrderAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (
          data.requirements as InspectionRequirement[]
        ).map((requirement) => requirement.id),
      };//

      if(formData.orderCreationMethod === 'manual_entry' && formData.manualOrderNumber) {
        orderData.order_number = formData.manualOrderNumber;
      }

      // For 'create' option, do not set order_number - let system generate it
      createInspectionOrder({
        inspectionOrder: orderData,
      });
    },
    [createInspectionOrder, inspectionData, linkInspectionOrder, methods]
  );

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        nonProceededRequirements={nonProceededRequirements}
        enforcementAction={enforcementAction}
        title="Create Order"
        onSubmit={handleBaseSubmit}
        isLoading={isPendingOrder || isPendingLink}
        additionalFormFields={ inspectionData.is_history &&
           <FormProvider {...methods}>
            <OrderCreationOptions
              inspectionData={inspectionData}
              isHistorical={inspectionData.is_history}
            />
          </FormProvider>
        }
      />
    </FormProvider>
  );
};

export default OrderCreateModal;

