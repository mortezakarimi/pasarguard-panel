export type ExtensionAdminPage = {
  path: string
  label: string
  permissions: string[]
}

export type ExtensionAdminUI = {
  label: string
  icon?: string | null
  pages: ExtensionAdminPage[]
  settings_schema?: Record<string, unknown> | null
}

export type ExtensionSubscriptionUI = {
  slots: string[]
}

export type ExtensionUIManifest = {
  admin?: ExtensionAdminUI | null
  subscription?: ExtensionSubscriptionUI | null
}

export type ExtensionInfo = {
  id: string
  name: string
  version: string
  description: string
  sdk_version: string
  permissions: string[]
  enabled: boolean
  ui: ExtensionUIManifest
}

export type ExtensionSettingsUpdate = {
  settings: Record<string, unknown>
}

export type ExtensionEnabledUpdate = {
  enabled: boolean
}
