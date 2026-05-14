package vault_pennal

import data.vault.status

deny[msg] {
  not status == "valid"
  msg := "Vault lease expired for monkey troop"
}

# ExternalData fetch
external_data[status] {
  vault_response := data.vault.lease[input.pod.metadata.name]
  status := vault_response.status
}
