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
    Displays the dashboard based on the user's team type. 
    Includes missing parts for the assembly team.
    """
    user = request.user
    team_type = user.takim_tipi
    all_parts = Parca.objects.all()

    # Only the assembly team can see all aircraft and missing parts
    ucaklar = Ucak.objects.prefetch_related('parcalar') if team_type == "MONTAJ" else None

    # Checking for missing parts for all aircraft types
    required_parts = ["KANAT", "GOVDE", "AVIYONIK", "KUYRUK"]
    missing_parts = {}  # To hold missing parts grouped by aircraft type

    all_ucak_tipleri = {
        "TB2": ["KANAT", "GOVDE", "KUYRUK", "AVIYONIK"],
        "TB3": ["KANAT", "GOVDE", "KUYRUK", "AVIYONIK"],
        "AKINCI": ["KANAT", "GOVDE", "KUYRUK", "AVIYONIK"],
        "KIZILELMA": ["KANAT", "GOVDE", "KUYRUK", "AVIYONIK"],
    }

    for ucak_tipi in all_ucak_tipleri:
        missing_list = []

        for part_type in required_parts:
            # Check if parts have zero stock or no records
            if not Parca.objects.filter(tip=part_type, ucak_tipi=ucak_tipi).exists():
                # If no records, add to missing list
                missing_list.append(part_type)
            else:
                # Check for parts with zero stock
                zero_stock = Parca.objects.filter(tip=part_type, ucak_tipi=ucak_tipi, stok_adedi=0)
                if zero_stock.exists():
                    missing_list.append(part_type)

        if missing_list:
            # Only add aircraft types with missing parts
            missing_parts[ucak_tipi] = missing_list

    context = {
        "team_type": team_type,
        "all_parts": all_parts,
        "ucaklar": ucaklar,
        "missing_parts": missing_parts,
    }
    return render(request, "uretim/dashboard.html", context)


class SimpleLoginView(LoginView):
    """
    Handles user authentication and redirects to the dashboard upon successful login.
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
            form.add_error(None, "Geçersiz kullanıcı adı veya şifre.")
            return self.form_invalid(form)


class PersonelViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for personnel.
    """
    queryset = Personel.objects.all()
    serializer_class = PersonelSerializer

    def create(self, request, *args, **kwargs):
        """
        Validates the team type and creates a new personnel record.
        """
        data = request.data
        team_type = data.get("takim_tipi")
        password = data.get("password")

        valid_team_types = [choice[0] for choice in Personel.TAKIM_TIPLERI]
        if team_type not in valid_team_types:
            return Response(
                {"error": f"Geçersiz takım tipi. Geçerli seçenekler: {', '.join(valid_team_types)}"},
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
        Allows users to create parts only for their team's type.
        """
        data = request.data
        tip = data.get("tip")
        user = request.user

        # Check if the user is authorized to create this part type
        if user.takim_tipi != tip:
            return Response(
                {"error": f"Sadece {user.takim_tipi} tipi parça üretebilirsiniz."},
                status=status.HTTP_403_FORBIDDEN,
            )

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

    @action(detail=True, methods=['put'])
    def update_stock(self, request, pk=None):
        """
        Reduces the stock of a part by 1 if it's not already zero.
        """
        part = self.get_object()
        user = request.user

        # Ensure the user can only modify parts of their team's type
        if user.takim_tipi != part.tip:
            return Response(
                {"error": f"Sadece {user.takim_tipi} tipi parça stoklarını azaltabilirsiniz."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Reduce stock
        if part.stok_adedi > 0:
            part.stok_adedi -= 1
            part.save()
            return Response(
                {"message": f"{part.tip} parçasının stok miktarı azaltıldı. Kalan stok: {part.stok_adedi}"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Stok zaten sıfır, daha fazla azaltılamaz."},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
        Creates a new aircraft or updates the stock if the same type already exists.
        """
        data = request.data
        ucak_tipi = data.get("isim")
        parca_ids = [int(pid) for pid in data.getlist("parcalar[]")]

        # Required parts for the aircraft
        required_parts = ["KANAT", "GOVDE", "KUYRUK", "AVIYONIK"]

        missing_parts = set()
        invalid_parts = set()
        available_types = set()
        selected_parts = []

        # Validate parts
        for part_id in parca_ids:
            try:
                part = Parca.objects.get(id=part_id)
                if part.ucak_tipi != ucak_tipi:
                    invalid_parts.add(part.tip)
                elif part.stok_adedi < 1:
                    if part.tip not in invalid_parts:
                        missing_parts.add(part.tip)
                else:
                    selected_parts.append(part)
                    available_types.add(part.tip)
            except Parca.DoesNotExist:
                return Response(
                    {"error": f"Parça ID {part_id} mevcut değil."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Check for missing required parts
        for required_type in required_parts:
            if required_type not in available_types and required_type not in invalid_parts:
                missing_parts.add(required_type)

        if missing_parts or invalid_parts:
            return Response(
                {
                    "error": "Eksik veya hatalı parçalar mevcut!",
                    "missing_parts": list(missing_parts),
                    "invalid_parts": list(invalid_parts),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reduce stock
        for part in selected_parts:
            part.stok_adedi -= 1
            part.save()

        # Update stock if the aircraft type exists
        try:
            existing_aircraft = Ucak.objects.get(isim=ucak_tipi)
            existing_aircraft.stok_adedi += 1
            existing_aircraft.save()
            return Response(
                {"message": f"{ucak_tipi} tipi uçak için stok artırıldı.", "aircraft_id": existing_aircraft.id},
                status=status.HTTP_200_OK,
            )
        except Ucak.DoesNotExist:
            # Create new aircraft
            ucak = Ucak.objects.create(isim=ucak_tipi, stok_adedi=1)
            ucak.parcalar.set(selected_parts)
            return Response(
                {"message": "Uçak başarıyla üretildi!", "aircraft_id": ucak.id},
                status=status.HTTP_201_CREATED,
            )
