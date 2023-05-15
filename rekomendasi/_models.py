from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.def 
class User(AbstractUser):
    ROLE_CHOICES = (
        ("M", "Mahasiswa"),
        ("D", "Dosen")
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class Peminatan(models.Model):
    PEMINATAN_CHOICES = (
        ("M", "Murni"),
        ("P", "Pemodelan"),
        ("K", "Komputasi"),
    )
    nama = models.CharField(max_length=20, choices=PEMINATAN_CHOICES)


class Kelas(models.Model):
    KELAS_CHOICES = (
        ("B", "Bioinformatika"),
        ("DS", "Sains Data"),
        ("P", "Pemodelan"),
        ("PDS", "PD Stokastik"),
        ("Graf", "Graf"),
        ("RO", "Riset Operasi"),
        ("Geo", "Geometri"),
        ("Alj", "Aljabar"),
        ("Anal", "Analisis"),
    )
    kelas = models.CharField(max_length=30, choices=KELAS_CHOICES)
    partisipan = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mengikuti_kelas")
    

class Partisipasi_Dosen(models.Model):
    dosen = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mengajar_kelas")
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name="partisipasi_kelas")


class Partisipasi_Mahasiswa(models.Model):
    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nilai")
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name="nilai")
    nilai = models.IntegerField(default=0)
    

class Run(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="runs_created")
    partisipan_mahasiswa = models.ForeignKey(Partisipasi_Mahasiswa, on_delete=models.CASCADE, related_name="run")
    partisipan_dosen = models.ForeignKey(Partisipasi_Dosen, on_delete=models.CASCADE, related_name="run")
    RUN_STATUS = (
        ("P", "Pending"),
        ("F", "Finished")
    )
    status = models.CharField(max_length=15, choices=RUN_STATUS)
    
    def kelas(self):
        return ["Bioinformatika", "Sains Data", "Pemodelan", "PD Stokastik", "Graf", "Riset Operasi", "Geometri", "Aljabar", "Analisis"]