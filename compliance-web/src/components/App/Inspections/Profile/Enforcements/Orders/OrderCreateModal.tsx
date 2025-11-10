import { Box, Collapse, Typography } from "@mui/material";
import { FC, useCallback, useEffect, useMemo, useState } from "react";
import { FormProvider, useForm, useFormContext } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { ExpandMoreRounded } from "@mui/icons-material";
import { useQueryClient } from "@tanstack/react-query";
import EnforcementModal from "@/components/App/Inspections/Profile/Enforcements/EnforcementModal";
import {
  orderSchema,
  getDefaultFormValues,
  ENFORCEMENT_MESSAGES,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import ControlledCheckbox from "@/components/Shared/Controlled/ControlledCheckbox";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { useCreateInspectionOrder } from "@/hooks/useInspectionOrders";
import {
  InspectionOrder,
  InspectionOrderAPIData,
} from "@/models/InspectionOrder";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { notify } from "@/store/snackbarStore";

type OrderFormType = yup.InferType<typeof orderSchema>;

const ManualOrderNumberInfo = () => {
  const [isInfoExpanded, setIsInfoExpanded] = useState(false);

  return (
    <Box
      sx={{ display: "flex", gap: 1, ml: 3, cursor: "pointer" }}
      onClick={() => setIsInfoExpanded(!isInfoExpanded)}
    >
      <ExpandMoreRounded
        sx={{
          marginTop: "-0.125rem",
          fontSize: "1.25rem",
          transform: isInfoExpanded ? "rotate(180deg)" : "rotate(270deg)",
        }}
      />
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
        <Typography variant="caption">Why enter a manual Order #?</Typography>
        <Collapse in={isInfoExpanded}>
          <Typography variant="caption">
            If you are entering an order that was previously created outside
            this system, check this box and enter the existing Order #. If this
            is a new order, leave the box unchecked, and the system will
            generate a number for you.
          </Typography>
        </Collapse>
      </Box>
    </Box>
  );
};

const OrderFormFields = () => {
  const { watch } = useFormContext<OrderFormType>();
  const isHistoricalRecord = watch("isHistoricalRecord");

  return (
    <>
      <ControlledCheckbox
        name="isHistoricalRecord"
        label="Check this box to enter an existing Order # for historical records."
        fontSize="small"
      />
      <ManualOrderNumberInfo />
      {isHistoricalRecord && (
        <ControlledTextField
          name="manualOrderNumber"
          label="Manual Order #"
          placeholder="Enter existing order number"
          sx={{ mt: 2 }}
          fullWidth
        />
      )}
    </>
  );
};

type OrderCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  onSubmit: (data: InspectionOrder) => void;
};

const OrderCreateModal: FC<OrderCreateModalProps> = ({
  inspectionData,
  requirementsList,
  requirement,
  onSubmit,
}) => {
  const queryClient = useQueryClient();

  const defaultValues = useMemo(() => {
    return getDefaultFormValues(requirement, false, undefined);
  }, [requirement]);

  const methods = useForm<OrderFormType>({
    resolver: yupResolver(orderSchema),
    mode: "onBlur",
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
    queryClient.invalidateQueries({
      queryKey: ["pending-items", inspectionData.id],
    });
    notifyAndSubmit(data);
  };

  const notifyAndSubmit = (data: InspectionOrder) => {
    notify.success(ENFORCEMENT_MESSAGES.ORDER_CREATED(data.order_number || ""));
    onSubmit(data);
  };

  const { mutate: createInspectionOrder, isPending: isPendingOrder } =
    useCreateInspectionOrder(onSuccess);

  const handleBaseSubmit = useCallback(
    (data: OrderFormType) => {
      const orderData: InspectionOrderAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (
          data.requirements as InspectionRequirement[]
        ).map((requirement) => requirement.id),
      };

      if (data.isHistoricalRecord) {
        orderData.order_number = data.manualOrderNumber ?? "";
      }

      createInspectionOrder({
        inspectionOrder: orderData,
      });
    },
    [createInspectionOrder, inspectionData]
  );

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        title="Create Order"
        onSubmit={handleBaseSubmit}
        isLoading={isPendingOrder}
        additionalFormFields={<OrderFormFields />}
      />
    </FormProvider>
  );
};

export default OrderCreateModal;
