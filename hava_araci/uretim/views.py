from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Parca, Ucak, Takim, Personel, UcakParca
from .serializers import ParcaSerializer, UcakSerializer, TakimSerializer, PersonelSerializer


class SimpleLoginView(LoginView):
    """
    Overrides the default LoginView to remove authentication restrictions.
    """
    def form_valid(self, form):
        # Authenticate the user without additional restrictions
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        # Authenticate the user (this checks username/password correctness)
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('/')  # Redirect after successful login
        else:
            form.add_error(None, "Invalid credentials")
            return self.form_invalid(form)

class ParcaViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for 'Parca' model and ensures that
    parts are produced only by responsible teams.
    """
    queryset = Parca.objects.all()
    serializer_class = ParcaSerializer

    def create(self, request, *args, **kwargs):
        """
        Validates if the team producing the part is responsible for the given part type.
        """
        data = request.data
        parca_tipi = data.get('tip', None)
        takim_id = data.get('takim_id', None)

        # Check if the team is authorized to produce this part type
        if takim_id:
            try:
                takim = Takim.objects.get(id=takim_id)
                if takim.sorumlu_parca_tipi != parca_tipi:
                    return Response(
                        {"error": f"{takim.isim} cannot produce parts of type: {parca_tipi}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Takim.DoesNotExist:
                return Response(
                    {"error": "Team does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return super().create(request, *args, **kwargs)


class UcakViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for 'Ucak' model.
    """
    queryset = Ucak.objects.all()
    serializer_class = UcakSerializer


class TakimViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for 'Takim' model.
    """
    queryset = Takim.objects.all()
    serializer_class = TakimSerializer
class PersonelViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for 'Personel' model and validates team assignments.
    """
    queryset = Personel.objects.all()
    serializer_class = PersonelSerializer
    print("PersonelViewSet")

    def create(self, request, *args, **kwargs):
        """
        Validates if the team type provided for a person is valid.
        """
        data = request.data
        takim_tipi = data.get('takim_tipi', None)
        password = data.get('password', None)

        # Check if the provided team type is valid (based on TAKIM_TIPLERI)
        valid_team_types = [choice[0] for choice in Personel.TAKIM_TIPLERI]
        if takim_tipi not in valid_team_types:
            return Response(
                {"error": f"Invalid team type. Valid options are: {', '.join(valid_team_types)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the person and set hashed password
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        personel = serializer.save()
        if password:
            personel.set_password(password)  # Hash the password
            personel.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MontajViewSet(viewsets.ViewSet):
    """
    Handles the assembly process where compatible parts are combined to produce an aircraft.
    """
    def create(self, request):
        """
        Produces an aircraft by combining compatible parts and deducting inventory.
        """
        data = request.data
        ucak_tipi = data.get('isim', None)
        parca_ids = data.get('parcalar', [])

        # Check if all required parts are available
        missing_parts = []
        for parca_id in parca_ids:
            try:
                parca = Parca.objects.get(id=parca_id)
                if parca.stok_adedi < 1:
                    missing_parts.append(parca.tip)
            except Parca.DoesNotExist:
                return Response(
                    {"error": f"Part with ID {parca_id} does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if missing_parts:
            return Response(
                {"error": "Missing parts!", "missing_parts": missing_parts},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct stock and create the aircraft
        for parca_id in parca_ids:
            parca = Parca.objects.get(id=parca_id)
            parca.stok_adedi -= 1
            parca.save()

        ucak = Ucak.objects.create(isim=ucak_tipi, stok_adedi=1)
        ucak.parcalar.set(parca_ids)
        ucak.save()

        return Response({"message": "Aircraft successfully produced!", "aircraft_id": ucak.id})


class EnvanterViewSet(viewsets.ViewSet):
    """
    Lists all parts with insufficient stock.
    """
    def list(self, request):
        """
        Returns a list of parts where stock is less than or equal to zero.
        """
        insufficient_parts = Parca.objects.filter(stok_adedi__lte=0)
        serializer = ParcaSerializer(insufficient_parts, many=True)
        return Response(serializer.data)


class RaporlamaViewSet(viewsets.ViewSet):
    """
    Generates reports on used parts and their associated aircraft.
    """
    def list(self, request):
        """
        Returns a detailed list of parts used and the aircraft they are associated with.
        """
        used_parts = UcakParca.objects.all()
        data = [
            {
                "aircraft": part.ucak.isim,
                "part": part.parca.tip,
                "quantity": part.adet
            }
            for part in used_parts
        ]
        return Response(data)
