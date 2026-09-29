import uuid

from decouple import config
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from supabase import create_client


@deconstructible
class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage.

    Uploaded files are stored in the Supabase
    'space-images' bucket.
    """

    def __init__(self):
        self.supabase_url = config("SUPABASE_URL")

        self.supabase_key = config(
            "SUPABASE_SERVICE_ROLE_KEY"
        )

        self.bucket = config(
            "SUPABASE_STORAGE_BUCKET",
            default="space-images",
        )

        self.supabase = create_client(
            self.supabase_url,
            self.supabase_key,
        )

    def _generate_name(self, name):
        """
        Generate a unique filename while
        preserving the original extension.
        """

        extension = ""

        if "." in name:
            extension = "." + name.rsplit(".", 1)[1].lower()

        filename = f"{uuid.uuid4().hex}{extension}"

        return f"space_images/{filename}"

    def _open(self, name, mode="rb"):
        """
        Download a file from Supabase Storage.
        """

        response = (
            self.supabase.storage
            .from_(self.bucket)
            .download(name)
        )

        return ContentFile(response)

    def _save(self, name, content):
        """
        Upload a file to Supabase Storage.
        """

        if hasattr(content, "seek"):
            content.seek(0)

        file_data = content.read()

        final_name = self._generate_name(name)

        content_type = getattr(
            content,
            "content_type",
            None,
        )

        file_options = {
            "cache-control": "31536000",
            "upsert": "false",
        }

        if content_type:
            file_options["content-type"] = content_type

        (
            self.supabase.storage
            .from_(self.bucket)
            .upload(
                path=final_name,
                file=file_data,
                file_options=file_options,
            )
        )

        return final_name

    def delete(self, name):
        """
        Delete a file from Supabase Storage.
        """

        if not name:
            return

        (
            self.supabase.storage
            .from_(self.bucket)
            .remove([name])
        )

    def exists(self, name):
        """
        UUID filenames make collisions extremely unlikely.
        """

        return False

    def url(self, name):
        """
        Return the public Supabase URL.
        """

        return (
            self.supabase.storage
            .from_(self.bucket)
            .get_public_url(name)
        )

    def size(self, name):
        """
        Django may request file size.
        """

        return 0