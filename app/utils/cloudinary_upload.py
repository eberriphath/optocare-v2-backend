import cloudinary.uploader


ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf",
    "jpg",
    "jpeg",
    "png"
}

MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10 MB


def get_file_extension(filename):
    if not filename or "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1].lower()


def validate_document(file):

    if not file:
        return False, "No document was provided"

    if not file.filename:
        return False, "Document filename is missing"

    extension = get_file_extension(file.filename)

    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        return False, (
            "Unsupported document type. "
            "Allowed types are PDF, JPG, JPEG and PNG"
        )

    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_DOCUMENT_SIZE:
        return False, "Document must not exceed 10 MB"

    return True, None


def upload_document(file, application_id):

    result = cloudinary.uploader.upload(
        file,
        resource_type="auto",
        folder="optocare/applications",
        public_id=f"application_{application_id}",
        overwrite=True
    )

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
        "resource_type": result.get("resource_type"),
        "format": result.get("format")
    }