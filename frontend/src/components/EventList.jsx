import EventCard from './EventCard'

export default function EventList({ events, loading, error }) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-16 text-gray-400">
        <div className="text-center">
          <div className="text-4xl mb-3 animate-pulse">🎲</div>
          <p>Loading events…</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 p-6 text-center text-red-700">
        <p className="font-medium">Failed to load events.</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    )
  }

  if (!events || events.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <div className="text-5xl mb-4">🔍</div>
        <p className="text-lg font-medium text-gray-500">No events found</p>
        <p className="text-sm mt-1">Try adjusting your filters or check back soon.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  )
}
