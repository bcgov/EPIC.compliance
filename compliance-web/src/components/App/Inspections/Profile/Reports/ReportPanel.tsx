import { Box } from "@mui/material";
import { motion } from "framer-motion";

interface ReportPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const ReportPanel: React.FC<ReportPanelProps> = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`ir-tabpanel-${index}`}
      aria-labelledby={`ir-tab-${index}`}
      {...other}
      width="70%"
      sx={{
        overflow: "auto",
        minHeight: "200px",
        height: "calc(100vh - var(--ir-tabs-container-top-position))",
      }}
    >
      {value === index && (
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          {children}
        </motion.div>
      )}
    </Box>
  );
};

export default ReportPanel;
