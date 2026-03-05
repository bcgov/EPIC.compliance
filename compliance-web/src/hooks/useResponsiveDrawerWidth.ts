import { useMenuStore } from "@/store/menuStore";
import { APP_SIDE_NAV_WIDTH, APP_SIDE_NAV_WIDTH_COLLAPSED } from "@/utils/constants";

/**
 * Hook that returns a drawer width that respects the side navigation width.
 * The drawer will never exceed the available viewport width.
 * 
 * @param defaultWidth - The default/desired width of the drawer (e.g., "1240px")
 * @returns A CSS value that ensures the drawer doesn't push the side nav off screen
 */
function useResponsiveDrawerWidth(defaultWidth: string): string {
  const { expandMenu } = useMenuStore();
  const sideNavWidth = expandMenu ? APP_SIDE_NAV_WIDTH : APP_SIDE_NAV_WIDTH_COLLAPSED;
  
  // Use CSS min() to dynamically cap the width based on available viewport space
  // This ensures the drawer never exceeds 100vw - navWidth
  return `min(${defaultWidth}, calc(100vw - ${sideNavWidth}px))`;
}

export default useResponsiveDrawerWidth;


