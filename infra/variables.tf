variable "subscription_id" {
  description = "Hub subscription ID; supplied outside this repository."
  type        = string
}

variable "enabled" {
  description = "Keep the adopted hub network managed. Set false only with an explicitly reviewed network decommission plan. Paid app/database resources remain out of scope."
  type        = bool
  default     = false
}

variable "enable_app" {
  description = "Start the interactive app only after Entra, GitHub App, image, DNS and Key Vault inputs are accepted."
  type        = bool
  default     = false
}

variable "enable_postgres" {
  description = "Create the paid private Backstage PostgreSQL server only after sizing and backup review."
  type        = bool
  default     = false
}

variable "enable_techdocs_storage" {
  description = "Create the private technical TechDocs account and endpoint after publisher access is designed."
  type        = bool
  default     = false
}

variable "enable_container_environment" {
  description = "Create a paid Container Apps environment only after ingress and reachability are selected."
  type        = bool
  default     = false
}

variable "enable_low_cost_vm" {
  description = "Prepare the paid single-VM Backstage pilot only after the operating schedule, Entra edge, backups and restore test are reviewed."
  type        = bool
  default     = false
}

variable "backstage_vm_admin_ssh_public_key" {
  description = "Public SSH key for emergency VM administration through Azure Run Command; port 22 is not exposed."
  type        = string
  default     = null
}

variable "backstage_vm_shutdown_time" {
  description = "Daily local-time automatic shutdown for the on-demand Backstage VM (HHMM). It does not automatically start the VM or cap monthly spending."
  type        = string
  default     = "2000"

  validation {
    condition     = can(regex("^([01][0-9]|2[0-3])[0-5][0-9]$", var.backstage_vm_shutdown_time))
    error_message = "Use a four-digit 24-hour shutdown time such as 2000."
  }
}

variable "enable_low_cost_vm_backup" {
  description = "Create a VM-scoped Blob destination for database-aware dumps after backup/restore scripts and cost are reviewed."
  type        = bool
  default     = false

  validation {
    condition     = !var.enable_low_cost_vm_backup || var.enable_low_cost_vm
    error_message = "The VM backup destination requires the low-cost VM switch."
  }
}

variable "backstage_vm_backup_storage_account_name" {
  description = "Globally unique Standard LRS account name for encrypted off-host Backstage database dumps."
  type        = string
  default     = null
}

variable "enable_backstage_vault" {
  description = "Create the dedicated Backstage Key Vault and private endpoint after access and DNS review. Does not enable the app."
  type        = bool
  default     = false
}

variable "backstage_vault_name" {
  description = "Globally unique Backstage-only Key Vault name."
  type        = string
  default     = "kv-example-hub-backstage-001"
}

variable "backstage_vault_admin_group_object_id" {
  description = "Reviewed Entra group object ID for Backstage vault administration; required when enabling the vault."
  type        = string
  default     = null
}

variable "location" {
  type    = string
  default = "eastus2"
}

variable "storage_account_name" {
  description = "Globally unique private account for technical TechDocs only."
  type        = string
  default     = null
}

variable "postgres_server_name" {
  description = "Globally unique PostgreSQL Flexible Server name."
  type        = string
  default     = null
}

variable "postgres_admin_password" {
  description = "Database bootstrap password; held in protected Terraform state and separately entered into Key Vault."
  type        = string
  sensitive   = true
  default     = null
}

variable "log_analytics_workspace_id" {
  description = "Existing hub operational workspace ID; do not create a duplicate."
  type        = string
  default     = null
}

variable "acr_id" {
  description = "Reviewed existing Azure Container Registry resource ID."
  type        = string
  default     = null
}

variable "acr_login_server" {
  description = "Login server corresponding to acr_id."
  type        = string
  default     = null
}

variable "image_digest" {
  description = "Exact immutable ACR image reference (repository@sha256:...)."
  type        = string
  default     = null
}

variable "base_url" {
  description = "Accepted HTTPS Backstage URL and Entra redirect origin."
  type        = string
  default     = null
}

variable "entra_tenant_id" {
  type    = string
  default = null
}

variable "entra_client_id" {
  type    = string
  default = null
}

variable "catalog_url" {
  description = "Reviewed merged GitHub URL for the technical catalog Location."
  type        = string
  default     = null
}

variable "engineer_roster_url" {
  description = "Private reviewed GitHub URL for exact Entra-object-ID User entities."
  type        = string
  default     = null
}

variable "engineer_user_refs" {
  description = "Exact allowed Backstage User refs, for example user:default/example; not email matching."
  type        = string
  default     = null
}

variable "github_app_id" {
  type    = string
  default = null
}

variable "github_app_client_id" {
  type    = string
  default = null
}

variable "key_vault_id" {
  description = "Reviewed Backstage Key Vault ID for the later app deployment; use the dedicated vault output when commissioned."
  type        = string
  default     = null
}

variable "key_vault_secret_ids" {
  description = "Versionless Key Vault IDs keyed by entra-client-secret, postgres-password, github-app-client-secret, github-app-private-key and github-app-webhook-secret."
  type        = map(string)
  default     = {}
}

variable "tags" {
  type    = map(string)
  default = {}
}
