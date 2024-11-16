from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Parca

User = get_user_model()

class ParcaViewSetTests(APITestCase):
    def setUp(self):
        """
        Runs before each test. Sets up the required users and parts for testing.
        """
        # Users
        self.kanat_user = User.objects.create_user(username="kanat_user", password="password", takim_tipi="KANAT")
        self.govde_user = User.objects.create_user(username="govde_user", password="password", takim_tipi="GOVDE")

        # Parts
        self.parca_kanat = Parca.objects.create(tip="KANAT", stok_adedi=5, ucak_tipi="TB2")
        self.parca_govde = Parca.objects.create(tip="GOVDE", stok_adedi=3, ucak_tipi="TB3")

    def test_reduce_stock_success(self):
        """
        A user with the correct team type can successfully reduce the stock of a part.
        """
        self.client.login(username="kanat_user", password="password")

        response = self.client.put(f"/api/parcalar/{self.parca_kanat.id}/update_stock/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.parca_kanat.refresh_from_db()
        self.assertEqual(self.parca_kanat.stok_adedi, 4)

    def test_reduce_stock_zero(self):
        """
        If a part's stock is zero, reducing it further should be rejected.
        """
        self.client.login(username="govde_user", password="password")
        self.parca_govde.stok_adedi = 0
        self.parca_govde.save()

        response = self.client.put(f"/api/parcalar/{self.parca_govde.id}/update_stock/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Stok zaten sıfır, daha fazla azaltılamaz.")

    def test_reduce_stock_wrong_team(self):
        """
        A user trying to reduce the stock of a part that does not belong to their team type should be rejected.
        """
        self.client.login(username="govde_user", password="password")

        response = self.client.put(f"/api/parcalar/{self.parca_kanat.id}/update_stock/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"],
            "Sadece GOVDE tipi parça stoklarını azaltabilirsiniz."
        )

    def test_create_part_wrong_team(self):
        """
        A user trying to create a part that does not match their team type should be rejected.
        """
        self.client.login(username="govde_user", password="password")

        data = {
            "tip": "KANAT",
            "stok_adedi": 5,
            "ucak_tipi": "TB2",
        }
        response = self.client.post("/api/parcalar/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Sadece GOVDE tipi parça üretebilirsiniz.")
