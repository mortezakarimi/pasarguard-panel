import { ExtensionIframe } from '@/features/extensions/components/extension-iframe'
import { useExtension, useSetExtensionEnabled } from '@/features/extensions/hooks/use-extensions'
import { useAdmin } from '@/hooks/use-admin'
import { hasPermission, isOwner } from '@/utils/rbac'
import { ArrowLeft } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { LoadingSpinner } from '@/components/common/loading-spinner'

type ExtensionHostProps = {
  extensionId: string
  pagePath?: string
}

export function ExtensionHost({ extensionId, pagePath = 'dashboard' }: ExtensionHostProps) {
  const { t } = useTranslation()
  const { admin } = useAdmin()
  const { data: extension, isLoading, isError } = useExtension(extensionId)
  const setEnabled = useSetExtensionEnabled(extensionId)
  const canManage = isOwner(admin) || hasPermission(admin, 'extensions', 'manage')

  if (isLoading) return <LoadingSpinner />
  if (isError || !extension) {
    return <p className="text-muted-foreground p-6">{t('extensions.notFound', { defaultValue: 'Extension not found.' })}</p>
  }

  const page = extension.ui.admin?.pages.find(p => p.path === pagePath) ?? extension.ui.admin?.pages[0]
  const pageLabel = page?.label ?? extension.name

  return (
    <div className="flex flex-col gap-4 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" size="icon">
            <Link to="/extensions" aria-label={t('extensions.back', { defaultValue: 'Back to extensions' })}>
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-semibold">{extension.name}</h1>
            <p className="text-muted-foreground text-sm">
              v{extension.version} · {pageLabel}
            </p>
          </div>
        </div>
        {canManage && isOwner(admin) && (
          <div className="flex items-center gap-2">
            <span className="text-sm">{t('extensions.enabled', { defaultValue: 'Enabled' })}</span>
            <Switch
              checked={extension.enabled}
              disabled={setEnabled.isPending}
              onCheckedChange={checked => setEnabled.mutate({ enabled: checked })}
            />
          </div>
        )}
      </div>
      <ExtensionIframe extensionId={extensionId} pagePath={page?.path ?? pagePath} title={pageLabel} />
    </div>
  )
}
