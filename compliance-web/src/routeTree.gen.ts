/* prettier-ignore-start */

/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file is auto-generated by TanStack Router

import { createFileRoute } from '@tanstack/react-router'

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as OidcCallbackImport } from './routes/oidc-callback'
import { Route as AuthenticatedImport } from './routes/_authenticated'
import { Route as IndexImport } from './routes/index'
import { Route as EaoPlansIndexImport } from './routes/eao-plans/index'
import { Route as EaoPlansPlanIdImport } from './routes/eao-plans/$planId'
import { Route as AuthenticatedProfileImport } from './routes/_authenticated/profile'
import { Route as AuthenticatedIrBoardImport } from './routes/_authenticated/ir-board'
import { Route as AuthenticatedUsersIndexImport } from './routes/_authenticated/users/index'
import { Route as AuthenticatedCeDatabaseInspectionImport } from './routes/_authenticated/ce-database/inspection'
import { Route as AuthenticatedCeDatabaseCompliantsImport } from './routes/_authenticated/ce-database/compliants'
import { Route as AuthenticatedCeDatabaseCaseFilesImport } from './routes/_authenticated/ce-database/case-files'
import { Route as AuthenticatedAdminTopicsImport } from './routes/_authenticated/admin/topics'
import { Route as AuthenticatedAdminStaffImport } from './routes/_authenticated/admin/staff'
import { Route as AuthenticatedAdminProponentsImport } from './routes/_authenticated/admin/proponents'
import { Route as AuthenticatedAdminAgenciesImport } from './routes/_authenticated/admin/agencies'

// Create Virtual Routes

const NewpageLazyImport = createFileRoute('/newpage')()
const AboutLazyImport = createFileRoute('/about')()

// Create/Update Routes

const NewpageLazyRoute = NewpageLazyImport.update({
  path: '/newpage',
  getParentRoute: () => rootRoute,
} as any).lazy(() => import('./routes/newpage.lazy').then((d) => d.Route))

const AboutLazyRoute = AboutLazyImport.update({
  path: '/about',
  getParentRoute: () => rootRoute,
} as any).lazy(() => import('./routes/about.lazy').then((d) => d.Route))

const OidcCallbackRoute = OidcCallbackImport.update({
  path: '/oidc-callback',
  getParentRoute: () => rootRoute,
} as any)

const AuthenticatedRoute = AuthenticatedImport.update({
  id: '/_authenticated',
  getParentRoute: () => rootRoute,
} as any)

const IndexRoute = IndexImport.update({
  path: '/',
  getParentRoute: () => rootRoute,
} as any)

const EaoPlansIndexRoute = EaoPlansIndexImport.update({
  path: '/eao-plans/',
  getParentRoute: () => rootRoute,
} as any)

const EaoPlansPlanIdRoute = EaoPlansPlanIdImport.update({
  path: '/eao-plans/$planId',
  getParentRoute: () => rootRoute,
} as any)

const AuthenticatedProfileRoute = AuthenticatedProfileImport.update({
  path: '/profile',
  getParentRoute: () => AuthenticatedRoute,
} as any)

const AuthenticatedIrBoardRoute = AuthenticatedIrBoardImport.update({
  path: '/ir-board',
  getParentRoute: () => AuthenticatedRoute,
} as any)

const AuthenticatedUsersIndexRoute = AuthenticatedUsersIndexImport.update({
  path: '/users/',
  getParentRoute: () => AuthenticatedRoute,
} as any)

const AuthenticatedCeDatabaseInspectionRoute =
  AuthenticatedCeDatabaseInspectionImport.update({
    path: '/ce-database/inspection',
    getParentRoute: () => AuthenticatedRoute,
  } as any)

const AuthenticatedCeDatabaseCompliantsRoute =
  AuthenticatedCeDatabaseCompliantsImport.update({
    path: '/ce-database/compliants',
    getParentRoute: () => AuthenticatedRoute,
  } as any)

