// Keep phone captures within the backend's image-size and pixel limits.
export async function prepareCameraPhoto(file) {
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    throw new Error('Please capture or upload a JPG or PNG photo.');
  }
  if (file.size > 30 * 1024 * 1024) throw new Error('This photo is too large. Use a lower camera resolution.');
  const url = URL.createObjectURL(file);
  try {
    const image = new Image();
    image.src = url;
    await image.decode();
    const scale = Math.min(1, 1600 / Math.max(image.naturalWidth, image.naturalHeight));
    if (scale === 1 && file.size <= 10 * 1024 * 1024) return file;
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
    canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Camera photo processing is unavailable. Please upload a smaller JPG.');
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92));
    if (!blob) throw new Error('Could not prepare this camera photo. Try uploading a JPG.');
    return new File([blob], 'leaf-camera.jpg', { type: 'image/jpeg' });
  } finally {
    URL.revokeObjectURL(url);
  }
}
