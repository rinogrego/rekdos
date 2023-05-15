from django.contrib import admin
from .models import User, Peminatan, Kelas, Nilai, Pengajar, Run, Run_Results, Partisipasi_Dosen, Partisipasi_Mahasiswa

# Register your models here.

class PeminatanInline(admin.TabularInline):
    model = Peminatan
  
  
class NilaiInline(admin.TabularInline):
    model = Nilai


class PengajarInline(admin.TabularInline):
    model = Pengajar
    

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "role", "minat", "mengajar", "kelas")
    inlines = [PeminatanInline, NilaiInline, PengajarInline]
    
  
class KelasAdmin(admin.ModelAdmin):
    list_display = ("nama", "mahasiswa", "dosen")
    inlines = [NilaiInline, PengajarInline]


class NilaiAdmin(admin.ModelAdmin):
    list_display = ("mahasiswa", "kelas", "nilai",)
    

class PengajarAdmin(admin.ModelAdmin):
    list_display = ("dosen", "kelas")
    

class PartisipasiMahasiswaInline(admin.TabularInline):
    model = Partisipasi_Mahasiswa


class PartisipasiDosenInline(admin.TabularInline):
    model = Partisipasi_Dosen


class RunResultsInline(admin.TabularInline):
    model = Run_Results


class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "author_role", "status", "mahasiswa", "dosen")
    inlines = [PartisipasiMahasiswaInline, PartisipasiDosenInline, RunResultsInline]
    

class RunResultsAdmin(admin.ModelAdmin):
    list_display = ("id", )

  
admin.site.register(User, UserAdmin)
admin.site.register(Kelas, KelasAdmin)
admin.site.register(Pengajar, PengajarAdmin)
admin.site.register(Nilai, NilaiAdmin)
admin.site.register(Run, RunAdmin)
admin.site.register(Run_Results, RunResultsAdmin)