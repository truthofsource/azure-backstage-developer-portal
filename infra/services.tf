# Selected VM profile from the services-group definition; managed alternatives omitted.
resource "azurerm_resource_group" "backstage_services" {
  count    = var.enable_low_cost_vm ? 1 : 0
  name     = "rg-example-hub-backstage-eastus2-001"
  location = var.location
  tags     = merge(var.tags, { environment = "hub", workload = "backstage", managed_by = "terraform", data_class = "internal" })
}
