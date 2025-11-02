import CaptureInterface from '@/components/CaptureInterface'
import Navigation from '@/components/Navigation'

export default function HomePage() {
  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-hidden">
        <CaptureInterface />
      </main>
    </div>
  )
}
