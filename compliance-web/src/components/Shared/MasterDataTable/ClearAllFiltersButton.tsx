import { Button } from "@mui/material";

interface ClearAllFiltersButtonProps {
  onClick: () => void;
}

const ClearAllFiltersButton: React.FC<ClearAllFiltersButtonProps> = ({
  onClick,
}) => (
  <Button variant="outlined" size="small" onClick={onClick}>
    Clear All
  </Button>
);

export default ClearAllFiltersButton;
