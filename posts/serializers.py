from rest_framework import serializers
# we use '.' when we staying in the same app
from .models import Post, Vote


# when someone wants information from our model about a Post object
# it will come here to PostSerializer, which wll convert out model into
# Json
class PostSerializer(serializers.ModelSerializer):
    poster = serializers.ReadOnlyField(source='poster.username')
    poster_id = serializers.ReadOnlyField(source='poster.id')
    # we want to add votes and be able to see the amount of votes , so votes needed to be added to fields
    # but through a function , because we want the total votes for a specific post
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'url', 'poster', 'poster_id', 'created', 'votes']

    def get_votes(self, post):
        return Vote.objects.filter(post=post).count()


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        # the reason we dont put 'voter' and 'post' in fields is because we dont want people to be able
        # change those fields or add those fields
        fields = ['id']
