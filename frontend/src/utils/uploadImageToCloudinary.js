/**
 * Upload a single image to Cloudinary (same preset as Feed posts).
 * Returns { url } or null if env missing / failure.
 */
export async function uploadImageToCloudinary(file) {
  const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
  const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET
  if (!cloudName || !uploadPreset || !file) return null

  const formData = new FormData()
  formData.append('file', file)
  formData.append('upload_preset', uploadPreset)

  try {
    const response = await fetch(
      `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`,
      { method: 'POST', body: formData }
    )
    const data = await response.json()
    if (!data.secure_url) return null
    return { url: data.secure_url }
  } catch {
    return null
  }
}
