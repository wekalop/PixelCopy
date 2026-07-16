"""User-facing domain and service exceptions."""


class PixelCopyError(Exception):
    """Base class for expected PixelCopy failures."""


class ImageImportError(PixelCopyError):
    """Base class for image import failures."""


class UnsupportedImageError(ImageImportError):
    """The decoded content is not a supported image format."""


class CorruptImageError(ImageImportError):
    """The source could not be decoded safely as an image."""
