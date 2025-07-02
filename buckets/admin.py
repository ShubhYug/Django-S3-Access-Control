from django.contrib import admin

from .models import Bucket, BucketPermission


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "prefix")


@admin.register(BucketPermission)
class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ("user", "bucket", "can_view", "can_upload", "can_delete")
    list_filter = ("can_view", "can_upload", "can_delete")
