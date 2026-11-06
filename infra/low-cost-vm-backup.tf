# Destination only. No backup is scheduled or claimed until a PostgreSQL dump,
# off-host upload, retention check and restore rehearsal have succeeded.
resource "azurerm_storage_account" "backstage_vm_backup" {
  count                           = var.enable_low_cost_vm_backup ? 1 : 0
  name                            = var.backstage_vm_backup_storage_account_name
  resource_group_name             = azurerm_resource_group.backstage_services[0].name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  shared_access_key_enabled       = false
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = true
  tags                            = var.tags

  network_rules {
    default_action             = "Deny"
    bypass                     = ["None"]
    virtual_network_subnet_ids = [azurerm_subnet.backstage_vm[0].id]
  }

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 14
    }

    container_delete_retention_policy {
      days = 14
    }
  }

  lifecycle {
    precondition {
      condition     = var.enabled && try(length(var.backstage_vm_backup_storage_account_name), 0) >= 3
      error_message = "Provide a reviewed globally unique backup account name before enabling the backup destination."
    }
  }
}

resource "azapi_resource" "backstage_vm_backup_container" {
  count     = var.enable_low_cost_vm_backup ? 1 : 0
  type      = "Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01"
  name      = "database-backups"
  parent_id = "${azurerm_storage_account.backstage_vm_backup[0].id}/blobServices/default"

  body = {
    properties = {
      publicAccess = "None"
      metadata = {
        purpose    = "backstage-database-recovery"
        data_class = "internal"
      }
    }
  }
}

resource "azurerm_role_assignment" "backstage_vm_backup_writer" {
  count                = var.enable_low_cost_vm_backup ? 1 : 0
  scope                = azapi_resource.backstage_vm_backup_container[0].id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_virtual_machine.backstage[0].identity[0].principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_storage_management_policy" "backstage_vm_backup" {
  count              = var.enable_low_cost_vm_backup ? 1 : 0
  storage_account_id = azurerm_storage_account.backstage_vm_backup[0].id

  rule {
    name    = "expire-backstage-dumps"
    enabled = true

    filters {
      prefix_match = ["database-backups/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        delete_after_days_since_modification_greater_than = 90
      }
      version {
        delete_after_days_since_creation = 14
      }
    }
  }
}
