import { notify } from "@/store/snackbarStore";
import { AddRounded } from "@mui/icons-material";
import { Button } from "@mui/material";
import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import InspectionDrawer from "@/components/App/Inspections/InspectionDrawer";
import { useDrawer } from "@/store/drawerStore";
import { CaseFile } from "@/models/CaseFile";
import { useParams } from "@tanstack/react-router";

const CaseFileCreateInspection = () => {
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useDrawer();
  const { caseFileNumber } = useParams({ strict: false });

  const caseFileData = queryClient.getQueryData<CaseFile>([
    "case-file",
    caseFileNumber,
  ]);

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["inspections-by-caseFileId", caseFileData?.id],
      });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, setClose, caseFileData]
  );

  const handleOpenInspectionDrawer = useCallback(() => {
    setOpen({
      content: (
        <InspectionDrawer
          onSubmit={handleOnSubmit}
          caseFile={caseFileData as CaseFile}
        />
      ),
      width: "1118px",
    });
  }, [setOpen, handleOnSubmit, caseFileData]);

  return (
    <Button
      variant="text"
      size="small"
      onClick={handleOpenInspectionDrawer}
      startIcon={<AddRounded />}
    >
      Inspection
    </Button>
  );
};

export default CaseFileCreateInspection;
