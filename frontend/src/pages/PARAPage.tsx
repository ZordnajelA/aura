import Navigation from '@/components/Navigation'

export default function PARAPage() {
  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-6">PARA Organization</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-2">Projects</h2>
              <p className="text-gray-600">Active projects</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-2">Areas</h2>
              <p className="text-gray-600">Ongoing responsibilities</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-2">Resources</h2>
              <p className="text-gray-600">Reference materials</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-2">Archives</h2>
              <p className="text-gray-600">Completed items</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