const AuthenticatedCeDatabaseCaseFilesRoute =
  AuthenticatedCeDatabaseCaseFilesImport.update({
    path: '/ce-database/case-files',
    getParentRoute: () => AuthenticatedRoute,
  } as any)

const AuthenticatedAdminTopicsRoute = AuthenticatedAdminTopicsImport.update({
  path: '/admin/topics',
  getParentRoute: () => AuthenticatedRoute,
} as any)

const AuthenticatedAdminStaffRoute = AuthenticatedAdminStaffImport.update({
  path: '/admin/staff',
  getParentRoute: () => AuthenticatedRoute,
} as any)

const AuthenticatedAdminProponentsRoute =
  AuthenticatedAdminProponentsImport.update({
    path: '/admin/proponents',
    getParentRoute: () => AuthenticatedRoute,
  } as any)

const AuthenticatedAdminAgenciesRoute = AuthenticatedAdminAgenciesImport.update(
  {
    path: '/admin/agencies',
    getParentRoute: () => AuthenticatedRoute,
  } as any,
)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexImport
      parentRoute: typeof rootRoute
    }
    '/_authenticated': {
      id: '/_authenticated'
      path: ''
      fullPath: ''
      preLoaderRoute: typeof AuthenticatedImport
      parentRoute: typeof rootRoute
    }
    '/oidc-callback': {
      id: '/oidc-callback'
      path: '/oidc-callback'
      fullPath: '/oidc-callback'
      preLoaderRoute: typeof OidcCallbackImport
      parentRoute: typeof rootRoute
    }
    '/about': {
      id: '/about'
      path: '/about'
      fullPath: '/about'
      preLoaderRoute: typeof AboutLazyImport
      parentRoute: typeof rootRoute
    }
    '/newpage': {
      id: '/newpage'
      path: '/newpage'
      fullPath: '/newpage'
      preLoaderRoute: typeof NewpageLazyImport
      parentRoute: typeof rootRoute
    }
    '/_authenticated/ir-board': {
      id: '/_authenticated/ir-board'
      path: '/ir-board'
      fullPath: '/ir-board'
      preLoaderRoute: typeof AuthenticatedIrBoardImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/profile': {
      id: '/_authenticated/profile'
      path: '/profile'
      fullPath: '/profile'
      preLoaderRoute: typeof AuthenticatedProfileImport
      parentRoute: typeof AuthenticatedImport
    }
    '/eao-plans/$planId': {
      id: '/eao-plans/$planId'
      path: '/eao-plans/$planId'
      fullPath: '/eao-plans/$planId'
      preLoaderRoute: typeof EaoPlansPlanIdImport
      parentRoute: typeof rootRoute
    }
    '/eao-plans/': {
      id: '/eao-plans/'
      path: '/eao-plans'
      fullPath: '/eao-plans'
      preLoaderRoute: typeof EaoPlansIndexImport
      parentRoute: typeof rootRoute
    }
    '/_authenticated/admin/agencies': {
      id: '/_authenticated/admin/agencies'
      path: '/admin/agencies'
      fullPath: '/admin/agencies'
      preLoaderRoute: typeof AuthenticatedAdminAgenciesImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/admin/proponents': {
      id: '/_authenticated/admin/proponents'
      path: '/admin/proponents'
      fullPath: '/admin/proponents'
      preLoaderRoute: typeof AuthenticatedAdminProponentsImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/admin/staff': {
      id: '/_authenticated/admin/staff'
      path: '/admin/staff'
      fullPath: '/admin/staff'
      preLoaderRoute: typeof AuthenticatedAdminStaffImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/admin/topics': {
      id: '/_authenticated/admin/topics'
      path: '/admin/topics'
      fullPath: '/admin/topics'
      preLoaderRoute: typeof AuthenticatedAdminTopicsImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/ce-database/case-files': {
      id: '/_authenticated/ce-database/case-files'
      path: '/ce-database/case-files'
      fullPath: '/ce-database/case-files'
      preLoaderRoute: typeof AuthenticatedCeDatabaseCaseFilesImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/ce-database/compliants': {
      id: '/_authenticated/ce-database/compliants'
      path: '/ce-database/compliants'
      fullPath: '/ce-database/compliants'
      preLoaderRoute: typeof AuthenticatedCeDatabaseCompliantsImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/ce-database/inspection': {
      id: '/_authenticated/ce-database/inspection'
      path: '/ce-database/inspection'
      fullPath: '/ce-database/inspection'
      preLoaderRoute: typeof AuthenticatedCeDatabaseInspectionImport
      parentRoute: typeof AuthenticatedImport
    }
    '/_authenticated/users/': {
      id: '/_authenticated/users/'
      path: '/users'
      fullPath: '/users'
      preLoaderRoute: typeof AuthenticatedUsersIndexImport
      parentRoute: typeof AuthenticatedImport
    }
  }
}

