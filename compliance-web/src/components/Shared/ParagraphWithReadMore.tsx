import { Link, Stack } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { useEffect, useRef, useState } from "react";

interface ParagraphWithReadMoreProps {
  maxHeight?: number;
  renderTypography?: React.ReactNode;
  expand?: boolean;
  isFormatted?: boolean;
}

export default function ParagraphWithReadMore({
  maxHeight = 150,
  renderTypography,
  expand = false,
  isFormatted = false,
}: ParagraphWithReadMoreProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showReadMore, setShowReadMore] = useState(false);

  useEffect(() => {
    if (
      contentRef.current &&
      contentRef.current.scrollHeight > maxHeight + 20
    ) {
      setShowReadMore(true);
    }
    if (expand) {
      setIsExpanded(true);
    }
  }, [maxHeight, expand]);

  const handleReadMoreClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <Stack flex={1}>
      <Stack
        ref={contentRef}
        className={isFormatted ? "editor-content" : ""}
        sx={{
          maxHeight: isExpanded ? "none" : `${maxHeight}px`,
          overflowX: "scroll",
          padding: 0,
        }}
      >
        {renderTypography}
      </Stack>
      {showReadMore && (
        <Link
          fontSize={BCDesignTokens.typographyFontSizeSmallBody}
          underline="hover"
          sx={{ cursor: "pointer" }}
          onClick={handleReadMoreClick}
        >
          {isExpanded ? "Read Less" : "Read More"}
        </Link>
      )}
    </Stack>
  );
}
