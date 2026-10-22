from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Property, PropertyImage

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    #Maybe this is the reason why the login is not working, because the serializer is not returning the token. 
    #YEAH that what i think ! 
    
class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['uploaded_at']

#Now we create the class thats going to handle the property Serializer
class PropertySerializer(serializers.ModelSerializer):
    agent_name = serializers.SerializerMethodField()
    #Agregamos las imagenes vinculadas.
    images = PropertyImageSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        #fields = '__all__' # No hace caso a las peticiones y comrpobaciones durante las modificaciones de json files.
        fields = [
            'id', 'agent', 'agent_name', 'title', 'description', 
            'property_type', 'status', 'price', 'area_m2', 
            'bedrooms', 'bathrooms', 'parking_spaces', 'location',
            'latitude', 'longitude',
            'images',
            'unavailability_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ('agent','created_at','updated_at')
    
    def get_agent_name(self,obj): #This function it made for get the full name and user name of who make or add the proerty.
        if obj.agent:
            return obj.agent.get_full_name() or obj.agent.username
        return None
    
    def validate(self, attrs): 
        # Obtener el estado del objeto actual o de los datos entrantes
        status = attrs.get('status', getattr(self.instance, 'status', None))
        unavailability_reason = attrs.get('unavailability_reason', getattr(self.instance, 'unavailability_reason', None))

        if status == 'no_disponible' and not unavailability_reason:
            raise serializers.ValidationError({
                "unavailability_reason": "Debe especificar un motivo para marcar la propiedad como No disponible."
            })

        if status in ['vendido', 'arrendado']:
            raise serializers.ValidationError({
                "status": "Las propiedades solo pueden pasar a Vendido o Arrendado mediante la confirmación de Cierre definitivo."
            })

        return attrs
    
    ##Remember Delete this code  before of the second commit.
    ''' # Its not making the validation on each field of the .json file
    def validate(self, attrs):
        if data.get('status') == 'no_disponible' and not data.get('unavailability_reason'):
            raise serializers.ValidationError({
                "unavailability_reason":"Debe especificar un motivo para marcar la propiedad como No disponible."
            })
        if data.get('status') in ['vendido', 'arrendado']:
            raise serializers.ValidationError({
                "status":"Las propiedaes se encuentran en estasdos Vendido o Arrendado solo pueden asignarse mediante la confirmación de Cierre definitivo"
            })
            
        return data
    '''
    
    def get_agent_name(self, obj):
        if obj.agent:
            # Intenta con el nombre completo; si está vacío, devuelve el username o el email
            full_name = f"{obj.agent.first_name} {obj.agent.last_name}".strip()
            return full_name if full_name else (obj.agent.username or obj.agent.email)
        return ""