type ExtensionIframeProps = {
  extensionId: string
  pagePath?: string
  title: string
}

export function ExtensionIframe({ extensionId, pagePath = 'dashboard', title }: ExtensionIframeProps) {
  const baseApi = import.meta.env.VITE_BASE_API || '/'
  const normalizedBase = baseApi.endsWith('/') ? baseApi : `${baseApi}/`
  const src = new URL(`api/extensions/${extensionId}/ui/${pagePath}/`, normalizedBase).toString()

  return (
    <iframe
      title={title}
      src={src}
      className="h-[calc(100vh-12rem)] w-full rounded-lg border border-border bg-background"
      sandbox="allow-scripts allow-forms allow-same-origin"
    />
  )
}
