from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from .models import Post, Vote
from .serializers import PostSerializer, VoteSerializer
from rest_framework.response import Response


# PostList because we want to list out all our posts in the database
class PostList(generics.ListCreateAPIView):
    # 1st . whats information we want from the database
    queryset = Post.objects.all()
    #   2nd.  what serializer we going to use -- we created PostSerializer
    serializer_class = PostSerializer
    # only authenticated users can post to our APIs , but anyone can view it
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # save the API post made , and save it by the user that made the request
    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)


class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # can only delete a post you created
    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['pk'], poster=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('this isnt your post to delet bruh !')


class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, post=post)

    # save the Api vote that is made , by the voter thats requesting to post
    # also we want to set what the post is
    def perform_create(self, serializer):
        # the reason we created the get_queryset is so we can use this if statement
        # which checks if the user already made a vote for the same post more then once
        # and if they did , raise error
        if self.get_queryset().exists():
            raise ValidationError('you have already voted for this post')
        serializer.save(voter=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))

    # reason for this function , we dont want a user to delete something they never voted for
    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            # if the vote exist delete and respond as follows
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('you never voted for this post')
