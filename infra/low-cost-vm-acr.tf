# Optional VM identity pull access. The live hub registry is owned by the
# separate hub-registry state; this root only assigns the VM's principal.
locals {
  backstage_vm_acr_id           = "/subscriptions/${var.subscription_id}/resourceGroups/rg-example-hub-registry-eastus2-001/providers/Microsoft.ContainerRegistry/registries/examplehubregistry001"
  backstage_vm_reader_condition = <<-CONDITION
    (
      (
        !(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/content/read'})
        AND !(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/metadata/read'})
      )
      OR
      (@Request[Microsoft.ContainerRegistry/registries/repositories:name] StringEqualsIgnoreCase 'backstage/portal')
    )
  CONDITION
}

resource "azurerm_role_assignment" "backstage_vm_repository_reader" {
  count                = var.enable_low_cost_vm ? 1 : 0
  scope                = var.acr_id
  role_definition_name = "Container Registry Repository Reader"
  principal_id         = azurerm_linux_virtual_machine.backstage[0].identity[0].principal_id
  principal_type       = "ServicePrincipal"
  condition            = local.backstage_vm_reader_condition
  condition_version    = "2.0"

  lifecycle {
    precondition {
      condition = (var.enabled &&
        try(lower(var.acr_id), "") == lower(local.backstage_vm_acr_id) &&
      try(lower(var.acr_login_server), "") == "examplehubregistry001.azurecr.io")
      error_message = "Use the reviewed hub Basic ACR ID and login server before granting the VM repository access."
    }
  }
}
