import { DialogContent } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { FC, useEffect, useState } from "react";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { StaffUser } from "@/models/Staff";
import { STAFF_USER_POSITION } from "@/utils/constants";

type SendForApprovalModalProps = {
  staffUsers: StaffUser[];
  onSubmitHandler: (data: SendForApprovalFormType) => void;
  isPending: boolean;
};

const sendForApprovalSchema = yup.object().shape({
  director: yup
    .object<StaffUser>()
    .nullable()
    .required("Please select a director"),
});

export type SendForApprovalFormType = yup.InferType<typeof sendForApprovalSchema>;

const initFormData = {
  director: undefined,
};

const SendForApprovalModal: FC<SendForApprovalModalProps> = ({
  staffUsers,
  onSubmitHandler,
  isPending,
}) => {
  const [directorsList, setDirectorsList] = useState<StaffUser[]>([]);

  useEffect(() => {
    setDirectorsList(
      staffUsers?.filter((user) =>
        [
          STAFF_USER_POSITION.DIRECTOR,
          STAFF_USER_POSITION.DEPUTY_DIRECTOR,
        ].includes(user.position_id ?? 0)
      ) ?? []
    );
  }, [staffUsers]);

  const methods = useForm<SendForApprovalFormType>({
    resolver: yupResolver(sendForApprovalSchema),
    mode: "onChange",
    defaultValues: initFormData,
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset(initFormData);
  }, [reset]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <ModalTitleBar title={"Send for Deputy Approval?"} />
        <DialogContent dividers>
          <ControlledAutoComplete
            name="director"
            label="Deputy Director"
            placeholder="Select Deputy Director"
            options={directorsList ?? []}
            getOptionLabel={(option) =>
              `${option.first_name} ${option.last_name}`
            }
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
            sx={{ mb: "-0.5rem" }}
            disabled={!directorsList?.length}
            isRequired={true}
          />
        </DialogContent>
        {directorsList && directorsList.length > 0 && (
          <ModalActions
            primaryActionButtonText={"Send"}
            isButtonValidation
            isLoading={isPending}
          />
        )}
      </form>
    </FormProvider>
  );
};

export default SendForApprovalModal;
