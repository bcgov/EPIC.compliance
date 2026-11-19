import { DescriptionOutlined } from "@mui/icons-material";
import { Button } from "@mui/material";
import { useState } from "react";
import { downloadFile } from "@/utils/appUtils";
import { useInspectionOrderRendered } from "@/hooks/useInspectionOrders";
import { EnforcementActionEnum } from "@/utils/constants";
import { useWarningLetterRendered } from "@/hooks/useInspectionWarningLetters";
import { ENFORCEMENT_TYPES } from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { notify } from "@/store/snackbarStore";
import { AxiosError } from "axios";

interface EnforcementDownloadDocxButtonProps {
  enforcementId: number;
  fileNumber: string;
  enforcementType: EnforcementActionEnum;
}

const EnforcementDownloadDocxButton = ({
  enforcementId,
  fileNumber,
  enforcementType,
}: EnforcementDownloadDocxButtonProps) => {
  const [isLoading, setIsLoading] = useState(false);

  const onError = (error: AxiosError) => {
    notify.error(error.message ?? "Error downloading DOCX");
    setIsLoading(false);
  };

  const { mutate: mutateOrderDocxData } = useInspectionOrderRendered(
    (data) => {
      downloadFile(data, `${fileNumber}.docx`);
      setIsLoading(false);
    },
    onError
  );

  const { mutate: mutateWarningLetterDocxData } = useWarningLetterRendered(
    (data) => {
      downloadFile(data, `${fileNumber}.docx`);
      setIsLoading(false);
    },
    onError
  );

  const handleDownloadClick = () => {
    setIsLoading(true);
    if (enforcementType === ENFORCEMENT_TYPES.ORDER) {
      mutateOrderDocxData({
        inspectionOrderId: enforcementId,
        format: "docx",
      });
    } else {
      mutateWarningLetterDocxData({
        inspectionWarningLetterId: enforcementId,
        format: "docx",
      });
    }
  };

  return (
    <Button variant="text" onClick={handleDownloadClick} disabled={isLoading}>
      <DescriptionOutlined sx={{ mr: 1, fontSize: 20 }} />
      {isLoading ? "Loading..." : "Download DOCX"}
    </Button>
  );
};

export default EnforcementDownloadDocxButton;
