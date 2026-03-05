import { useMemo } from "react";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useMenuStore } from "@/store/menuStore";
import { APP_SIDE_NAV_WIDTH, APP_SIDE_NAV_WIDTH_COLLAPSED } from "@/utils/constants";

/**
 * Hook that determines if a drawer is constrained (its default width exceeds available space).
 * Used to trigger responsive layout changes before the drawer hits its max-width constraint.
 * 
 * @param defaultWidth - The default/desired width of the drawer in pixels (e.g., "1240px")
 * @returns true if the drawer would exceed available viewport width, false otherwise
 */
function useIsDrawerConstrained(defaultWidth: string): boolean {
  const { expandMenu } = useMenuStore();
  const sideNavWidth = expandMenu ? APP_SIDE_NAV_WIDTH : APP_SIDE_NAV_WIDTH_COLLAPSED;

  // Parse the default width from string (e.g., "1240px" -> 1240)
  const parsedWidth = useMemo(() => {
    const match = /^\s*(\d+(?:\.\d+)?)px\s*$/.exec(defaultWidth);
    return match ? Number(match[1]) : 0;
  }, [defaultWidth]);

  // Calculate the threshold: drawer width + nav width + small buffer
  const threshold = useMemo(() => `${parsedWidth + sideNavWidth + 20}px`, [parsedWidth, sideNavWidth]);

  // Check if viewport width is less than threshold
  const isConstrained = useMediaQuery(`(max-width: ${threshold})`);

  return isConstrained;
}

export default useIsDrawerConstrained;
