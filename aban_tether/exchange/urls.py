from django.urls import path
from .views import SubmitOrderView

urlpatterns = [
    path('submit-order/', SubmitOrderView.as_view(), name='submit-order'),
]
