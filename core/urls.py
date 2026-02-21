from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # On retire la ligne logout d'ici car elle est déjà gérée 
    # dans users/urls.py avec ta propre vue (views.deconnexion_view)
    
    path('users/', include('users.urls')), 
    path('', include('ponzi.urls')),       
]