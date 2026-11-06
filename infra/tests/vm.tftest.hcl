mock_provider "azurerm" {}
mock_provider "azapi" {}
variables { subscription_id = "00000000-0000-4000-8000-000000000001" }
run "disabled_default" {
  command = plan
  assert {
    condition     = length(azurerm_linux_virtual_machine.backstage) == 0 && length(azurerm_virtual_network.backstage) == 0
    error_message = "The portfolio must not create a VM/network by default."
  }
}
run "selected_vm_profile" {
  command = plan
  variables {
    enabled                           = true
    enable_low_cost_vm                = true
    backstage_vm_admin_ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// reference-only-no-private-key"
    acr_id                            = "/subscriptions/00000000-0000-4000-8000-000000000001/resourceGroups/rg-example-hub-registry-eastus2-001/providers/Microsoft.ContainerRegistry/registries/examplehubregistry001"
    acr_login_server                  = "examplehubregistry001.azurecr.io"
  }
  assert {
    condition     = azurerm_linux_virtual_machine.backstage[0].disable_password_authentication && azurerm_linux_virtual_machine.backstage[0].size == "Standard_D2als_v6"
    error_message = "Preserve the selected key-only VM profile."
  }
  assert {
    condition     = azurerm_role_assignment.backstage_vm_repository_reader[0].condition_version == "2.0"
    error_message = "Registry access must retain the repository condition."
  }
  assert {
    condition     = azurerm_dev_test_global_vm_shutdown_schedule.backstage[0].enabled
    error_message = "Keep the shutdown safety net."
  }
}
