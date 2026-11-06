# Identity, admission and permission

**Terms used here:** A managed identity lets an Azure service request access without storing a password in the application.

An engineer encounters two complementary sign-in boundaries:

1. Caddy delegates ingress authentication to OAuth2 Proxy. Its Entra application checks the configured engineering group and establishes a Secure, SameSite=Lax host cookie. The source config sets one-hour refresh and eight-hour expiry; these are settings, not proof of a particular observed session lifetime.
2. Backstage's Microsoft provider uses a separate Entra application. The configured resolver matches the identity's object ID to a catalog User annotation. Hosted permission checks compare the resulting exact User entity ref with the approved engineer refs.

The hosted backend refuses missing required inputs or a mismatched runtime profile. Guest sign-in is available only in the explicit local evaluation branch. The public reference does not initialize either provider.

The read-oriented policy allows approved reads and denies catalog writes/actions without an explicit permission rule. Optional software-template execution requires the explicit switch, a listed maintainer, allowed action IDs and own-task conditions. The source supports rendering a technical component and publishing a component proposal; it is not blanket GitHub or Azure deployment authority. Writer credentials are separate from the ordinary reader App and absent from default Compose mounts.

| Identity | Purpose | Credential boundary |
| --- | --- | --- |
| Engineer | Interactive access to portal | Entra and protected session state |
| Ingress app | Admission/group gate | Dedicated mounted client/cookie secrets |
| Backstage app | Backend matching the signed-in person to a known account | Separate mounted client secret |
| Reader GitHub App | Catalog/source access | Restricted App key and installation scope |
| Optional writer App | Reviewed component proposals | Separate restricted key and maintainer rules |
| Azure VM managed identity | Registry reads and backup access | Azure-issued token, no storage account key |

Catalog groups document ownership; they do not create Entra groups. Protected rosters, keys, tokens and actual object IDs are absent from this repository. Full provider sign-in and permission-framework integration were not rerun for this portfolio.

[Backstage Microsoft provider documentation](https://backstage.io/docs/auth/microsoft/provider/) explains provider configuration and identity resolvers. [Permission framework](https://backstage.io/docs/permissions/overview/) describes the policy layer.