// Create and export the route tree

export const routeTree = rootRoute.addChildren({
  IndexRoute,
  AuthenticatedRoute: AuthenticatedRoute.addChildren({
    AuthenticatedIrBoardRoute,
    AuthenticatedProfileRoute,
    AuthenticatedAdminAgenciesRoute,
    AuthenticatedAdminProponentsRoute,
    AuthenticatedAdminStaffRoute,
    AuthenticatedAdminTopicsRoute,
    AuthenticatedCeDatabaseCaseFilesRoute,
    AuthenticatedCeDatabaseCompliantsRoute,
    AuthenticatedCeDatabaseInspectionRoute,
    AuthenticatedUsersIndexRoute,
  }),
  OidcCallbackRoute,
  AboutLazyRoute,
  NewpageLazyRoute,
  EaoPlansPlanIdRoute,
  EaoPlansIndexRoute,
})

/* prettier-ignore-end */

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/",
        "/_authenticated",
        "/oidc-callback",
        "/about",
        "/newpage",
        "/eao-plans/$planId",
        "/eao-plans/"
      ]
    },
    "/": {
      "filePath": "index.tsx"
    },
    "/_authenticated": {
      "filePath": "_authenticated.tsx",
      "children": [
        "/_authenticated/ir-board",
        "/_authenticated/profile",
        "/_authenticated/admin/agencies",
        "/_authenticated/admin/proponents",
        "/_authenticated/admin/staff",
        "/_authenticated/admin/topics",
        "/_authenticated/ce-database/case-files",
        "/_authenticated/ce-database/compliants",
        "/_authenticated/ce-database/inspection",
        "/_authenticated/users/"
      ]
    },
    "/oidc-callback": {
      "filePath": "oidc-callback.tsx"
    },
    "/about": {
      "filePath": "about.lazy.tsx"
    },
    "/newpage": {
      "filePath": "newpage.lazy.tsx"
    },
    "/_authenticated/ir-board": {
      "filePath": "_authenticated/ir-board.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/profile": {
      "filePath": "_authenticated/profile.tsx",
      "parent": "/_authenticated"
    },
    "/eao-plans/$planId": {
      "filePath": "eao-plans/$planId.tsx"
    },
    "/eao-plans/": {
      "filePath": "eao-plans/index.tsx"
    },
    "/_authenticated/admin/agencies": {
      "filePath": "_authenticated/admin/agencies.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/admin/proponents": {
      "filePath": "_authenticated/admin/proponents.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/admin/staff": {
      "filePath": "_authenticated/admin/staff.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/admin/topics": {
      "filePath": "_authenticated/admin/topics.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/ce-database/case-files": {
      "filePath": "_authenticated/ce-database/case-files.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/ce-database/compliants": {
      "filePath": "_authenticated/ce-database/compliants.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/ce-database/inspection": {
      "filePath": "_authenticated/ce-database/inspection.tsx",
      "parent": "/_authenticated"
    },
    "/_authenticated/users/": {
      "filePath": "_authenticated/users/index.tsx",
      "parent": "/_authenticated"
    }
  }
}
ROUTE_MANIFEST_END */
