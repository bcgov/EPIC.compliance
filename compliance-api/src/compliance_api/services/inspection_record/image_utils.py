"""Image utilities for efficient memory handling in DOCX generation."""

from io import BytesIO

from PIL import Image, UnidentifiedImageError
import requests
from requests.exceptions import RequestException

# Configuration
DEFAULT_TIMEOUT = 30  # seconds
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 8192  # 8KB chunks for streaming
TARGET_DPI = 300  # DPI for document images
JPEG_QUALITY = 92  # Quality for JPEG compression
Image.MAX_IMAGE_PIXELS = 200_000_000


class ImageDownloadError(Exception):
    """Raised when image download fails."""


class ImageTooLargeError(Exception):
    """Raised when image exceeds maximum size limit."""


class ImageProcessingError(Exception):
    """Raised when image processing/optimization fails."""


def download_image_stream(url: str, timeout: int = DEFAULT_TIMEOUT) -> BytesIO:
    """
    Download an image using streaming to minimize memory usage.

    Args:
        url: The URL of the image to download
        timeout: Request timeout in seconds

    Returns:
        BytesIO stream containing the image data

    Raises:
        ImageDownloadError: If download fails
        ImageTooLargeError: If image exceeds MAX_DOWNLOAD_SIZE
    """
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        # Check content-length if available
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > MAX_DOWNLOAD_SIZE:
            response.close()
            raise ImageTooLargeError(
                f"Image size {int(content_length)} bytes exceeds limit of {MAX_DOWNLOAD_SIZE} bytes"
            )

        # Stream download with size tracking
        image_data = BytesIO()
        downloaded_size = 0

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            downloaded_size += len(chunk)
            if downloaded_size > MAX_DOWNLOAD_SIZE:
                image_data.close()
                response.close()
                raise ImageTooLargeError(
                    f"Image size exceeds limit of {MAX_DOWNLOAD_SIZE} bytes"
                )
            image_data.write(chunk)

        image_data.seek(0)
        return image_data

    except RequestException as e:
        raise ImageDownloadError(f"Failed to download image: {e}") from e


def optimize_image_for_docx(
    image_stream: BytesIO,
    target_width_inches: float = 4.0,
    dpi: int = TARGET_DPI,
    quality: int = JPEG_QUALITY
) -> BytesIO:
    """
    Optimize an image for embedding in a DOCX document.

    Resizes the image to match the target display dimensions and compresses
    to reduce memory usage and final file size.

    Args:
        image_stream: BytesIO stream containing the original image
        target_width_inches: Target display width in inches
        dpi: Target DPI (dots per inch)
        quality: JPEG compression quality (1-100)

    Returns:
        BytesIO stream containing the optimized image
    """
    target_width_px = int(target_width_inches * dpi)

    with Image.open(image_stream) as img:
        original_width, original_height = img.size

        # Only resize if image is larger than target
        if original_width > target_width_px:
            # Calculate proportional height
            ratio = target_width_px / original_width
            target_height_px = int(original_height * ratio)

            # Use high-quality resampling
            img = img.resize((target_width_px, target_height_px), Image.LANCZOS)

        # Convert RGBA to RGB for JPEG compatibility (handles transparency)
        if img.mode in ('RGBA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Save optimized image to new stream
        optimized_stream = BytesIO()
        img.save(optimized_stream, format='JPEG', quality=quality, optimize=True)
        optimized_stream.seek(0)

        return optimized_stream


def download_and_optimize_image(
    url: str,
    target_width_inches: float = 4.0,
    timeout: int = DEFAULT_TIMEOUT
) -> BytesIO:
    """
    Download and optimize an image in one operation.

    This is the main entry point for efficient image handling.
    Downloads using streaming, optimizes for DOCX embedding, and
    cleans up intermediate resources.

    Args:
        url: The URL of the image to download
        target_width_inches: Target display width in inches
        timeout: Request timeout in seconds

    Returns:
        BytesIO stream containing the optimized image ready for DOCX

    Raises:
        ImageDownloadError: If download fails
        ImageTooLargeError: If image exceeds size limit
        ImageProcessingError: If image optimization fails
    """
    print(f"Starting download and optimization for image: {url}")
    raw_stream = None
    try:
        raw_stream = download_image_stream(url, timeout)
        optimized_stream = optimize_image_for_docx(raw_stream, target_width_inches)
        return optimized_stream
    except (UnidentifiedImageError, OSError) as e:
        raise ImageProcessingError(f"Failed to process image: {e}") from e
    finally:
        # Clean up the raw stream
        if raw_stream is not None:
            raw_stream.close()
