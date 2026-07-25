export default function Toast({ message, visible }) {
  if (!visible || !message) return null

  return (
    <div className="fixed bottom-6 right-6 z-[100] transition-opacity duration-300">
      <div className="bg-slate-900 text-white px-4 py-3 rounded-lg shadow-lg text-sm font-medium">
        {message}
      </div>
    </div>
  )
}
