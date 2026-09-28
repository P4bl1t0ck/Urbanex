from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

#Now we create the class thats going to handle the property Serializer
class PropertySerializer(serializers.ModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent.get_full_name')
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('agent','created_at','updated_at')
    
    def validate(self, data):
        if data.get('status') == 'no_disponible' and not data.get('unavailability_reason'):
            raise serializers.ValidationError({
                "unavailability_reason":"Debe especificar un motivo para marcar la propiedad como No disponible."
            })
        if data.get('status') in ['vendido', 'arrendado']:
            raise serializers.ValidationError({
                "status":"Las propiedaes se encuentran en estasdos Vendido o Arrendado solo pueden asignarse mediante la confirmación de Cierre definitivo"
            })
            
        return data
            
    