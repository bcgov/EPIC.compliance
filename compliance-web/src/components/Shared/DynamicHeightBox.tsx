import { MQ } from "@/styles/responsive";
import { Box, BoxProps } from "@mui/material";
import { useEffect, useState, useRef } from "react";

interface DynamicHeightBoxProps extends Omit<BoxProps, 'height'> {
  /**
   * Additional offset to subtract from the calculated height (in pixels)
   * @default 0
   */
  bottomOffset?: number;
  /**
   * Whether to include vertical padding (top + bottom) in the height calculation
   * @default true
   */
  includePadding?: boolean;
  /**
   * Custom height calculation function
   * Receives the top position and returns the calculated height
   */
  heightCalculator?: (topPosition: number) => string;
}

/**
 * A Box component that dynamically calculates its height based on its top position in the viewport.
 * Useful for components that need to fill the remaining viewport height from their current position.
 */
export default function DynamicHeightBox({
  bottomOffset = 0,
  includePadding = true,
  heightCalculator,
  children,
  sx,
  ...boxProps
}: DynamicHeightBoxProps) {
  const [componentTopPosition, setComponentTopPosition] = useState(0);
  const [actualPadding, setActualPadding] = useState(0);
  const componentRef = useRef<HTMLDivElement>(null);

  // Measure component position and padding
  useEffect(() => {
    const updatePosition = () => {
      if (componentRef.current) {
        const rect = componentRef.current.getBoundingClientRect();
        setComponentTopPosition(rect.top);
        
        // Calculate actual padding if includePadding is true
        if (includePadding) {
          const computedStyle = window.getComputedStyle(componentRef.current);
          let totalPadding = 0;
          
          if (includePadding) {
            const paddingTop = parseFloat(computedStyle.paddingTop) || 0;
            const paddingBottom = parseFloat(computedStyle.paddingBottom) || 0;
            totalPadding += paddingTop + paddingBottom;
          }
          
          setActualPadding(totalPadding);
        }
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    
    // Update position after a short delay to ensure layout is complete
    const timeoutId = setTimeout(updatePosition, 100);

    return () => {
      window.removeEventListener('resize', updatePosition);
      clearTimeout(timeoutId);
    };
  }, [includePadding]);

  // Calculate height
  const calculateHeight = () => {
    if (heightCalculator) {
      return heightCalculator(componentTopPosition);
    }
    
    const totalOffset = includePadding ? bottomOffset + actualPadding : bottomOffset;
    return `calc(100vh - ${componentTopPosition + totalOffset}px)`;
  };

  return (
    <Box
      ref={componentRef}
      sx={{
        height: calculateHeight(),
        [MQ.mdToLg]: {
          width: "auto",
          height: "auto",
        },
        ...sx,
      }}
      {...boxProps}
    >
      {children}
    </Box>
  );
}
