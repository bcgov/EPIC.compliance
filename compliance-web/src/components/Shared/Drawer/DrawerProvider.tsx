import React from "react";
import { Box, Drawer } from "@mui/material";
import { useDrawer } from "@/store/drawerStore";
import { useMenuStore } from "@/store/menuStore";
import { BCDesignTokens } from "epic.theme";
import { APP_SIDE_NAV_WIDTH, APP_SIDE_NAV_WIDTH_COLLAPSED } from "@/utils/constants";

const DrawerProvider: React.FC = () => {
  const { drawerContent, setClose, isOpen, drawerWidth } = useDrawer();
  const { appHeaderHeight, expandMenu } = useMenuStore();
  const sideNavWidth = expandMenu ? APP_SIDE_NAV_WIDTH : APP_SIDE_NAV_WIDTH_COLLAPSED;

  return (
    <Drawer
      anchor={"right"}
      open={isOpen}
      onClose={setClose}
      variant="persistent"
      sx={{
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          boxSizing: "border-box",
          boxShadow: BCDesignTokens.surfaceShadowSmall,
          height: `calc(100vh - ${appHeaderHeight}px)`,
          top: appHeaderHeight,
          maxWidth: `calc(100vw - ${sideNavWidth}px)`,
          // Once at max-width, maintain it (prevents shrinking)
          minWidth: drawerWidth,
        },
      }}
    >
      <Box role="presentation" sx={{ width: drawerWidth }}>
        {drawerContent}
      </Box>
    </Drawer>
  );
};

export default DrawerProvider;
