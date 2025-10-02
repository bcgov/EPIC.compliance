import React from 'react';
import { createRouter, RouterProvider, createRoute, createRootRoute } from '@tanstack/react-router';

// Create a minimal root route for Storybook
const rootRoute = createRootRoute({
  component: () => React.createElement('div'),
});

// Create a simple route for Storybook
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => React.createElement('div'),
});

// Create a simple route tree for Storybook
const storybookRouteTree = rootRoute.addChildren([indexRoute]);

// Mock authentication context for Storybook
const mockAuth = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  signinRedirect: () => Promise.resolve(),
  signinSilent: () => Promise.resolve(),
  signinPopup: () => Promise.resolve(),
  signinResourceOwnerCredentials: () => Promise.resolve(),
  signoutRedirect: () => Promise.resolve(),
  signoutPopup: () => Promise.resolve(),
  signoutSilent: () => Promise.resolve(),
  removeUser: () => Promise.resolve(),
  clearStaleState: () => Promise.resolve(),
  queryUserInfo: () => Promise.resolve(),
  revokeAccessToken: () => Promise.resolve(),
  revokeRefreshToken: () => Promise.resolve(),
  events: {
    addAccessTokenExpiring: () => () => {},
    addAccessTokenExpired: () => () => {},
    addSilentRenewError: () => () => {},
    addUserLoaded: () => () => {},
    addUserUnloaded: () => () => {},
    addUserSignedIn: () => () => {},
    addUserSignedOut: () => () => {},
    addUserSessionChanged: () => () => {},
    removeAccessTokenExpiring: () => {},
    removeAccessTokenExpired: () => {},
    removeSilentRenewError: () => {},
    removeUserLoaded: () => {},
    removeUserUnloaded: () => {},
    removeUserSignedIn: () => {},
    removeUserSignedOut: () => {},
    removeUserSessionChanged: () => {},
  },
} as any;

// Create a mock router for Storybook
const storybookRouter = createRouter({
  routeTree: storybookRouteTree,
  context: {
    authentication: mockAuth,
  },
});

// Note: We don't register the router type here to avoid conflicts with the main app's router types

export const RouterDecorator = (Story: React.ComponentType) => {
  return React.createElement(
    'div',
    { style: { padding: '20px' } },
    React.createElement(
      RouterProvider,
      { router: storybookRouter },
      React.createElement(Story)
    )
  );
};
