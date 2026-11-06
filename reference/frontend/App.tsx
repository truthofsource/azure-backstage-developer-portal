import { createApp } from '@backstage/frontend-defaults';
import catalogPlugin from '@backstage/plugin-catalog/alpha';
import { SignInPage } from '@backstage/core-components';
import { configApiRef, microsoftAuthApiRef, useApi } from '@backstage/core-plugin-api';
import { SignInPageBlueprint } from '@backstage/plugin-app-react';
import { createFrontendModule } from '@backstage/frontend-plugin-api';
import { navModule } from './modules/nav';
import { homeModule } from './modules/home';
import { operationsPlugin } from './modules/operations';
import { releasesPlugin } from './modules/releases';

const signInPage = SignInPageBlueprint.make({
  params: {
    loader: async () => props => {
      const config = useApi(configApiRef);
      const local = config.getOptionalString('auth.environment') === 'development';
      return (
        <SignInPage
          {...props}
          providers={local ? ['guest'] : [{
            id: 'microsoft-auth-provider',
            title: 'Microsoft',
            message: 'Sign in with your approved engineering account',
            apiRef: microsoftAuthApiRef,
          }]}
        />
      );
    },
  },
});

export default createApp({
  features: [catalogPlugin, navModule, homeModule, operationsPlugin, releasesPlugin,
    createFrontendModule({ pluginId: 'app', extensions: [signInPage] })],
});
