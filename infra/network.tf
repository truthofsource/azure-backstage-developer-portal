locals {
  network_tags = merge(var.tags, {
    environment = "hub"
    workload    = "hub-network"
    managed_by  = "terraform"
    data_class  = "internal"
  })
}

resource "azurerm_resource_group" "backstage" {
  count    = var.enabled ? 1 : 0
  name     = "rg-example-hub-network-eastus2-001"
  location = var.location
  tags     = local.network_tags
}

resource "azurerm_virtual_network" "backstage" {
  count               = var.enabled ? 1 : 0
  name                = "vnet-example-hub-eastus2-001"
  location            = azurerm_resource_group.backstage[0].location
  resource_group_name = azurerm_resource_group.backstage[0].name
  address_space       = ["10.50.0.0/20"]
  tags                = local.network_tags
}

resource "azurerm_subnet" "container_apps" {
  count                = var.enabled ? 1 : 0
  name                 = "snet-backstage-container-apps"
  resource_group_name  = azurerm_resource_group.backstage[0].name
  virtual_network_name = azurerm_virtual_network.backstage[0].name
  address_prefixes     = ["10.50.0.0/23"]

  delegation {
    name = "container-apps-environments"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "postgres" {
  count                = var.enabled ? 1 : 0
  name                 = "snet-backstage-postgres"
  resource_group_name  = azurerm_resource_group.backstage[0].name
  virtual_network_name = azurerm_virtual_network.backstage[0].name
  address_prefixes     = ["10.50.2.0/27"]

  delegation {
    name = "0"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "private_endpoints" {
  count                = var.enabled ? 1 : 0
  name                 = "snet-backstage-private-endpoints"
  resource_group_name  = azurerm_resource_group.backstage[0].name
  virtual_network_name = azurerm_virtual_network.backstage[0].name
  address_prefixes     = ["10.50.2.32/27"]
}
