const GALLERY_SETS = {
  villa: [
    "/images/villa-exterior.png",
    "/images/living-room.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
    "/images/balcony.png",
  ],
  apartment: [
    "/images/apartment.png",
    "/images/living-room.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
    "/images/balcony.png",
  ],
  flat: [
    "/images/apartment.png",
    "/images/flat-interior.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
  ],
  home: [
    "/images/flat-interior.png",
    "/images/living-room.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
  ],
  residence: [
    "/images/living-room.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
    "/images/balcony.png",
  ],
  luxury: [
    "/images/villa-exterior.png",
    "/images/living-room.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
    "/images/balcony.png",
  ],
  default: [
    "/images/apartment.png",
    "/images/living-room.png",
    "/images/bedroom.png",
    "/images/kitchen.png",
  ],
};

function getGalleryKey(title = "") {
  const t = title.toLowerCase();

  if (t.includes("villa")) return "villa";
  if (t.includes("apartment")) return "apartment";
  if (t.includes("flat")) return "flat";
  if (t.includes("home")) return "home";
  if (t.includes("residence")) return "residence";
  if (t.includes("luxury")) return "luxury";

  return "default";
}

export function getPropertyImage(title = "") {
  return getPropertyGalleryImages(title)[0];
}

export function getPropertyGalleryImages(title = "") {
  return GALLERY_SETS[getGalleryKey(title)];
}