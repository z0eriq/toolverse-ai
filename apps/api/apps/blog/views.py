from rest_framework import generics, permissions

from apps.blog.models import BlogPost
from apps.blog.serializers import BlogPostDetailSerializer, BlogPostListSerializer
from apps.common.exceptions import success_response


class BlogPostListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = BlogPostListSerializer
    queryset = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).prefetch_related("tags")

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page if page is not None else self.get_queryset(), many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return success_response(serializer.data)


class BlogPostDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = BlogPostDetailSerializer
    lookup_field = "slug"
    queryset = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).prefetch_related("tags")

    def retrieve(self, request, *args, **kwargs):
        return success_response(self.get_serializer(self.get_object()).data)
