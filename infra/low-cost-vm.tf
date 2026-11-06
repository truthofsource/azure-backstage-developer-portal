# Disabled cost-controlled pilot alternative. This provisions an empty Linux VM;
# it does not install Backstage, PostgreSQL, TLS, identity enforcement or backup.
# Never enable until those operational pieces and a monthly runtime schedule are reviewed.
resource "azurerm_subnet" "backstage_vm" {
  count                = var.enable_low_cost_vm ? 1 : 0
  name                 = "snet-backstage-vm"
  resource_group_name  = azurerm_resource_group.backstage[0].name
  virtual_network_name = azurerm_virtual_network.backstage[0].name
  address_prefixes     = ["10.50.2.64/27"]
  service_endpoints    = ["Microsoft.Storage"]
}

resource "azurerm_network_security_group" "backstage_vm" {
  count               = var.enable_low_cost_vm ? 1 : 0
  name                = "nsg-example-hub-backstage-vm-eastus2-001"
  location            = var.location
  resource_group_name = azurerm_resource_group.backstage_services[0].name
  tags                = var.tags

  security_rule {
    name                       = "https-in"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "backstage_vm" {
  count                     = var.enable_low_cost_vm ? 1 : 0
  subnet_id                 = azurerm_subnet.backstage_vm[0].id
  network_security_group_id = azurerm_network_security_group.backstage_vm[0].id
}

resource "azurerm_public_ip" "backstage_vm" {
  count               = var.enable_low_cost_vm ? 1 : 0
  name                = "pip-example-hub-backstage-vm-eastus2-001"
  location            = var.location
  resource_group_name = azurerm_resource_group.backstage_services[0].name
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = "example-backstage-eastus2-001"
  tags                = var.tags
}

resource "azurerm_network_interface" "backstage_vm" {
  count               = var.enable_low_cost_vm ? 1 : 0
  name                = "nic-example-hub-backstage-vm-eastus2-001"
  location            = var.location
  resource_group_name = azurerm_resource_group.backstage_services[0].name
  tags                = var.tags

  ip_configuration {
    name                          = "primary"
    subnet_id                     = azurerm_subnet.backstage_vm[0].id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.backstage_vm[0].id
  }
}

resource "azurerm_linux_virtual_machine" "backstage" {
  count                           = var.enable_low_cost_vm ? 1 : 0
  name                            = "vm-example-hub-backstage-eastus2-001"
  resource_group_name             = azurerm_resource_group.backstage_services[0].name
  location                        = var.location
  size                            = "Standard_D2als_v6"
  admin_username                  = "backstageadmin"
  disable_password_authentication = true
  custom_data                     = base64encode(replace(file("${path.module}/../runtime/vm/bootstrap-host.sh"), "\r\n", "\n"))
  network_interface_ids           = [azurerm_network_interface.backstage_vm[0].id]
  tags                            = var.tags

  admin_ssh_key {
    username   = "backstageadmin"
    public_key = var.backstage_vm_admin_ssh_public_key
  }

  identity {
    type = "SystemAssigned"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 32
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  lifecycle {
    precondition {
      condition     = var.enabled && try(length(trimspace(var.backstage_vm_admin_ssh_public_key)), 0) > 30
      error_message = "Keep the adopted network enabled and supply a reviewed SSH public key before creating the low-cost VM."
    }
  }
}

resource "azurerm_dev_test_global_vm_shutdown_schedule" "backstage" {
  count                 = var.enable_low_cost_vm ? 1 : 0
  virtual_machine_id    = azurerm_linux_virtual_machine.backstage[0].id
  location              = var.location
  enabled               = true
  daily_recurrence_time = var.backstage_vm_shutdown_time
  timezone              = "Central Standard Time"

  notification_settings {
    enabled = false
  }
}
