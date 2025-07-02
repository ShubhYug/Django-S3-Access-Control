# Create your views here.
import boto3
from botocore.exceptions import ClientError
from decouple import config
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bucket, BucketPermission
from .serializers import BucketSerializer

# Create AWS S3 client
aws_client = boto3.client(
    "s3",
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
)


class BucketListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        permissions_qs = BucketPermission.objects.filter(
            user=request.user, can_view=True
        )
        buckets = [perm.bucket for perm in permissions_qs]
        serializer = BucketSerializer(buckets, many=True)
        return Response(serializer.data)


class BucketObjectsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, bucket_id):
        bucket = get_object_or_404(Bucket, id=bucket_id)
        perm = get_object_or_404(
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
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, bucket_id):
        bucket = get_object_or_404(Bucket, id=bucket_id)
        perm = get_object_or_404(
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
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, bucket_id, key):
        bucket = get_object_or_404(Bucket, id=bucket_id)
        perm = get_object_or_404(
            BucketPermission, user=request.user, bucket=bucket, can_delete=True
        )

        try:
            aws_client.delete_object(Bucket=bucket.name, Key=key)
            return Response({"message": "Deleted successfully"})
        except ClientError as e:
            return Response({"error": str(e)}, status=500)
