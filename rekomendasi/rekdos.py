import hungarian, spanning_tree
import numpy as np
import json
import pprint

P = ["Murni", "Pemodelan", "Komputasi"]
K = ["Bioinformatika", "Sains Data", "Pemodelan", "PD Stokastik", "Graf", "Riset Operasi", "Geometri", "Aljabar", "Analisis"]

data_dosen = json.load(open("src/data_dosen.json", mode='rb'))
data_mahasiswa = json.load(open("src/data_mahasiswa.json", mode='rb'))


def compute_edge_weights(data_dosen, data_mahasiswa):
    total_dosen = len(data_dosen)
    total_mahasiswa = len(data_mahasiswa)
    bobot_total = np.zeros([total_mahasiswa, total_dosen])
    
    # # json
    bobot_total_json = {}
    
    for idx_mahasiswa, (mahasiswa, mhs_data) in enumerate(data_mahasiswa.items()):
        bobot_total_json[mahasiswa] = {}
        for idx_dosen, (dosen, d_data) in enumerate(data_dosen.items()):
            # proses data peminatan
            peminatan_dosen = set(d_data["peminatan"])
            peminatan_mahasiswa = set(mhs_data["peminatan"])
            bobot_peminatan = len(peminatan_dosen.intersection(peminatan_mahasiswa))
            
            # proses data kelas & nilai
            partisipasi_dosen = [1 if kelas in d_data["kelas"] else 0 for kelas in K]
            nilai_mahasiswa = [mhs_data["nilai"][kelas] for kelas in K]
            bobot_kelas = np.dot(partisipasi_dosen, nilai_mahasiswa) / len(K)
            
            # proses bobot total
            bobot_total[idx_mahasiswa][idx_dosen] = np.floor(bobot_kelas * np.log(1 + bobot_peminatan))
            
            # bikin json
            bobot_total_json[mahasiswa][dosen] = np.floor(bobot_kelas * np.log(1 + bobot_peminatan))
            
    return bobot_total, bobot_total_json


test_weights = np.array([
    [10, 21, 32, 11],
    [42, 2, 33, 21],
    [100, 21, 33, 24],
    [11, 12, 32, 22]
])


bobot_total, bobot_total_json = compute_edge_weights(data_dosen=data_dosen, data_mahasiswa=data_mahasiswa)
pprint.pprint(bobot_total_json)
print("==== MATRIX BOBOT ===")
print(bobot_total)

hasil_hungarian = hungarian.Hungarian(bobot_total)
print("==== HASIL HUNGARIAN ===")
print(bobot_total)

hasil_kruskal, _, _ = spanning_tree.Kruskal(bobot_total)
print("==== HASIL KRUSKAL ===")
print(hasil_kruskal)


