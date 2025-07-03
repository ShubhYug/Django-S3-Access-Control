import boto3
from botocore.exceptions import ClientError
from decouple import config
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bucket, BucketPermission
from .serializers import BucketSerializer

# AWS S3 client setup
aws_client = boto3.client(
    "s3",
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
)


class BucketListView(APIView):
    """
    API view to list all buckets the authenticated user has permission to view.
    GET /api/buckets/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        permissions_qs = BucketPermission.objects.filter(
            user=request.user, can_view=True
        )
        buckets = [perm.bucket for perm in permissions_qs]
        serializer = BucketSerializer(buckets, many=True)
        return Response(serializer.data)

class BucketObjectsView(APIView):
    """
    API view to list all objects in a given bucket the user is allowed to view.
    GET /api/buckets/<bucket_id>/objects/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, bucket_id):
        bucket = get_object_or_404(Bucket, id=bucket_id)
        print("bucket : ", bucket)
        get_object_or_404(
            BucketPermission, user=request.user, bucket=bucket, can_view=True
        )

        try:
            objects = aws_client.list_objects_v2(
                Bucket=bucket.name, Prefix=bucket.prefix or ""
            )
            contents = objects.get("Contents", [])
            return Response([obj["Key"] for obj in contents])
        except ClientError as e:
            return Response({"error": str(e)}, status=500)


class UploadObjectView(APIView):
    """
    API view to upload an object to a bucket if the user has upload permissions.
    POST /api/buckets/<bucket_id>/upload/
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, bucket_id):
        bucket = get_object_or_404(Bucket, id=bucket_id)
        get_object_or_404(
            BucketPermission, user=request.user, bucket=bucket, can_upload=True
        )

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)

        try:
            key = f"{bucket.prefix or ''}{timezone.now().strftime('%Y%m%d-%H%M%S')}_{file.name}"
            aws_client.upload_fileobj(file, bucket.name, key)
            return Response(
                {"message": "Upload successful", "bucket": bucket.name, "key": key},
                status=201,
            )
        except ClientError as e:
            return Response({"error": str(e)}, status=500)


class DeleteObjectView(APIView):
    """
    API view to delete an object from a bucket if the user has delete permissions.
    DELETE /api/buckets/<bucket_id>/objects/<key>/
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, bucket_id, key):
        bucket = get_object_or_404(Bucket, id=bucket_id)
        get_object_or_404(
            BucketPermission, user=request.user, bucket=bucket, can_delete=True
        )

        try:
            aws_client.delete_object(Bucket=bucket.name, Key=key)
            return Response({"message": "Deleted successfully"})
        except ClientError as e:
            return Response({"error": str(e)}, status=500)


# -------------------------------
# UI Views for HTML rendering
# -------------------------------


@login_required
def bucket_browser(request):
    permissions_qs = BucketPermission.objects.filter(user=request.user, can_view=True)
    buckets = []

    if not permissions_qs.exists():
        return render(request, "buckets.html", {"buckets": [], "message": "You do not have access to any buckets."})

    for perm in permissions_qs:
        bucket = perm.bucket
        objects = aws_client.list_objects_v2(
            Bucket=bucket.name, Prefix=bucket.prefix or ""
        )
        keys = [obj["Key"] for obj in objects.get("Contents", [])]
        buckets.append({
            "id": bucket.id,
            "name": bucket.name,
            "objects": keys,
            "can_upload": perm.can_upload,
            "can_delete": perm.can_delete
        })

    return render(request, "buckets.html", {"buckets": buckets})


@login_required
@csrf_exempt
def handle_upload_form(request, bucket_id):
    """
    Handles the file upload form submitted from the HTML interface.
    """
    if request.method == "POST":
        file = request.FILES.get("file")
        bucket = get_object_or_404(Bucket, id=bucket_id)
        get_object_or_404(
            BucketPermission, user=request.user, bucket=bucket, can_upload=True
        )

        if file:
            key = f"{file.name}"
            aws_client.upload_fileobj(file, bucket.name, key)

    return redirect("bucket-browser")


@login_required
@require_POST
@csrf_exempt
def handle_delete(request, bucket_id, key):
    """
    Handles the delete form submitted from the HTML interface to remove an object from a bucket.
    """
    bucket = get_object_or_404(Bucket, id=bucket_id)
    get_object_or_404(
        BucketPermission, user=request.user, bucket=bucket, can_delete=True
    )

    try:
        aws_client.delete_object(Bucket=bucket.name, Key=key)
    except ClientError:
        pass

    return redirect("bucket-browser")


def logout_view(request):
    """
    Logs the user out and redirects to the login page.
    """
    logout(request)
    return redirect("login")
