import { useState } from "react";
import { IconButton } from "@mui/material";
import { FileCopy, FileCopyOutlined } from "@mui/icons-material";
import { BCDesignTokens } from "epic.theme";

const iconStyles = { color: BCDesignTokens.themeBlue90, fontSize: "1rem" };

const CopyButton = ({ ...props }) => {
  const copyHandler = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const [hover, setHover] = useState<boolean>(false);

  return (
    <IconButton
      color="primary"
      onClick={() => copyHandler(props.copyText)}
      sx={{
        width: "2rem",
        height: "2rem",
        borderRadius: "0.25rem",
      }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {hover ? (
        <FileCopy sx={iconStyles} />
      ) : (
        <FileCopyOutlined sx={iconStyles} />
      )}
    </IconButton>
  );
};

export default CopyButton;
