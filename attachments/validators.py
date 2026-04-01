import os

from rest_framework import serializers

from attachments.constants import ALLOWED_EXTENSIONS


def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise serializers.ValidationError("Unsupported file type.")
    return file


def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5 MB
    if file.size > max_size:
        raise serializers.ValidationError("File too large.")
    return file
