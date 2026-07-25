import { createContext, useContext, useEffect, useState } from 'react'
import { loadJSON, saveJSON } from '../utils/storageUtils'

const STORAGE_KEY = 'compare'
const MAX_COMPARE = 3
const CompareContext = createContext(null)

export function CompareProvider({ children }) {
  const [compareIds, setCompareIds] = useState(() => loadJSON(STORAGE_KEY, []))
  const [message, setMessage] = useState('')

  useEffect(() => {
    saveJSON(STORAGE_KEY, compareIds)
  }, [compareIds])

  useEffect(() => {
    if (!message) return undefined
    const timer = setTimeout(() => setMessage(''), 2500)
    return () => clearTimeout(timer)
  }, [message])

  const isInCompare = (id) => compareIds.includes(Number(id))

  const addToCompare = (id) => {
    const numericId = Number(id)
    if (compareIds.includes(numericId)) return

    if (compareIds.length >= MAX_COMPARE) {
      setMessage('You can compare up to 3 properties only.')
      return
    }

    setCompareIds((prev) => [...prev, numericId])
  }

  const removeFromCompare = (id) => {
    const numericId = Number(id)
    setCompareIds((prev) => prev.filter((item) => item !== numericId))
  }

  const toggleCompare = (id) => {
    const numericId = Number(id)
    if (compareIds.includes(numericId)) {
      removeFromCompare(numericId)
    } else {
      addToCompare(numericId)
    }
  }

  const clearCompare = () => setCompareIds([])

  return (
    <CompareContext.Provider
      value={{
        compareIds,
        isInCompare,
        addToCompare,
        removeFromCompare,
        toggleCompare,
        clearCompare,
        message,
      }}
    >
      {children}
    </CompareContext.Provider>
  )
}

export function useCompare() {
  const context = useContext(CompareContext)
  if (!context) {
    throw new Error('useCompare must be used within CompareProvider')
  }
  return context
}
