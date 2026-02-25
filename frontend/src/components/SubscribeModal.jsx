import SubscribeForm from './SubscribeForm'

export default function SubscribeModal({ locations, gameSystems, onClose }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 text-xl leading-none font-bold"
          aria-label="Close"
        >
          ×
        </button>
        <div className="p-6">
          <SubscribeForm locations={locations} gameSystems={gameSystems} />
        </div>
      </div>
    </div>
  )
}
