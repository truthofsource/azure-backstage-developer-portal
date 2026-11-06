import { createBackend } from '@backstage/backend-defaults';
import { basename } from 'node:path';
import permissionPolicy from './permissionPolicy';
import releasePlugin from './releases/plugin';
import templateModule from './templates/module';

const local = process.env.BACKSTAGE_LOCAL_EVALUATION === 'true';
const hosted = process.env.BACKSTAGE_HOSTED_ENABLE === 'true';
if (local === hosted) {
  throw new Error('Select exactly one Backstage runtime mode');
}
if (hosted) {
  const hostedProfile = process.env.BACKSTAGE_HOSTED_PROFILE;
  if (hostedProfile !== 'vm' && hostedProfile !== 'managed') {
    throw new Error('Hosted Backstage requires an explicit vm or managed profile');
  }
  const overlay = hostedProfile === 'vm' ? 'app-config.vm.yaml' : 'app-config.azure-managed.yaml';
  if (!process.argv.some(arg => basename(arg) === overlay)) {
    throw new Error(`Hosted Backstage profile ${hostedProfile} requires ${overlay}`);
  }
  const required = [
    'BACKSTAGE_BASE_URL', 'BACKSTAGE_POSTGRES_HOST', 'BACKSTAGE_POSTGRES_USER',
    'BACKSTAGE_POSTGRES_PASSWORD', 'BACKSTAGE_ENTRA_CLIENT_ID',
    'BACKSTAGE_ENTRA_CLIENT_SECRET', 'BACKSTAGE_ENTRA_TENANT_ID',
    'BACKSTAGE_CATALOG_URL',
    'BACKSTAGE_ENGINEER_USER_REFS', 'BACKSTAGE_GITHUB_APP_ID',
    'BACKSTAGE_GITHUB_APP_CLIENT_ID', 'BACKSTAGE_GITHUB_APP_CLIENT_SECRET',
    'BACKSTAGE_GITHUB_APP_PRIVATE_KEY', 'BACKSTAGE_GITHUB_APP_WEBHOOK_SECRET',
  ];
  if (hostedProfile === 'managed') required.push('BACKSTAGE_TECHDOCS_STORAGE_ACCOUNT', 'BACKSTAGE_ENGINEER_ROSTER_URL');
  const missing = required.filter(name => !process.env[name]?.trim());
  if (missing.length) {
    throw new Error(`Hosted Backstage configuration missing: ${missing.join(', ')}`);
  }
  if (process.env.NODE_ENV !== 'production' ||
      !process.env.BACKSTAGE_BASE_URL?.startsWith('https://')) {
    throw new Error('Hosted Backstage requires production mode and an HTTPS base URL');
  }
}

const backend = createBackend();
backend.add(import('@backstage/plugin-app-backend'));
backend.add(import('@backstage/plugin-auth-backend'));
if (local) {
  backend.add(import('@backstage/plugin-auth-backend-module-guest-provider'));
} else {
  backend.add(import('@backstage/plugin-auth-backend-module-microsoft-provider'));
}
backend.add(import('@backstage/plugin-catalog-backend'));
backend.add(import('@backstage/plugin-catalog-backend-module-logs'));
backend.add(import('@backstage/plugin-catalog-backend-module-scaffolder-entity-model'));
backend.add(import('@backstage/plugin-techdocs-backend'));
backend.add(import('@backstage/plugin-search-backend'));
// The local pilot uses Lunr. A hosted instance uses persistent PostgreSQL
// search while retaining the same catalog and TechDocs collators.
if (hosted) {
  backend.add(import('@backstage/plugin-search-backend-module-pg'));
}
backend.add(import('@backstage/plugin-search-backend-module-catalog'));
backend.add(import('@backstage/plugin-search-backend-module-techdocs'));
backend.add(import('@backstage/plugin-permission-backend'));
backend.add(permissionPolicy);
backend.add(releasePlugin);
if (process.env.BACKSTAGE_TEMPLATES_ENABLED === 'true') {
  backend.add(import('@backstage/plugin-scaffolder-backend'));
  backend.add(templateModule);
}
backend.add(import('@backstage/plugin-user-settings-backend'));
backend.start();
