import useMediaQuery from "@mui/material/useMediaQuery";
import { MQ } from "@/styles/responsive";

type ResponsiveCaps = {
  mdToLgMax?: string;   // cap width within 768–1199.95px
};

const parsePx = (value: string): number | null => {
  const match = /^\s*(\d+(?:\.\d+)?)px\s*$/.exec(value);
  return match ? Number(match[1]) : null;
};

const clampPx = (basePx: string, capPx: string): string => {
  const base = parsePx(basePx);
  const cap = parsePx(capPx);
  if (base == null || cap == null) return basePx;
  return `${Math.min(base, cap)}px`;
};

function useResponsiveDrawerWidth(
  defaultWidth: string,
  caps?: ResponsiveCaps
): string {
  const isMdToLg = useMediaQuery(MQ.mdToLg);

  if (isMdToLg && caps?.mdToLgMax) {
    return clampPx(defaultWidth, caps.mdToLgMax);
  }
  return defaultWidth;
}

export default useResponsiveDrawerWidth;


