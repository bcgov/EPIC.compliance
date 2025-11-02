import { MQ } from "@/styles/responsive";
import { Box } from "@mui/material";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
  id: string;
  width?: string;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, id, width = "75%", ...other } = props;

  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`${id}-${index}`}
      aria-labelledby={`${id}-${index}`}
      {...other}
      overflow={"auto"}
      sx={{
        width: width,
        [MQ.mdToLg]: {
          width: "100%",
        },
      }}
    >
      {value === index && children}
    </Box>
  );
}

export default TabPanel;
