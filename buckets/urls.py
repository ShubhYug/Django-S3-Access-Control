from django.urls import path
from .views import BucketListView, BucketObjectsView, UploadObjectView, DeleteObjectView


urlpatterns = [
    path('api/buckets/', BucketListView.as_view()),
    path('api/buckets/<int:bucket_id>/objects/', BucketObjectsView.as_view()),
    path('api/buckets/<int:bucket_id>/upload/', UploadObjectView.as_view()),
    path('api/buckets/<int:bucket_id>/objects/<str:key>/', DeleteObjectView.as_view()),
]