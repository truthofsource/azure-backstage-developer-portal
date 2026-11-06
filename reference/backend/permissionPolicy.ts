import { createBackendModule } from '@backstage/backend-plugin-api';
import { AuthorizeResult, PolicyDecision, isPermission } from '@backstage/plugin-permission-common';
import { PermissionPolicy, PolicyQuery, PolicyQueryUser } from '@backstage/plugin-permission-node';
import { policyExtensionPoint } from '@backstage/plugin-permission-node/alpha';
import { actionExecutePermission, taskCreatePermission, taskCancelPermission, taskReadPermission, templateDryRunPermission } from '@backstage/plugin-scaffolder-common/alpha';
import { createScaffolderActionConditionalDecision, createScaffolderTaskConditionalDecision, scaffolderActionConditions, scaffolderTaskConditions } from '@backstage/plugin-scaffolder-backend/alpha';

export class ReadOnlyEngineeringPolicy implements PermissionPolicy {
  async handle(request: PolicyQuery, user?: PolicyQueryUser): Promise<PolicyDecision> {
    const hosted = process.env.BACKSTAGE_HOSTED_ENABLE === 'true';
    const allowedRefs = new Set((process.env.BACKSTAGE_ENGINEER_USER_REFS ?? '')
      .split(',').map(value => value.trim().toLowerCase()).filter(Boolean));
    const authorized = !hosted || (user !== undefined &&
      allowedRefs.has(user.info.userEntityRef.toLowerCase()));
    const maintainer = authorized && user !== undefined && process.env.BACKSTAGE_TEMPLATES_ENABLED === 'true' &&
      (process.env.BACKSTAGE_TEMPLATE_MAINTAINERS ?? '').split(',').map(value=>value.trim().toLowerCase())
        .includes(user.info.userEntityRef.toLowerCase());
    if (isPermission(request.permission, actionExecutePermission)) {
      if (!maintainer) return {result:AuthorizeResult.DENY};
      return createScaffolderActionConditionalDecision(request.permission,{anyOf:[
        scaffolderActionConditions.hasActionId({actionId:'workforce:render-node-worker'}),
        scaffolderActionConditions.hasActionId({actionId:'workforce:publish-component-pr'}),
      ]});
    }
    if (isPermission(request.permission, taskReadPermission) || isPermission(request.permission, taskCancelPermission)) {
      if (!maintainer) return {result:AuthorizeResult.DENY};
      return createScaffolderTaskConditionalDecision(request.permission,
        scaffolderTaskConditions.isTaskOwner({createdBy:[user!.info.userEntityRef]}));
    }
    if (isPermission(request.permission, taskCreatePermission) || isPermission(request.permission, templateDryRunPermission)) {
      return {result:maintainer?AuthorizeResult.ALLOW:AuthorizeResult.DENY};
    }
    // Catalog writes and all unclassified permissions still fail closed.
    return {
      result: authorized && request.permission.attributes.action === 'read'
        ? AuthorizeResult.ALLOW
        : AuthorizeResult.DENY,
    };
  }
}

export default createBackendModule({
  pluginId: 'permission',
  moduleId: 'workforce-read-only-policy',
  register(reg) {
    reg.registerInit({
      deps: { policy: policyExtensionPoint },
      async init({ policy }) {
        policy.setPolicy(new ReadOnlyEngineeringPolicy());
      },
    });
  },
});
