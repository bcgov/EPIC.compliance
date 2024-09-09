import { DialogContent } from "@mui/material";
import { Agency } from "@/models/Agency";
import { useAddAgency, useUpdateAgency } from "@/hooks/useAgencies";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { notify } from "@/store/snackbarStore";
import { AxiosError } from "axios";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { useEffect } from "react";

type AgencyModalProps = {
  onSubmit: (submitMsg: string) => void;
  agency?: Agency;
};

const agencySchema = yup.object().shape({
  name: yup
    .string()
    .required("Name is required")
    .max(150, "Max length exceeded"),
  abbreviation: yup.string().optional().max(10, "Max length exceeded"),
});

type AgencyForm = yup.InferType<typeof agencySchema>;

const AgencyModal: React.FC<AgencyModalProps> = ({ onSubmit, agency }) => {
  const onSuccess = () => {
    onSubmit(agency ? "Successfully updated!" : "Successfully added!");
  };

  const onError = (err: AxiosError) => {
    notify.error(err?.message);
  };

  const { mutate: addAgency } = useAddAgency(onSuccess, onError);
  const { mutate: updateAgency } = useUpdateAgency(onSuccess, onError);

  const methods = useForm({
    resolver: yupResolver(agencySchema),
    mode: "onBlur",
    defaultValues: agency,
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset(agency);
  }, [agency, reset]);

  const onSubmitHandler = async (data: AgencyForm) => {
    const agencyData = {
      name: data.name,
      abbreviation: data.abbreviation,
    };
    if (agency) {
      updateAgency({ id: agency.id, agency: agencyData });
    } else {
      addAgency(agencyData);
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <ModalTitleBar title={agency ? agency.name : "Add Agency"} />
        <DialogContent dividers>
          <ControlledTextField
            label="Name"
            name="name"
            placeholder="eg. Canada Energy Regulator"
            fullWidth
          />
          <ControlledTextField
            label="Abbreviation (optional)"
            name="abbreviation"
            placeholder="CER"
            fullWidth
          />
        </DialogContent>
        <ModalActions primaryActionButtonText={agency ? "Save" : "Add"} />
      </form>
    </FormProvider>
  );
};

export default AgencyModal;
