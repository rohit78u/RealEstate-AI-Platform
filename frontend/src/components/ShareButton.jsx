import { useState } from 'react'
import Toast from './Toast'

export default function ShareButton({ className = '' }) {
  const [toast, setToast] = useState({ visible: false, message: '' })

  const showToast = (message) => {
    setToast({ visible: true, message })
    setTimeout(() => setToast({ visible: false, message: '' }), 2500)
  }

  const handleShare = async (event) => {
    event.preventDefault()
    event.stopPropagation()

    const url = window.location.href

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(url)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = url
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
      showToast('Link copied to clipboard!')
    } catch {
      showToast('Unable to copy link')
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={handleShare}
        className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-300 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors duration-200 ${className}`}
      >
        <span>↗</span>
        Share
      </button>
      <Toast message={toast.message} visible={toast.visible} />
    </>
  )
}
