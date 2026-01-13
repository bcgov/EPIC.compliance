/// <reference types="cypress" />
import { mount } from 'cypress/react';
import { ThemeProvider, CssBaseline } from "@mui/material";
import EAOAppBar from "@/components/Shared/Header/EAOAppBar";
import { AuthProvider } from "react-oidc-context";
import { createAppTheme } from "epic.theme";

const mockAuth = ({ user, isAuthenticated }) => ({
  user,
  isAuthenticated,
  signinRedirect: cy.stub().as('signinRedirect'),
  signoutRedirect: cy.stub().as('signoutRedirect'),
});

describe('EAOAppBar Component', () => {
  const MockedAuthProvider = ({ children, isAuthenticated }) => {
    const authContext = mockAuth({
      user: {
        profile: {
          given_name: "John",
          family_name: "Doe",
        },
      },
      isAuthenticated,
    });

    return (
      <AuthProvider {...authContext}>
        {children}
      </AuthProvider>
    );
  };

  const theme = createAppTheme();


  const mountComponent = (isAuthenticated = true) => {
    mount(
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <MockedAuthProvider isAuthenticated={isAuthenticated}>
          <EAOAppBar />
        </MockedAuthProvider>
      </ThemeProvider>
    );
  };

  it('should render the app bar with the mocked app title and logo', () => {
    mountComponent();

    cy.get('img').should('have.attr', 'src').and('include', 'bcgovLogoWhite.svg');
    // cy.get('h3').contains(mockAppConfig.appTitle).should('exist');
  });

  it('should display the Sign In button when not authenticated', () => {
    mountComponent(false);

    cy.get('button').contains('Sign In').should('exist');
  });
});
