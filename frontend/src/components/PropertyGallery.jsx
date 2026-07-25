import { useMemo, useState } from 'react'
import { getPropertyGalleryImages } from '../utils/imageUtils'

export default function PropertyGallery({ property }) {
  const images = useMemo(() => {
    const dbImages = (property.images || []).map((img) => img.image_path)
    const placeholders = getPropertyGalleryImages(property.title)

    if (dbImages.length > 0) {
      const merged = [...dbImages]
      placeholders.forEach((img) => {
        if (!merged.includes(img)) merged.push(img)
      })
      return merged.slice(0, 5)
    }

    return placeholders
  }, [property])

  const [selectedIndex, setSelectedIndex] = useState(0)
  const selectedImage = images[selectedIndex] || images[0]

  return (
    <div>
      <div className="bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl h-80 lg:h-96 overflow-hidden">
        <img
          src={selectedImage}
          alt={property.title}
          className="w-full h-full object-cover rounded-xl transition-opacity duration-300"
        />
      </div>

      {images.length > 1 && (
        <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
          {images.map((image, index) => (
            <button
              key={`${image}-${index}`}
              type="button"
              onClick={() => setSelectedIndex(index)}
              className={`flex-shrink-0 h-16 w-24 rounded-lg overflow-hidden border-2 transition-all duration-300 hover:opacity-80 ${
                selectedIndex === index ? 'border-primary-600 ring-2 ring-primary-600' : 'border-transparent'
              }`}
            >
              <img src={image} alt="" className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
