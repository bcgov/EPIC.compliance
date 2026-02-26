import ControlledDateTimeField from "@/components/Shared/Controlled/ControlledDateTimeField";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import {
  useCreateContinuationReportEntry,
  useDeleteContinuationReportEntry,
  useUpdateContinuationReportEntry,
} from "@/hooks/useContinuationReports";
import {
  ContinuationReport,
  ContinuationReportAPIData,
  ContinuationReportFormData,
} from "@/models/ContinuationReport";
import dateUtils from "@/utils/dateUtils";
import { yupResolver } from "@hookform/resolvers/yup";
import { Button, DialogContent, Stack } from "@mui/material";
import dayjs, { Dayjs } from "dayjs";
import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { ContinuationReportContextType } from "./ContinuationReport";
import ControlledLexicalEditor from "@/components/Shared/Controlled/ControlledLexicalEditor";
import { AccessTimeRounded } from "@mui/icons-material";

type ContinuationReportEntryModal = {
  onSubmit: (submitMsg: string) => void;
  continuationReportEntry?: ContinuationReport;
  context: ContinuationReportContextType;
};

const continuationReportFormSchema = yup.object().shape({
  dateOfEntry: yup
    .mixed<Dayjs>()
    .nullable()
    .required("Date Created is required"),
  entry: yup
    .object({
      html: yup.string().required("Action is required"),
      text: yup.string().required("Action is required"),
    })
    .nullable()
    .required("Action is required"),
});

type ContinuationReportSchemaType = yup.InferType<
  typeof continuationReportFormSchema
>;

const initFormData: ContinuationReportFormData = {
  dateOfEntry: undefined,
  entry: undefined,
};

const ContinuationReportEntryModal: React.FC<ContinuationReportEntryModal> = ({
  onSubmit,
  continuationReportEntry,
  context,
}) => {
  const defaultValues = useMemo<ContinuationReportFormData>(() => {
    if (continuationReportEntry) {
      // map existing data
      return {
        dateOfEntry: dayjs(continuationReportEntry.date_created),
        entry: {
          html: continuationReportEntry.rich_text,
          text: continuationReportEntry.text,
        },
      };
    }
    return initFormData;
  }, [continuationReportEntry]);

  const methods = useForm<ContinuationReportSchemaType>({
    resolver: yupResolver(continuationReportFormSchema),
    mode: "onBlur",
    defaultValues,
  });
  const maxSelectableDate = dayjs().add(1, "day");
  const { handleSubmit, reset } = methods;

  useEffect(() => {
    if (continuationReportEntry) {
      reset(defaultValues);
    }
  }, [defaultValues, reset, continuationReportEntry]);

  const onSuccess = () => {
    onSubmit(
      continuationReportEntry ? "Successfully updated!" : "Successfully added!"
    );
  };

  const { mutate: addEntry, isPending: isPendingAddEntry } =
    useCreateContinuationReportEntry(onSuccess);
  const { mutate: updateEntry, isPending: isPendingUpdateEntry } =
    useUpdateContinuationReportEntry(onSuccess);
  const { mutate: deleteEntry, isPending: isPendingDeleteEntry } =
    useDeleteContinuationReportEntry(onSuccess);

  const onSubmitHandler = (data: ContinuationReportSchemaType) => {
    const crEntry: ContinuationReportAPIData = {
      text: data.entry.text,
      rich_text: data.entry.html,
      date_created: dateUtils.dateToISO(data.dateOfEntry),
    };
    if (continuationReportEntry) {
      updateEntry({
        id: continuationReportEntry.id,
        crEntry,
      });
    } else {
      addEntry({
        ...crEntry,
        case_file_id: context.caseFileId,
        context_type: context.contextType,
        context_id: context.contextId,
      });
    }
  };

  const onDeleteEntry = () => {
    if (continuationReportEntry?.id) {
      deleteEntry(continuationReportEntry.id);
    }
  };

  const setCurrentTime = () => {
    methods.setValue("dateOfEntry", dayjs());
  };

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmitHandler)}>
          <ModalTitleBar
            title={continuationReportEntry ? "Edit Entry" : "Add Entry"}
          />
          <DialogContent dividers>
            <Stack direction="row" spacing={2} alignItems="center">
              <ControlledDateTimeField
                name="dateOfEntry"
                width="67%"
                maxDate={maxSelectableDate}
                isRequired={true}
              />
              <Button
                color="secondary"
                size="small"
                sx={{ height: 40 }}
                onClick={setCurrentTime}
              >
                <AccessTimeRounded sx={{ mr: 1 }} />
                Set Current Time
              </Button>
            </Stack>
            <ControlledLexicalEditor
              label="Action"
              name="entry"
              isRequired={true}
            />
          </DialogContent>
          <ModalActions
            primaryActionButtonText={
              continuationReportEntry ? "Save" : "Add Entry"
            }
            isLoading={isPendingAddEntry || isPendingUpdateEntry}
            onDeleteAction={continuationReportEntry ? onDeleteEntry : undefined}
            isDeleteActionLoading={isPendingDeleteEntry}
          />
        </form>
      </FormProvider>
    </>
  );
};

export default ContinuationReportEntryModal;
