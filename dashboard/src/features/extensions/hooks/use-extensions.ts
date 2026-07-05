import { fetcher } from '@/service/http'
import type { ExtensionEnabledUpdate, ExtensionInfo, ExtensionSettingsUpdate } from '@/features/extensions/types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

const EXTENSIONS_KEY = ['extensions'] as const

export function useExtensions() {
  return useQuery({
    queryKey: EXTENSIONS_KEY,
    queryFn: () => fetcher<ExtensionInfo[]>('/api/extensions'),
  })
}

export function useExtension(extensionId: string | undefined) {
  return useQuery({
    queryKey: [...EXTENSIONS_KEY, extensionId],
    queryFn: () => fetcher<ExtensionInfo>(`/api/extensions/${extensionId}`),
    enabled: Boolean(extensionId),
  })
}

export function useUpdateExtensionSettings(extensionId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ExtensionSettingsUpdate) =>
      fetcher<Record<string, unknown>>(`/api/extensions/${extensionId}/settings`, {
        method: 'PUT',
        body: payload,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: EXTENSIONS_KEY })
    },
  })
}

export function useSetExtensionEnabled(extensionId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ExtensionEnabledUpdate) =>
      fetcher<ExtensionInfo>(`/api/extensions/${extensionId}/enabled`, {
        method: 'PUT',
        body: payload,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: EXTENSIONS_KEY })
    },
  })
}
