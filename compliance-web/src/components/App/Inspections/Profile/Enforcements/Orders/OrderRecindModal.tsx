import {
  Box,
  Button,
  DialogActions,
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
import { useModal } from "@/store/modalStore";
type OrderRecindModalProps = {
  order: InspectionOrder;
  onSuccess: (message: string, data?: InspectionOrder) => void;
  isHistoricalInspection?: boolean;
};

const createOrderRecindSchema = (isHistoricalInspection: boolean) =>
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

const OrderRecindModal: FC<OrderRecindModalProps> = ({
  order,
  onSuccess,
  isHistoricalInspection,
}) => {
  const { setClose } = useModal();

  const orderRecindSchema = createOrderRecindSchema(
    isHistoricalInspection ?? false
  );

  type OrderRecindFormType = yup.InferType<
    ReturnType<typeof createOrderRecindSchema>
  >;

  const methods = useForm<OrderRecindFormType>({
    resolver: yupResolver(orderRecindSchema),
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

  const { mutate: updateOrderStatus } = useUpdateOrderStatus(() =>
    onSuccess("Order rescinded")
  );
  const { mutate: replaceOrder } = useReplaceOrder(onReplaceSuccess);

  const onRecindHandler = () => {
    updateOrderStatus({
      inspectionOrderId: order.id ?? 0,
      statusPayload: {
        status: OrderStatusEnum.RESCINDED,
      },
    });
  };

  const onReplaceHandler = (data: OrderRecindFormType) => {
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
        <ModalTitleBar title={"Recind Order?"} />
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
        <DialogActions
          sx={{
            padding: "1rem 1.5rem",
            justifyContent: "space-between",
          }}
        >
          <Button
            variant="text"
            onClick={() => setClose()}
            data-testid="recind-modal-button-cancel"
          >
            Cancel
          </Button>
          <Box sx={{ display: "flex", gap: "0.75rem" }}>
            <Button
              type="submit"
              data-testid="recind-modal-button-replace"
              disabled={!isValid}
            >
              Replace
            </Button>
            <Button
              color="error"
              onClick={onRecindHandler}
              data-testid="recind-modal-button-recind"
            >
              Recind
            </Button>
          </Box>
        </DialogActions>
      </form>
    </FormProvider>
  );
};

export default OrderRecindModal;
