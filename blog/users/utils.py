import os

from django.core.files.storage import FileSystemStorage


class CustomStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        base_name, extension = os.path.splitext(name)
        counter = 1
        while self.exists(name):
            name = f"{base_name}_{counter}{extension}"
            counter += 1
        return name
