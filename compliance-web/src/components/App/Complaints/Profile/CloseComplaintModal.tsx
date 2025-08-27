import { DialogContent, Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { FC, useEffect } from "react";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import {
  useComplaintResolutionsData,
  useUpdateComplaintStatus,
} from "@/hooks/useComplaints";
import { ComplaintResolution } from "@/models/ComplaintResolution";
import { Complaint, ComplaintStatusAPIData } from "@/models/Complaint";
import { Agency } from "@/models/Agency";
import { ComplaintResolutionEnum } from "@/components/App/Complaints/ComplaintFormUtils";
import { useAgenciesData } from "@/hooks/useAgencies";

type CloseComplaintModalProps = {
  complaintData: Complaint;
  onUpdateStatusSuccess: () => void;
};

const closeComplaintSchema = yup.object().shape({
  resolution: yup
    .object<ComplaintResolution>()
    .nullable()
    .required("Please select a resolution"),
  agency: yup.object<Agency>().when("resolution", {
    is: (resolution: ComplaintResolution) =>
      resolution?.id === ComplaintResolutionEnum.AGENCY,
    then: (schema) => schema.required("Agency is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
});

export type CloseComplaintFormType = yup.InferType<typeof closeComplaintSchema>;

const initFormData = {
  resolution: undefined,
  agency: undefined,
};

const CloseComplaintModal: FC<CloseComplaintModalProps> = ({
  complaintData,
  onUpdateStatusSuccess,
}) => {
  const { data: complaintResolutions } = useComplaintResolutionsData();
  const { data: agencies } = useAgenciesData();

  const methods = useForm<CloseComplaintFormType>({
    resolver: yupResolver(closeComplaintSchema),
    mode: "onBlur",
    defaultValues: initFormData,
  });

  const { handleSubmit, reset, watch } = methods;

  const resolution = watch("resolution") as ComplaintResolution;

  useEffect(() => {
    reset(initFormData);
  }, [reset]);

  const { mutate: updateComplaintStatus, isPending } = useUpdateComplaintStatus(
    onUpdateStatusSuccess
  );

  const onSubmitHandler = (data: CloseComplaintFormType) => {
    const complaintStatus: ComplaintStatusAPIData = {
      status: "CLOSED",
      resolution_id: (data.resolution as ComplaintResolution).id,
    };
    if (complaintStatus.resolution_id === ComplaintResolutionEnum.AGENCY) {
      complaintStatus.resolution_agency_id = (data.agency as Agency).id.toString();
    }
    updateComplaintStatus({
      id: complaintData?.id ?? 0,
      complaintStatus,
    });
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <ModalTitleBar title={"Close Complaint?"} />
        <DialogContent dividers>
          <Typography variant="body1" sx={{ mb: "1rem" }}>
            You are about to close complaint{" "}
            <b>{complaintData?.complaint_number ?? ""}</b>.
          </Typography>
          <ControlledAutoComplete
            name="resolution"
            label="Resolution"
            placeholder="Select Resolution"
            options={complaintResolutions ?? []}
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
            sx={{ mb: "-0.5rem" }}
            disabled={!complaintResolutions?.length}
            isRequired={true}
          />
          {resolution?.id === ComplaintResolutionEnum.AGENCY && (
            <ControlledAutoComplete
              name="agency"
              label="Agency"
              placeholder="Select Agency"
              options={agencies ?? []}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              disabled={!agencies?.length}
              isRequired={true}
            />
          )}
        </DialogContent>
        <ModalActions
          primaryActionButtonText={"Close Complaint"}
          isButtonValidation
          isLoading={isPending}
        />
      </form>
    </FormProvider>
  );
};

export default CloseComplaintModal;
