from django.contrib import admin
from api.models import SwellBuoy, TideBuoy, SurfSpot, SurfSession

# Register your models here.
admin.site.register([SwellBuoy, TideBuoy, SurfSpot, SurfSession])
