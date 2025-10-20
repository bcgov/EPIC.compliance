import { Link, Stack } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { useEffect, useRef, useState, useCallback } from "react";

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

  const checkContentHeight = useCallback(() => {
    if (contentRef.current) {
      const shouldShowReadMore = contentRef.current.scrollHeight > maxHeight + 20;
      setShowReadMore(shouldShowReadMore);
    }
  }, [maxHeight]);

  useEffect(() => {
    checkContentHeight();
    if (expand) {
      setIsExpanded(true);
    }
  }, [maxHeight, expand, checkContentHeight]);

  // Set up image load listeners to re-check content height when images load
  useEffect(() => {
    const contentElement = contentRef.current;
    if (!contentElement) return;

    const handleImageLoad = () => {
      // Use setTimeout to ensure the DOM has updated after image load
      setTimeout(checkContentHeight, 0);
    };

    // Find all images within the content
    const images = contentElement.querySelectorAll('img');
    
    // Add load event listeners to all images
    images.forEach(img => {
      if (img.complete) {
        // Image already loaded, check height immediately
        handleImageLoad();
      } else {
        // Image still loading, add event listener
        img.addEventListener('load', handleImageLoad);
        img.addEventListener('error', handleImageLoad); // Also handle errors
      }
    });

    // Cleanup function to remove event listeners
    return () => {
      images.forEach(img => {
        img.removeEventListener('load', handleImageLoad);
        img.removeEventListener('error', handleImageLoad);
      });
    };
  }, [renderTypography, checkContentHeight]);

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
