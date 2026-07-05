import { ExtensionHost } from '@/features/extensions/components/extension-host'
import { useParams } from 'react-router'

export default function ExtensionDetailPage() {
  const { extensionId = '' } = useParams()
  return <ExtensionHost extensionId={extensionId} />
}
