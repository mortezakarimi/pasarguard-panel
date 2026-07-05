import { useExtensions } from '@/features/extensions/hooks/use-extensions'
import { useAdmin } from '@/hooks/use-admin'
import { hasPermission, isOwner } from '@/utils/rbac'
import { Puzzle } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'
import { LoadingSpinner } from '@/components/common/loading-spinner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ExtensionsPage() {
  const { t } = useTranslation()
  const { admin } = useAdmin()
  const { data: extensions, isLoading, isError } = useExtensions()
  const canManage = isOwner(admin) || hasPermission(admin, 'extensions', 'manage')

  if (isLoading) return <LoadingSpinner />
  if (isError) {
    return <p className="text-muted-foreground p-6">{t('extensions.loadError', { defaultValue: 'Failed to load extensions.' })}</p>
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">{t('extensions.title', { defaultValue: 'Extensions' })}</h1>
        <p className="text-muted-foreground text-sm">
          {t('extensions.subtitle', { defaultValue: 'Manage installed PasarGuard extensions.' })}
        </p>
      </div>

      {!extensions?.length ? (
        <Card>
          <CardHeader>
            <CardTitle>{t('extensions.empty.title', { defaultValue: 'No extensions installed' })}</CardTitle>
            <CardDescription>
              {t('extensions.empty.description', {
                defaultValue: 'Install an extension package and add it to EXTENSIONS_ALLOWLIST in your .env file.',
              })}
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {extensions.map(extension => (
            <Card key={extension.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Puzzle className="h-5 w-5" />
                    <CardTitle className="text-lg">{extension.name}</CardTitle>
                  </div>
                  <Badge variant={extension.enabled ? 'default' : 'secondary'}>
                    {extension.enabled
                      ? t('extensions.status.enabled', { defaultValue: 'Enabled' })
                      : t('extensions.status.disabled', { defaultValue: 'Disabled' })}
                  </Badge>
                </div>
                <CardDescription>{extension.description || extension.id}</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-3">
                <span className="text-muted-foreground text-xs">v{extension.version}</span>
                <Button asChild size="sm" disabled={!extension.enabled && !canManage}>
                  <Link to={`/extensions/${extension.id}`}>
                    {t('extensions.open', { defaultValue: 'Open' })}
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
