module "relay_hybrid_connection" {
  count  = var.relay_namespace_name != null ? 1 : 0
  source = "../dtos-devops-templates/infrastructure/modules/relay-hybrid-connection"

  name                 = "hc-${var.app_short_name}-${var.environment}"
  relay_namespace_name = var.relay_namespace_name
  resource_group_name  = var.resource_group_name_infra

  authorization_rules = {
    "${var.app_short_name}-${var.environment}-listen-send" = {
      listen = true
      send   = true
    }
  }
}

module "relay_send_identity" {
  count               = var.relay_namespace_name != null ? 1 : 0
  source              = "../dtos-devops-templates/infrastructure/modules/managed-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.region
  uai_name            = "mi-${var.app_short_name}-${var.environment}-relay-send"
}

module "relay_send_role_assignment" {
  count                = var.relay_namespace_name != null ? 1 : 0
  source               = "../dtos-devops-templates/infrastructure/modules/rbac-assignment"
  principal_id         = module.relay_send_identity[0].principal_id
  role_definition_name = "Azure Relay Sender"
  scope                = var.relay_namespace_id
  depends_on           = [module.relay_send_identity]
}
