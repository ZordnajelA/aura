import Navigation from '@/components/Navigation'

export default function DailyNotesPage() {
  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-6">Daily Notes</h1>
          <p className="text-gray-600">Daily notes timeline view will be implemented here.</p>
        </div>
      </main>
    </div>
  )
}
