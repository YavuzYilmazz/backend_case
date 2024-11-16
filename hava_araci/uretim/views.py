from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework.decorators import action
from django.contrib.auth.views import LoginView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Parca, Ucak, Takim, Personel, UcakParca
from .serializers import ParcaSerializer, UcakSerializer, TakimSerializer, PersonelSerializer
@login_required
def dashboard(request):
    """
    Dashboard for different team types.
    """
    user = request.user
    team_type = user.takim_tipi
    all_parts = Parca.objects.all()

    # Montaj takımında olan kullanıcılar uçakları da görür
    ucaklar = Ucak.objects.prefetch_related('parcalar') if team_type == "MONTAJ" else None

    context = {
        "team_type": team_type,
        "all_parts": all_parts,
        "ucaklar": ucaklar,
    }
    return render(request, "uretim/dashboard.html", context)

class SimpleLoginView(LoginView):
    """
    Custom login view to authenticate and redirect.
    """
    def form_valid(self, form):
        user = authenticate(
            self.request,
            username=form.cleaned_data.get("username"),
            password=form.cleaned_data.get("password"),
        )
        if user:
            login(self.request, user)
            return redirect("/dashboard")
        else:
            form.add_error(None, "Invalid credentials")
            return self.form_invalid(form)



class PersonelViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for personnel.
    """
    queryset = Personel.objects.all()
    serializer_class = PersonelSerializer

    def create(self, request, *args, **kwargs):
        """
        Validates team type and creates personnel.
        """
        data = request.data
        takim_tipi = data.get("takim_tipi")
        password = data.get("password")

        valid_team_types = [choice[0] for choice in Personel.TAKIM_TIPLERI]
        if takim_tipi not in valid_team_types:
            return Response(
                {"error": f"Invalid team type. Valid options: {', '.join(valid_team_types)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        personel = serializer.save()
        if password:
            personel.set_password(password)
            personel.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ParcaViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for parts.
    """
    queryset = Parca.objects.all()
    serializer_class = ParcaSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates or updates a part.
        """
        data = request.data
        tip = data.get("tip")
        ucak_tipi = data.get("ucak_tipi")
        stok_adedi = int(data.get("stok_adedi", 0))

        try:
            existing_part = Parca.objects.get(tip=tip, ucak_tipi=ucak_tipi)
            existing_part.stok_adedi += stok_adedi
            existing_part.save()
            serializer = self.get_serializer(existing_part)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Parca.DoesNotExist:
            return super().create(request, *args, **kwargs)


class TakimViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for teams.
    """
    queryset = Takim.objects.all()
    serializer_class = TakimSerializer

class UcakViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for aircraft and assembly.
    """
    queryset = Ucak.objects.prefetch_related('parcalar')
    serializer_class = UcakSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new aircraft or updates stock if the same type already exists.
        """
        data = request.data
        print("Gelen veri:", data)
        ucak_tipi = data.get("isim")
        parca_ids = [int(pid) for pid in data.getlist("parcalar[]")]
        print("Parça ID'leri:", parca_ids)

        eksik_parcalar = []
        selected_parts = []

        # Parça kontrolü
        for parca_id in parca_ids:
            try:
                parca = Parca.objects.get(id=parca_id)
                if parca.stok_adedi < 1:
                    eksik_parcalar.append(parca.tip)
                else:
                    selected_parts.append(parca)
            except Parca.DoesNotExist:
                return Response(
                    {"error": f"Parça ID {parca_id} mevcut değil."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if eksik_parcalar:
            return Response(
                {"error": "Eksik parçalar mevcut!", "missing_parts": eksik_parcalar},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Stok azalt
        for parca in selected_parts:
            parca.stok_adedi -= 1
            parca.save()

        # Aynı tip uçak varsa stok artır
        try:
            existing_aircraft = Ucak.objects.get(isim=ucak_tipi)
            existing_aircraft.stok_adedi += 1
            existing_aircraft.save()
            existing_aircraft.parcalar.add(*selected_parts)  # Parçaları ekle
            return Response(
                {"message": f"{ucak_tipi} tipi uçak için stok artırıldı.", "aircraft_id": existing_aircraft.id},
                status=status.HTTP_200_OK,
            )
        except Ucak.DoesNotExist:
            # Yeni uçak oluştur
            ucak = Ucak.objects.create(isim=ucak_tipi, stok_adedi=1)
            ucak.parcalar.set(selected_parts)  # Parçaları ilişkilendir
            return Response(
                {"message": "Uçak başarıyla üretildi!", "aircraft_id": ucak.id},
                status=status.HTTP_201_CREATED,
            )
