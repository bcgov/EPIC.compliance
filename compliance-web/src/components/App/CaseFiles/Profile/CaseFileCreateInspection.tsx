import InspectionDrawer from "@/components/App/Inspections/InspectionDrawer";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";
import { CaseFile } from "@/models/CaseFile";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { DRAWER_WIDTHS } from "@/utils/constants";
import { AddRounded } from "@mui/icons-material";
import { Button } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

const CaseFileCreateInspection = ({
  fileNumber,
  hidden = false,
}: {
  fileNumber: string;
  hidden?: boolean;
}) => {
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useDrawer();

  const caseFileData = queryClient.getQueryData<CaseFile>([
    "case-file",
    fileNumber,
  ]);

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["inspections-details-by-caseFileId", caseFileData?.id],
      });
      queryClient.invalidateQueries({
        queryKey: ["continuation-reports", caseFileData?.id],
      });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, setClose, caseFileData]
  );

  const drawerWidth = useResponsiveDrawerWidth(
    DRAWER_WIDTHS.INSPECTION_DRAWER
  );

  const handleOpenInspectionDrawer = useCallback(() => {
    setOpen({
      content: (
        <InspectionDrawer
          onSubmit={handleOnSubmit}
          caseFile={caseFileData as CaseFile}
        />
      ),
      width: drawerWidth,
    });
  }, [setOpen, handleOnSubmit, caseFileData, drawerWidth]);

  return hidden ? null : (
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
