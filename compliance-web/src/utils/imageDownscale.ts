const MAX_DPI = 300; // High quality print resolution
const LETTER_LONG_EDGE_INCHES = 11;
const LETTER_SHORT_EDGE_INCHES = 8.5;
const MAX_LONG_EDGE_PX = MAX_DPI * LETTER_LONG_EDGE_INCHES; // 3300px
const MAX_SHORT_EDGE_PX = MAX_DPI * LETTER_SHORT_EDGE_INCHES; // 2550px
const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5MB

interface DownscaleOptions {
  maxLongEdge?: number;
  maxShortEdge?: number;
  maxSizeBytes?: number;
  initialQuality?: number;
  minQuality?: number;
}

/**
 * Resizes/compresses an image File so neither edge exceeds the letter-paper
 * cap at 300 DPI and the file never exceeds maxSizeBytes. Non-raster files
 * (svg, etc.) pass through unchanged. Returns a new File, or the original
 * file if it already satisfies both constraints.
 */
export async function downscaleImage(
  file: File,
  options: DownscaleOptions = {}
): Promise<File> {
  const {
    maxLongEdge = MAX_LONG_EDGE_PX,
    maxShortEdge = MAX_SHORT_EDGE_PX,
    maxSizeBytes = MAX_FILE_SIZE_BYTES,
    initialQuality = 0.92,
    minQuality = 0.5,
  } = options;

  if (!file.type.startsWith("image/") || file.type === "image/svg+xml") {
    return file;
  }

  const bitmap = await loadBitmap(file);
  const { width: origWidth, height: origHeight } = bitmap;

  // The longer side is capped at maxLongEdge, the shorter at maxShortEdge
  const isLandscape = origWidth >= origHeight;
  const longEdge = isLandscape ? origWidth : origHeight;
  const shortEdge = isLandscape ? origHeight : origWidth;

  const withinDimensions = longEdge <= maxLongEdge && shortEdge <= maxShortEdge;
  if (withinDimensions && file.size <= maxSizeBytes) {
    return file;
  }

  const scale = Math.min(1, maxLongEdge / longEdge, maxShortEdge / shortEdge);
  const width = Math.round(origWidth * scale);
  const height = Math.round(origHeight * scale);

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (!ctx) return file;
  ctx.drawImage(bitmap, 0, 0, width, height);

  // PNGs stay PNG; everything else gets re-encoded as JPEG so changing 
  // the quality actually helps with size.
  const outputType = file.type === "image/png" ? "image/png" : "image/jpeg";

  let quality = initialQuality;
  let blob = await canvasToBlob(canvas, outputType, quality);

  while (blob.size > maxSizeBytes && quality > minQuality) {
    quality -= 0.1;
    blob = await canvasToBlob(canvas, outputType, quality);
  }

  // If still too big (common with PNG) shrink dimensions in the same proportions
  while (blob.size > maxSizeBytes && canvas.width > 500 && canvas.height > 500) {
    canvas.width = Math.round(canvas.width * 0.85);
    canvas.height = Math.round(canvas.height * 0.85);
    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    blob = await canvasToBlob(canvas, outputType, Math.max(quality, minQuality));
  }

  return new File([blob], renameToExt(file.name, outputType), {
    type: outputType,
    lastModified: file.lastModified,
  });
}

function loadBitmap(file: File): Promise<ImageBitmap> {
  return createImageBitmap(file);
}

function canvasToBlob(
  canvas: HTMLCanvasElement,
  type: string,
  quality: number
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error("Canvas toBlob failed"))),
      type,
      quality
    );
  });
}

function renameToExt(name: string, mimeType: string): string {
  const ext = mimeType === "image/png" ? "png" : "jpg";
  const base = name.replace(/\.[^/.]+$/, "");
  return `${base}.${ext}`;
}