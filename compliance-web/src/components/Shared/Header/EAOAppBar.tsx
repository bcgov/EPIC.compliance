import {
  AppBar as MuiAppBar,
  AppBarProps as MuiAppBarProps,
  Box,
  Button,
  Grid,
  styled,
  Typography,
  Avatar,
  useTheme,
} from "@mui/material";
import BC_Logo from "@/assets/images/bcgovLogoWhite.svg";
import { AppConfig } from "@/utils/config";
import { useAuth } from "react-oidc-context";
import EnvironmentBanner from "./EnvironmentBanner";
import { forwardRef, HTMLProps, useState } from "react";
import UserProfileMenu from "./UserProfileMenu";

type EAOAppBarProps = HTMLProps<HTMLDivElement>;
interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== "open",
})<AppBarProps>(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(["width", "margin"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
}));

const EAOAppBar = forwardRef<HTMLDivElement, EAOAppBarProps>((_props, ref) => {
  const theme = useTheme();
  const auth = useAuth();

  const [profileMenuAnchorEl, setProfileMenuAnchorEl] =
    useState<null | HTMLElement>(null);

  const handleOpenProfileMenu = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchorEl(event.currentTarget);
  };

  const handleCloseProfileMenu = () => {
    setProfileMenuAnchorEl(null);
  };

  const userInitials = `${auth.user?.profile?.given_name?.charAt(0)}${auth.user?.profile?.family_name?.charAt(0)}`;
  
  return (
    <>
      <AppBar ref={ref} position="static" color="primary" open={true}>
        <Grid
          container
          padding={"0.938rem 1.5rem"}
          margin={0}
          height={72}
          justifyContent="space-between"
        >
          <Grid display="flex" justifyContent="start" alignItems="center">
            <img src={BC_Logo} height={42} />
            <Typography
              variant="h3"
              color="inherit"
              paddingLeft={"2.5rem"}
              fontWeight={"bold"}
            >
              {AppConfig.appTitle}
            </Typography>
          </Grid>
          <Grid
            display="flex"
            justifyContent="center"
            alignItems="center"
            paddingRight={"0.75rem"}
          >
            {auth.isAuthenticated ? (
              <Box
                display={"flex"}
                alignItems={"center"}
                sx={{ cursor: "pointer" }}
                onClick={handleOpenProfileMenu}
              >
                <Typography variant="h6" color="inherit" marginRight={"1rem"}>
                  Hello, {auth.user?.profile.given_name}
                </Typography>
                <Avatar
                  sx={{
                    bgcolor: theme.palette.background.default,
                    width: "2rem",
                    height: "2rem",
                  }}
                >
                  <Typography
                    variant="body1"
                    fontWeight={700}
                    color={theme.palette.primary.main}
                    aria-label="user-initials"
                  >{userInitials}</Typography>
                </Avatar>
              </Box>
            ) : (
              <Button
                variant="outlined"
                color="inherit"
                onClick={() => auth.signinRedirect({ extraQueryParams: { kc_idp_hint: "idir" } })}
              >
                Sign In
              </Button>
            )}
          </Grid>
        </Grid>
        <UserProfileMenu
          anchorEl={profileMenuAnchorEl}
          handleClose={handleCloseProfileMenu}
        />
        <EnvironmentBanner />
      </AppBar>
    </>
  );
});

export default EAOAppBar;
