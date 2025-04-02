from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


class HiddenSchemaView(SpectacularAPIView):
    '''Скрывает эндпоинт /api/schema/ из публичной документации.'''

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        schema = response.data
        if '/api/schema/' in schema['paths']:
            del schema['paths']['/api/schema/']
        response.data = schema
        return response


urlpatterns = [
    path('api/', include('api.v1.urls')),
    path('api/schema/', HiddenSchemaView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    )
]
