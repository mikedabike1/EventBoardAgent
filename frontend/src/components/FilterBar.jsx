export default function FilterBar({ locations, gameSystems, filters, onChange, onSearch }) {
  function handleChange(key, value) {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Game System */}
        <div>
          <label htmlFor="filter-game" className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Game System
          </label>
          <select
            id="filter-game"
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400"
            value={filters.gameSystemId || ''}
            onChange={(e) => handleChange('gameSystemId', e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">All Games</option>
            {gameSystems.map((gs) => (
              <option key={gs.id} value={gs.id}>{gs.name}</option>
            ))}
          </select>
        </div>

        {/* Location */}
        <div>
          <label htmlFor="filter-location" className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Location
          </label>
          <select
            id="filter-location"
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400"
            value={filters.locationId || ''}
            onChange={(e) => handleChange('locationId', e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">All Locations</option>
            {locations.map((l) => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
        </div>

        {/* Date From */}
        <div>
          <label htmlFor="filter-date-from" className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            From Date
          </label>
          <input
            id="filter-date-from"
            type="date"
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400"
            value={filters.dateFrom || ''}
            onChange={(e) => handleChange('dateFrom', e.target.value || null)}
          />
        </div>

        {/* Date To */}
        <div>
          <label htmlFor="filter-date-to" className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            To Date
          </label>
          <input
            id="filter-date-to"
            type="date"
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400"
            value={filters.dateTo || ''}
            onChange={(e) => handleChange('dateTo', e.target.value || null)}
          />
        </div>
      </div>

      <div className="mt-3 flex gap-2 justify-end">
        <button
          className="text-sm text-gray-500 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
          onClick={() => onChange({ locationId: null, gameSystemId: null, dateFrom: null, dateTo: null })}
        >
          Clear
        </button>
        <button
          className="text-sm bg-purple-600 text-white px-5 py-2 rounded-lg hover:bg-purple-700 transition-colors font-medium"
          onClick={onSearch}
        >
          Search
        </button>
      </div>
    </div>
  )
}
