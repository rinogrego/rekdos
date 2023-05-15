from django.db import models
from django.contrib.auth.models import AbstractUser

import json

# Create your models here.def
class User(AbstractUser):
    MAHASISWA = "M"
    DOSEN = "D"
    ROLE_CHOICES = (
        (MAHASISWA, "Mahasiswa"),
        (DOSEN, "Dosen")
    )
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default=MAHASISWA)
    
    def __str__(self):
        return self.username
    
    def minat(self):
        return [peminatan.get_nama_display() for peminatan in self.peminatan.all()]
    
    def mengajar(self):
        return [kelas_diajar.kelas for kelas_diajar in self.kelas_diajar.all()]
    
    def kelas(self):
        return [kelas_diambil.kelas for kelas_diambil in self.kelas_diambil.all()]
    
    
# class Bidang_Minat(models.Model):
#     MURNI = "M"
#     PEMODELAN = "P"
#     KOMPUTASI = "K"
#     PEMODELAN_CHOICES = (
#         (MURNI, "Murni"),
#         (PEMODELAN, "Pemodelan"),
#         (KOMPUTASI, "Komputasi")
#     )
#     nama = models.CharField(max_length=2, choices=PEMODELAN_CHOICES)


class Peminatan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peminatan")
    MURNI = "M"
    PEMODELAN = "P"
    KOMPUTASI = "K"
    PEMINATAN_CHOICES = (
        (MURNI, "Murni"),
        (PEMODELAN, "Pemodelan"),
        (KOMPUTASI, "Komputasi")
    )
    nama = models.CharField(max_length=2, choices=PEMINATAN_CHOICES)
    # minat = models.ForeignKey(Bidang_Minat, on_delete=models.CASCADE, related_name="peminat")
    
    def dosen(self):
        return [user for user in self.user.all() if user.role == "D"]
    
    def mahasiswa(self):
        return [user for user in self.user.all() if user.role == "M"]
    

class Kelas(models.Model):
    nama = models.CharField(max_length=30)
    
    def __str__(self):
        return self.nama
    
    def mahasiswa(self):
        return [nilai.mahasiswa for nilai in self.nilai_mahasiswa.all()]
    
    def dosen(self):
        return [pengajar.dosen for pengajar in self.diajar_oleh.all()]


class Nilai(models.Model):
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kelas_diambil")
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name="nilai_mahasiswa")
    nilai = models.FloatField()
    
    def __str__(self):
        return f"{self.kelas} - {self.nilai}"
    

class Pengajar(models.Model):
    dosen = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kelas_diajar")
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name="diajar_oleh")
    

class Run(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="runs_created")
    name = models.CharField(max_length=50)
    RUN_STATUS = (
        ("P", "Pending"),
        ("F", "Finished")
    )
    status = models.CharField(max_length=15, choices=RUN_STATUS)
    datetime = models.DateTimeField(auto_now_add=True)
    
    def author_role(self):
        return self.author.get_role_display()
    
    def mahasiswa(self):
        return [partisipan.mahasiswa for partisipan in self.partisipan_mahasiswa.all()]
    
    def dosen(self):
        return [partisipan.dosen for partisipan in self.partisipan_dosen.all()]
    
    def get_results(self):
        return [result for result in self.results.all()]
    

class Run_Results(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="results")
    results = models.TextField(max_length=100000)
    
    def get_results_as_dict(self):
        # json results: {'kruskal': {'mhs_1': ['dos_1'], 'mhs_2': ['dos_2', 'dos_3']}, 'hungarian': {'mhs_1': ['dos_2'], 'mhs_2': ['dos_1']}}
        # {'mhs_1': {'kruskal': ['dos1', 'dos2'], 'hungarian': ['dos1]}, 'mhs_2': ...}
        results = json.loads(self.results)
        final_results = {}
        for method, res in results.items():
            for mhs, rekdos in res.items():
                if mhs not in final_results.keys():
                    final_results[mhs] = {}
                final_results[mhs][method] = rekdos
        
        return final_results
    
    def get_methods(self):
        results = json.loads(self.results)
        return results.keys()
    

# class Run_Recommendation(models.Model):
#     run_results = models.ForeignKey(Run_Results, on_delete=models.CASCADE, related_name="run_recommendations")
#     mahasiswa = models.ForeignKey(User, on_delete=models.PROTECT, related_name="rekomendasi_dosen")
#     dosen = models.ForeignKey(User, on_delete=models.PROTECT, related_name="rekomendasi_mahasiswa")


class Partisipasi_Dosen(models.Model):
    dosen = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partisipasi_dosen")
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="partisipan_dosen")


class Partisipasi_Mahasiswa(models.Model):
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partisipasi_mahasiswa")
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="partisipan_mahasiswa")

