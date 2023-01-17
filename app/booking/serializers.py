from rest_framework import serializers
from booking.models import Booking, Kit, Laboratory, TimeFrame
from django.utils.crypto import get_random_string
from datetime import datetime, date, timedelta

from users.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'start_date', 'end_date', 'available', 'public', 'access_id', 'password', 'owner', 'reserved_by', 'kit']
        extra_kwargs = {
            'start_date': {'required': True},
            'end_date': {'required': True},
            'available': {'required': True},
            'public': {'required': True},
            'access_id': {'required': True},
            'user': {'required': True},
            'kit': {'required': True}
        }

    def create(self, validated_data):
        validated_data['password'] = get_random_string(15)
        return Booking.objects.create(**validated_data)


class PublicBookingSerializer(serializers.ModelSerializer):

    reserved_by = UserSerializer()

    class Meta:
        model = Booking
        fields = ['id', 'start_date', 'end_date', 'available', 'public', 'access_id', 'password', 'owner', 'reserved_by', 'kit']
        

class KitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Kit
        fields = ['id', 'name', 'description', 'laboratory']
        extra_kwargs = {
            'name': {'required': True},
            'laboratory': {'required': True}
        }


class LaboratorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Laboratory
        fields = ['id', 'name', 'description', 'url']
        extra_kwargs = {
            'name': {'required': True}
        }


class TimeFrameSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeFrame
        fields = ['id', 'start_date', 'end_date', 'start_hour', 'end_hour', 'slot_duration', 'kit', 'enabled']
        extra_kwargs = {
            'start_date': {'required': True},
            'end_date': {'required': True},
            'start_hour': {'required': True},
            'end_hour': {'required': True},
            'slot_duration': {'required': True},
            'kit': {'required': True}
        }

    def create(self, validated_data):
        public = self.context['request'].data.get('public', False)

        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        start_hour = validated_data['start_hour']
        end_hour = validated_data['end_hour']

        kit = validated_data['kit']
        slot_duration = validated_data['slot_duration']

        if start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date")
        if start_hour > end_hour:
            raise serializers.ValidationError("Start hour must be before end hour")

        time_delta = end_date - start_date

        number_of_days = time_delta.days        
        number_of_slots = int(((datetime.combine(date.today(), end_hour) - datetime.combine(date.today(), start_hour)).total_seconds() / 60) / slot_duration)

        for _ in range(number_of_days + 1):
            start_date = datetime.combine(start_date, start_hour).replace(tzinfo=datetime.now().astimezone().tzinfo)

            for _ in range(number_of_slots):
                end_date = start_date + timedelta(minutes=slot_duration)

                booking = Booking.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    available=True,
                    public=public,
                    password=get_random_string(15),
                    owner=self.context['request'].user,
                    kit=kit
                )

                booking.save()
                start_date = end_date
            
            start_date = start_date + timedelta(days=1)

        return TimeFrame.objects.create(**validated_data)
