package multi_tenant_vault

deny[msg] {
  vault_ns := data.vault.namespace[input.review.namespace]
  input.review.userInfo.namespace != vault_ns
  msg := "Vault tenant mismatch"
}
