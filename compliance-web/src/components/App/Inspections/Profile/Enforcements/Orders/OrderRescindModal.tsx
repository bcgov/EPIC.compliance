import {
  DialogContent,
  Typography,
} from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import { FC, useEffect } from "react";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { InspectionOrder } from "@/models/InspectionOrder";
import {
  useReplaceOrder,
  useUpdateOrderStatus,
} from "@/hooks/useInspectionOrders";
import { OrderStatusEnum } from "@/utils/constants";
import OrderRescindActions from "./OrderRescindActions";
type OrderRescindModalProps = {
  order: InspectionOrder;
  onSuccess: (message: string, data?: InspectionOrder) => void;
  isHistoricalInspection?: boolean;
};

const createOrderRescindSchema = (isHistoricalInspection: boolean) =>
  yup.object().shape({
    replacementOrderNumber: isHistoricalInspection
      ? yup
          .string()
          .required("Please enter a replacement order number")
          .nullable()
      : yup.string().nullable().notRequired(),
  });

const initFormData = {
  replacementOrderNumber: undefined,
};

const OrderRescindModal: FC<OrderRescindModalProps> = ({
  order,
  onSuccess,
  isHistoricalInspection,
}) => {

  const orderRescindSchema = createOrderRescindSchema(
    isHistoricalInspection ?? false
  );

  type OrderRescindFormType = yup.InferType<
    ReturnType<typeof createOrderRescindSchema>
  >;

  const methods = useForm<OrderRescindFormType>({
    resolver: yupResolver(orderRescindSchema),
    mode: "onBlur",
    defaultValues: initFormData,
  });

  const {
    handleSubmit,
    reset,
    formState: { isValid },
  } = methods;

  useEffect(() => {
    reset(initFormData);
  }, [reset]);

  const onReplaceSuccess = (data: InspectionOrder) => {
    onSuccess("Order replaced", data);
  };

  const { mutate: updateOrderStatus, isPending: isRescindLoading } = useUpdateOrderStatus(() =>
    onSuccess("Order rescinded")
  );
  const { mutate: replaceOrder, isPending: isReplaceLoading } = useReplaceOrder(onReplaceSuccess);

  const onRescindHandler = () => {
    updateOrderStatus({
      inspectionOrderId: order.id ?? 0,
      statusPayload: {
        status: OrderStatusEnum.RESCINDED,
      },
    });
  };

  const onReplaceHandler = (data: OrderRescindFormType) => {
    const payload: {
      inspectionOrderId: number;
      replacementOrderNumber?: string;
    } = {
      inspectionOrderId: order.id ?? 0,
    };
    if (isHistoricalInspection && data.replacementOrderNumber) {
      payload.replacementOrderNumber = data.replacementOrderNumber;
    }
    replaceOrder(payload);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onReplaceHandler)}>
        <ModalTitleBar title={"Rescind Order?"} />
        <DialogContent dividers>
          <Typography variant="body1">
            You are about to rescind Order <strong>{order.order_number}</strong>
            . Choose how you would like to proceed:
          </Typography>
          <ul
            style={{
              marginTop: 8,
              marginBottom: 16,
              paddingLeft: 24,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <li>
              <Typography variant="body1">
                <strong>Rescind</strong> — Rescind this order immediately. It
                will no longer be open.
              </Typography>
            </li>
            <li>
              <Typography variant="body1">
                <strong>Replace</strong> — Create a new draft order from this
                one. When the new order is issued, this order will be rescinded
                and replaced.
              </Typography>
            </li>
          </ul>
          {isHistoricalInspection && (
            <ControlledTextField
              name="replacementOrderNumber"
              label="Replacement Order #"
              placeholder="Enter Replacement Order Number"
              fullWidth
              isRequired={true}
            />
          )}
        </DialogContent>
        <OrderRescindActions
          onReplaceAction={() => handleSubmit(onReplaceHandler)()}
          onRescindAction={onRescindHandler}
          isButtonValidation={true}
          onRescindConfirmationText={`Are you sure you want to rescind this?`}
          isLoading={isReplaceLoading}
          isRescindActionLoading={isRescindLoading}
        />
      </form>
    </FormProvider>
  );
};

export default OrderRescindModal;
