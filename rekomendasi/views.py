from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

from .models import User, Kelas, Nilai, Pengajar, Peminatan, Run, Run_Results, Partisipasi_Dosen, Partisipasi_Mahasiswa
import json

# Create your views here.
def index(request):
    if request.method == "POST":
        new_run = Run.objects.create(author=request.user, status="P")
        return render(request, "rekomendasi/run.html", {
            "run": new_run
        })
    
    available_runs = Run.objects.filter(status="P")
    finished_runs = Run.objects.filter(status="F")
    return render(request, "rekomendasi/index.html", {
        "available_runs": available_runs,
        "finished_runs": finished_runs
    })
    

def login_view(request):
  if request.method == "POST":

      # Attempt to sign user in
      username = request.POST["username"]
      password = request.POST["password"]
      user = authenticate(request, username=username, password=password)

      # Check if authentication successful
      if user is not None:
          login(request, user)
          return HttpResponseRedirect(reverse("index"))
      else:
          return render(request, "rekomendasi/login.html", {
              "message": "Invalid username and/or password."
          })
  else:
      return render(request, "rekomendasi/login.html")


def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("index"))


def register(request):
  if request.method == "POST":
      username = request.POST["username"]
      email = request.POST["email"]
      role = request.POST["role"]

      # Ensure password matches confirmation
      password = request.POST["password"]
      confirmation = request.POST["confirmation"]
      if password != confirmation:
          return render(request, "rekomendasi/register.html", {
              "message": "Passwords must match."
          })

      # Attempt to create new user
      try:
          user = User.objects.create_user(username, email, password, role=role)
          user.save()
      except IntegrityError:
          return render(request, "rekomendasi/register.html", {
              "message": "Username already taken."
          })
      login(request, user)
      return HttpResponseRedirect(reverse("index"))
  else:
      return render(request, "rekomendasi/register.html")


def profile(request, profile_username):
    user_profile = User.objects.get(username=profile_username)
    daftar_kelas = Kelas.objects.all()
    daftar_peminatan = {val: key for (key, val) in dict(Peminatan.PEMINATAN_CHOICES).items()}
    
    user_form = None
    if request.user == user_profile:
        # form ngisi nilai mahasiswa
        if request.user.role == "M":
            user_form = "M"
        # form ngisi nilai dosen
        if request.user.role == "D":
            user_form = "D"
            
    return render(request, "rekomendasi/profile.html", {
        "user_profile": user_profile,
        "daftar_kelas": daftar_kelas,
        "daftar_peminatan": daftar_peminatan.keys(),
        "user_form": user_form
    })
    

def profile_save(request, profile_username):
    if request.method == "POST":
        list_peminatan = []
        for key in request.POST.keys():
            if 'p-' in key:
                list_peminatan.append(key[2:])
                
        print(request.POST)
        daftar_peminatan = {val: key for (key, val) in dict(Peminatan.PEMINATAN_CHOICES).items()}
        d = Peminatan.objects.filter(user=request.user).delete()
        for peminatan in list_peminatan:
            p = Peminatan.objects.create(user=request.user, nama=daftar_peminatan[peminatan])
            p.save()
        d = Nilai.objects.filter(mahasiswa=request.user).delete()
        
        # process form mahasiswa
        if request.user.role == "M":
            for kelas in Kelas.objects.all():
                nilai = int(request.POST.get(kelas.nama))
                n = Nilai.objects.create(mahasiswa=request.user, kelas=kelas, nilai=nilai)
                n.save()
        
        # process form dosen
        elif request.user.role == "D":
            list_kelas_yang_diajar = []
            for key in request.POST.keys():
                if 'k-' in key:
                    kelas = Kelas.objects.get(nama=key[2:])
                    list_kelas_yang_diajar.append(kelas)
                    
            k = Pengajar.objects.filter(dosen=request.user).delete()
            for kelas in list_kelas_yang_diajar:
                k = Pengajar.objects.create(dosen=request.user, kelas=kelas)
                k.save()
    
    
    return HttpResponseRedirect(reverse("profile", args=(profile_username, )))

    
def run(request, run_id):
    run = Run.objects.get(id=run_id)
    if request.user.is_authenticated:
        took_all_classes = request.user.kelas_diambil.all().count() == Kelas.objects.all().count()
    else:
        took_all_classes = None
    message = None
    # register participation
    if request.method == "POST":
        if request.user.role == "D":
            par = Partisipasi_Dosen.objects.create(dosen=request.user, run=run)
        elif request.user.role == "M":
            par = Partisipasi_Mahasiswa.objects.create(mahasiswa=request.user, run=run)
        message = f"{request.user.username} have been added to the run!"
        par.save()
        
    return render(request, "rekomendasi/run.html", {
        "run": run,
        "message": message,
        "run_is_finished": True if run.status == "F" else False,
        "took_all_classes": took_all_classes,
    })
    

@login_required(login_url="login")
def run_create(request):
    name = request.POST.get("nama-run")
    new_run = Run.objects.create(name=name, author=request.user, status="P")
    new_run_id = new_run.id
    return HttpResponseRedirect(reverse("run", args=(new_run_id,)))


@login_required(login_url="login")
def run_join(request, run_id):
    run = Run.objects.get(id=run_id)
    if request.user.role == "M":
        o = Partisipasi_Mahasiswa.objects.create(mahasiswa=request.user, run=run)
    elif request.user.role == "D":
        o = Partisipasi_Dosen.objects.create(dosen=request.user, run=run)
    o.save()
    return HttpResponseRedirect(reverse("run", args=(run_id,)))


@login_required(login_url="login")
def run_leave(request, run_id):
    run = Run.objects.get(id=run_id)
    if request.user.role == "M":
        o = Partisipasi_Mahasiswa.objects.get(mahasiswa=request.user, run=run)
    elif request.user.role == "D":
        o = Partisipasi_Dosen.objects.get(dosen=request.user, run=run)
    o.delete()
    return HttpResponseRedirect(reverse("run", args=(run_id,)))
    

@login_required(login_url="login")
def run_finish(request, run_id):
    run = Run.objects.get(id=run_id)
    if request.user == run.author:
        print("Run Finished")
        from .utils import construct_inputs, Kruskal, Hungarian
        class_objects = Kelas.objects.all()
        df_weight_matrix = construct_inputs(run, class_objects)
        kruskal_result, _, _, _  = Kruskal(df_weight_matrix)
        hungarian_result = Hungarian(df_weight_matrix)
        results = {}
        results["kruskal"] = kruskal_result
        results["hungarian"] = hungarian_result
        results = json.dumps(results)
        ss = json.loads(results)
        run_results = Run_Results.objects.create(run=run, results=results)
        run_results.save()
        # ss = run.results.all().first().get_results_as_dict()
        # print(dir(run))
        # return JsonResponse(ss, safe=False)
        run.status = "F"
        run.save()
        message = "Run finished"
    else:
        message = "Only the run's author can finish the run"
    return render(request, "rekomendasi/run.html", {
        "run": run,
        "message": message,
        "run_is_finished": True,
    })
