from django.contrib.auth.models import User

from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource

from comics.api.authentication import (
    SecretKeyAuthentication, MultiAuthentication)
from comics.api.authorization import SubscriptionsAuthorization
from comics.core.models import Comic, Release, Image
from comics.accounts.models import Subscription


class UsersResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['email', 'date_joined', 'last_login']
        resource_name = 'users'
        authentication = MultiAuthentication(
            BasicAuthentication(realm='Comics API'),
            SecretKeyAuthentication())
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(pk=request.user.pk)

    def dehydrate(self, bundle):
        bundle.data['secret_key'] = \
            bundle.request.user.comics_profile.secret_key
        return bundle


class ComicsResource(ModelResource):
    class Meta:
        queryset = Comic.objects.all()
        resource_name = 'comics'
        authentication = SecretKeyAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'active': 'exact',
            'language': 'exact',
            'name': ALL,
            'slug': ALL,
        }

    def apply_authorization_limits(self, request, object_list):
        if request.GET.get('subscribed') == 'true':
            return object_list.filter(userprofile__user=request.user)
        elif request.GET.get('subscribed') == 'false':
            return object_list.exclude(userprofile__user=request.user)
        else:
            return object_list


class ImagesResource(ModelResource):
    class Meta:
        queryset = Image.objects.all()
        resource_name = 'images'
        authentication = SecretKeyAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'fetched': ALL,
            'title': ALL,
            'text': ALL,
            'height': ALL,
            'width': ALL,
        }


class ReleasesResource(ModelResource):
    comic = fields.ToOneField(ComicsResource, 'comic')
    images = fields.ToManyField(ImagesResource, 'images', full=True)

    class Meta:
        queryset = Release.objects.select_related().order_by('-fetched')
        resource_name = 'releases'
        authentication = SecretKeyAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'comic': ALL_WITH_RELATIONS,
            'images': ALL_WITH_RELATIONS,
            'pub_date': ALL,
            'fetched': ALL,
        }

    def apply_authorization_limits(self, request, object_list):
        if request.GET.get('subscribed') == 'true':
            return object_list.filter(comic__userprofile__user=request.user)
        elif request.GET.get('subscribed') == 'false':
            return object_list.exclude(comic__userprofile__user=request.user)
        else:
            return object_list


class SubscriptionsResource(ModelResource):
    comic = fields.ToOneField(ComicsResource, 'comic')

    class Meta:
        queryset = Subscription.objects.all()
        resource_name = 'subscriptions'
        authentication = SecretKeyAuthentication()
        authorization = SubscriptionsAuthorization()
        list_allowed_methods = ['get', 'post', 'patch']
        detail_allowed_methods = ['get', 'delete', 'put']
        filtering = {
            'comic': ALL_WITH_RELATIONS,
        }

    def obj_create(self, bundle, request=None, **kwargs):
        return super(SubscriptionsResource, self).obj_create(
            bundle, request, userprofile=request.user.comics_profile)
