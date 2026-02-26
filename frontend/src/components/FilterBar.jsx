import { useEffect, useRef, useState } from 'react'

function GameMultiSelect({ gameSystems, selectedIds, onChange }) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const allSelected = gameSystems.length > 0 && selectedIds.length === gameSystems.length

  function toggleSelectAll() {
    onChange(allSelected ? [] : gameSystems.map((gs) => gs.id))
  }

  function toggleId(id) {
    onChange(
      selectedIds.includes(id) ? selectedIds.filter((x) => x !== id) : [...selectedIds, id]
    )
  }

  let label = 'All Games'
  if (selectedIds.length === 1) {
    const gs = gameSystems.find((g) => g.id === selectedIds[0])
    label = gs ? gs.name : '1 Game Selected'
  } else if (selectedIds.length > 1) {
    label = `${selectedIds.length} Games Selected`
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400 flex items-center justify-between"
      >
        <span className={selectedIds.length ? 'text-gray-900 font-medium' : 'text-gray-500'}>
          {label}
        </span>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {/* Select All row */}
          <label className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={toggleSelectAll}
              className="accent-purple-600"
            />
            <span className="text-sm font-semibold text-gray-700">Select All</span>
          </label>

          {gameSystems.map((gs) => (
            <label
              key={gs.id}
              className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedIds.includes(gs.id)}
                onChange={() => toggleId(gs.id)}
                className="accent-purple-600"
              />
              <span className="text-sm text-gray-700">{gs.name}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  )
}

export default function FilterBar({ locations, gameSystems, filters, onChange, onSearch }) {
  function handleChange(key, value) {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Game System — multi-select */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Game System
          </label>
          <GameMultiSelect
            gameSystems={gameSystems}
            selectedIds={filters.gameSystemIds || []}
            onChange={(ids) => handleChange('gameSystemIds', ids)}
          />
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
          onClick={() => onChange({ locationId: null, gameSystemIds: [], dateFrom: null, dateTo: null })}
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
