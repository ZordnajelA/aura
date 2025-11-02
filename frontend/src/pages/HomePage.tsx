import CaptureInterface from '@/components/CaptureInterface'

export default function HomePage() {
  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">Aura</h1>
        <p className="text-sm text-gray-500">Universal Capture & PKM Assistant</p>
      </header>

      <main className="flex-1 overflow-hidden">
        <CaptureInterface />
      </main>
    </div>
  )
}
