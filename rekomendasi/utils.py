import pprint
import numpy as np
import pandas as pd


def compute_edge_weights(data_dosen, data_mahasiswa, kelas_tersedia):
    total_dosen = len(data_dosen)
    total_mahasiswa = len(data_mahasiswa)
    bobot_total_np = np.zeros([total_mahasiswa, total_dosen])
    bobot_total_df = pd.DataFrame(bobot_total_np, index=data_mahasiswa.keys(), columns=data_dosen.keys())
    
    # json
    bobot_total_json = {}
    
    for idx_mahasiswa, (mahasiswa, mhs_data) in enumerate(data_mahasiswa.items()):
        bobot_total_json[mahasiswa] = {}
        for idx_dosen, (dosen, d_data) in enumerate(data_dosen.items()):
            # proses data peminatan
            peminatan_dosen = set(d_data["peminatan"])
            peminatan_mahasiswa = set(mhs_data["peminatan"])
            bobot_peminatan = len(peminatan_dosen.intersection(peminatan_mahasiswa))
            
            # proses data kelas & nilai
            partisipasi_dosen = [1 if kelas in d_data["kelas"] else 0 for kelas in kelas_tersedia]
            nilai_mahasiswa = [mhs_data["nilai"][kelas] for kelas in kelas_tersedia]
            bobot_kelas = np.dot(partisipasi_dosen, nilai_mahasiswa) / len(kelas_tersedia)
            
            # proses bobot total dalam bentuk np.array
            bobot_total_np[idx_mahasiswa][idx_dosen] = np.floor(bobot_kelas * np.log(1 + bobot_peminatan))
            
            # proses bobot total dalam bentuk json
            bobot_total_json[mahasiswa][dosen] = np.floor(bobot_kelas * np.log(1 + bobot_peminatan))
            
            # proses bobot total dalam bentuk pd.DataFrame
            bobot_total_df.loc[mahasiswa, dosen] = np.floor(bobot_kelas * np.log(1 + bobot_peminatan))
            
    return bobot_total_df, bobot_total_np, bobot_total_json


def construct_inputs(run_object, class_objects):
    # create dosen dict
    dosen_dict = {}
    for dosen in run_object.partisipan_dosen.all():
        dosen_dict[dosen.dosen.username.capitalize()] = {}
        dosen_dict[dosen.dosen.username.capitalize()]["peminatan"] = [peminatan.get_nama_display() for peminatan in dosen.dosen.peminatan.all()]
        dosen_dict[dosen.dosen.username.capitalize()]["kelas"] = [kelas.kelas.nama for kelas in dosen.dosen.kelas_diajar.all()]
        
    # create mahasiswa dict 
    mahasiswa_dict = {}
    for mahasiswa in run_object.partisipan_mahasiswa.all():
        mahasiswa_dict[mahasiswa.mahasiswa.username.capitalize()] = {}
        mahasiswa_dict[mahasiswa.mahasiswa.username.capitalize()]["peminatan"] = [peminatan.get_nama_display() for peminatan in mahasiswa.mahasiswa.peminatan.all()]
        mahasiswa_dict[mahasiswa.mahasiswa.username.capitalize()]["nilai"] = {}
        for kelas in mahasiswa.mahasiswa.kelas_diambil.all():
            mahasiswa_dict[mahasiswa.mahasiswa.username.capitalize()]["nilai"][kelas.kelas.nama] = kelas.nilai
    
    kelas_tersedia = [kelas.nama for kelas in class_objects]
    bobot_total_df, _, _, = compute_edge_weights(data_dosen=dosen_dict, data_mahasiswa=mahasiswa_dict, kelas_tersedia=kelas_tersedia)
    
    return bobot_total_df


def Kruskal(df_bobot):
    df_bobot_proses = df_bobot.copy()
    max_mahasiswa = df_bobot.shape[0]
    max_dosen = df_bobot.shape[1]
    
    vertex_mahasiswa = [f"M_{i}" for i in range(max_mahasiswa)]
    vertex_dosen = [f"D_{i}" for i in range(max_dosen)]
    total_vertices = vertex_mahasiswa + vertex_dosen
    
    tree = []
    bucket_1 = []
    bucket_2 = []
    
    # looping all possible edges which is len_rows * len_columns
    for _ in range(max_mahasiswa * max_dosen):
        # get i,j of max value of the weight matrix
        ## thanks: https://stackoverflow.com/questions/48016629/get-column-and-row-index-for-highest-value-in-dataframe-pandas
        i_j = df_bobot_proses.stack().index[np.argmax(df_bobot_proses.values)] # th
        # to prevent multiple checking of the same edge, assign the value to -1
        df_bobot_proses.loc[i_j] = -1
        
        # check 4 possibilities
        # case 1: if both endpoints of this edge are in the same bucket
        if (i_j[0] in bucket_1 and i_j[1] in bucket_1) or \
           (i_j[0] in bucket_2 and i_j[1] in bucket_2):
            continue
        
        # case 2: one endpoint of this edge is in a bucket, and the other endpoint is not in any bucket
        elif (i_j[0] in bucket_1 and i_j[1] not in bucket_1 + bucket_2) or \
            (i_j[0] not in bucket_1 + bucket_2 and i_j[1] in bucket_1) or \
            (i_j[0] in bucket_2 and i_j[1] not in bucket_1 + bucket_2) or \
            (i_j[0] not in bucket_1 + bucket_2 and i_j[1] in bucket_2):
            tree.append(i_j)
            if i_j[0] in bucket_1:
                bucket_1.append(i_j[1])
            elif i_j[0] in bucket_2:
                bucket_2.append(i_j[1])
            elif i_j[1] in bucket_1:
                bucket_1.append(i_j[0])
            elif i_j[1] in bucket_2:
                bucket_2.append(i_j[0])

        # case 3: neither endpoint is in any bucket
        elif i_j[0] not in bucket_1 and i_j[1] not in bucket_2 and \
            i_j[0] not in bucket_2 and i_j[1] not in bucket_1:
            tree.append(i_j)
            if len(bucket_1) != 0:
                bucket_2.append(i_j[0])
                bucket_2.append(i_j[1])
            else:
                bucket_1.append(i_j[0])
                bucket_1.append(i_j[1])
            
        # case 4: each endpoint is in a different bucket
        elif (i_j[0] in bucket_1 and i_j[1] in bucket_2) or \
            (i_j[0] in bucket_2 and i_j[1] in bucket_1):
            tree.append(i_j)
            bucket_1 = bucket_1 + bucket_2
            bucket_2 = []
            
        # if all the vertices of the graph are in one bucket or if the number of assigned edges equals to 
        # the number of vertices less one, stop the algorithm since spanning tree is formed
        if (total_vertices in bucket_1) or \
           (total_vertices in bucket_2) or \
           len(tree) == len(total_vertices) - 1:
            break

    # construct assignment dict
    assignment_dict = {}
    for mhs, dosen in tree:
        if mhs not in assignment_dict.keys():
            assignment_dict[mhs] = []
        assignment_dict[mhs].append(dosen)
    
    return assignment_dict, tree, bucket_1, bucket_2


def balanced_hungarian(df_bobot):
    assert df_bobot.shape[0] == df_bobot.shape[1]
    assert type(df_bobot) == pd.DataFrame
    df_bobot_dosen = df_bobot.columns
    df_bobot_mahasiswa = df_bobot.index
    
    # phase 1 - reduction phase
        # row reduction 
        # column reduction
    
    min_each_row = df_bobot.min(axis=1)
    df_bobot = df_bobot.subtract(min_each_row, axis=0)
    
    min_each_column = df_bobot.min(axis=0)
    df_bobot = df_bobot.subtract(min_each_column, axis=1)
    
    # phase 2 - optimization
        # 1 - draw a min. number of lines that covers all the zeros in the matrix
            # row scanning
            # column scanning
        # 2 - check if num. of masker == num. of rows/columns of the matrix
            # if yes the algorithm is finished and go to step 5
            # else continue to step 3
        # 3 - identify the minimum value of the undeleted cell values
        # 4 - go to step 1
        # 5 - the assignment has been found. finish the algorithm
        
    df_scan = df_bobot.copy()
    while True:
        pairs = []
        column_line_marker = []
        row_line_marker = []
        
        # while zeros in df exists do row scanning and column scanning. if 0 still exists, repeat
        _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
        while _temp_df_with_line.where(_temp_df_with_line == 0).count().sum() > 0:
            # print("\n", "="*100, "\n")
            # print(_temp_df_with_line)
            # print("Column line marker:", column_line_marker)
            # print("Row line marker:", row_line_marker)
            # print("\n", "="*100, "\n")
            
            _prev_temp_df_with_line = _temp_df_with_line.copy()
            
            # row scanning
            for row in _temp_df_with_line.index:
                _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
                num_of_zeros = _temp_df_with_line.loc[row, :].where(_temp_df_with_line.loc[row, :] == 0).count()
                if num_of_zeros == 1:
                    column = _temp_df_with_line.loc[row, :].where(_temp_df_with_line.loc[row, :] == 0).dropna().index[0]
                    if (row, column) not in pairs:
                        column_line_marker.append(column)
                        pairs.append((row, column))

            # column scanning
            for column in _temp_df_with_line.columns:
                if column in column_line_marker:
                    # the column is already marked by vertical line
                    continue
                _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
                num_of_zeros = _temp_df_with_line.loc[:, column].where(_temp_df_with_line.loc[:, column] == 0).count()
                if num_of_zeros == 1:
                    row = _temp_df_with_line.loc[:, column].where(_temp_df_with_line.loc[:, column] == 0).dropna().index[0]
                    if (row, column) not in pairs:
                        row_line_marker.append(row)
                        pairs.append((row, column))
            
            _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
            if _temp_df_with_line.equals(_prev_temp_df_with_line):
                # print("Matriks tak berubah dari step sebelumnya. Mungkin ada yg free-choices")
                # ambil pilihan yang pertama dari scan row/kolom
                for row in _temp_df_with_line.index:
                    _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
                    column = _temp_df_with_line.loc[row, :].where(_temp_df_with_line.loc[row, :] == 0).dropna().index[0]
                    if (row, column) not in pairs:
                        column_line_marker.append(column)
                        pairs.append((row, column))
            
                ### BLOCK - NOT NEEDED HOPEFULLY ###
                # _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
                # _temp_df_with_line.where(_temp_df_with_line == 0).count().sum() > 0
                # for column in _temp_df_with_line.columns:   
                #     if column in column_line_marker:
                #         # the column is already marked by vertical line
                #         continue
                #     _temp_df_with_line = df_scan.drop(columns=column_line_marker, index=row_line_marker)
                #     try:
                #         row = _temp_df_with_line.loc[:, column].where(_temp_df_with_line.loc[:, column] == 0).dropna().index[0]
                #     except:
                #         # no more column with 0
                #         break
                #     if (row, column) not in pairs:
                #         row_line_marker.append(row)
                #         pairs.append((row, column))
                ### END BOCK ###

        # # if the number of pair equals to the number of row/columns
        # print("Pairs:", pairs)
        if len(pairs) == df_bobot.shape[0]:
            break
            
        # line drawing in the matrix is illustrated by dropping necessary rows/columns
        # print(f"DF delete rows: ({row_line_marker})")
        # print(df_scan)
        df_undeleted_cell_values = df_scan.drop(index=row_line_marker, axis=0)
        # print(f"DF delete columns: ({column_line_marker})")
        # print(df_undeleted_cell_values)
        df_undeleted_cell_values = df_undeleted_cell_values.drop(columns=column_line_marker, axis=1)
        # print("DF undeleted cell values")
        # print(df_undeleted_cell_values)

        min_value_of_undeleted_cells = min(df_undeleted_cell_values.min().values)
        # add minimum value to the intersecting points of horizontal and vertical lines
        intersecting_points = [(row, column) for row in row_line_marker for column in column_line_marker]
        for point in intersecting_points:
            df_scan.loc[point] += min_value_of_undeleted_cells

        # remove minimum value from the undeleted cell values
        df_scan.loc[df_undeleted_cell_values.index, df_undeleted_cell_values.columns] -= min_value_of_undeleted_cells
        
        # print(df_scan)
        # print("\n", "="*100, "\n")
    return df_scan, pairs


def Hungarian(df_bobot):
    _index_dosen = df_bobot.columns
    _index_mahasiswa = df_bobot.index
    jumlah_dosen = len(df_bobot.columns)
    jumlah_mahasiswa = len(df_bobot.index)
    _df_bobot_proses = df_bobot.copy()
    _df_bobot_proses = _df_bobot_proses.values.max() - _df_bobot_proses
    
    assignment_dict = {}
    for mhs in _index_mahasiswa:
        assignment_dict[mhs] = []
    
    batch = 0
    num_to_expand = jumlah_mahasiswa - jumlah_dosen
    
    while num_to_expand > 0:
        batch += 1
        batch_dict = {}
        
        # get rata-rata nilai mahasiswa
        for mhs in _df_bobot_proses.index:
            batch_dict[mhs] = _df_bobot_proses.loc[mhs, :].sum() / _df_bobot_proses.sum().sum()
        batch_list = sorted(batch_dict.items(), key=lambda x: x[1], reverse=True)
        
        # filter mahasiswa dengan bobot tertinggi
        batch_mhs = dict(batch_list[:jumlah_dosen])
        _df_bobot_proses_hungarian = _df_bobot_proses.loc[list(batch_mhs.keys()), :]
        
        # do hungarian
        _df_bobot_assignment, _pairs = balanced_hungarian(_df_bobot_proses_hungarian)
        
        # store the results
        for (mhs, dosen) in _pairs:
            assignment_dict[mhs].append(dosen)
                
        # one-liner hack [assignment_dict[mhs].append(dosen) for (mhs, dosen) in _pairs]
        
        # remove already paired students
        _df_bobot_proses = _df_bobot_proses.drop(index=batch_mhs.keys())
        
        # get the remaining mahasiswa for next batch
        jumlah_mahasiswa = _df_bobot_proses.index.shape[0]
        num_to_expand = jumlah_mahasiswa - jumlah_dosen
        
    # do final hungarian if jumlah_mahasiswa < jumlah_dosen
    if num_to_expand < 0:
        last_batch_dict = {}
        for dosen in _df_bobot_proses.columns:
            last_batch_dict[dosen] = _df_bobot_proses.loc[:, dosen].sum() / _df_bobot_proses.sum().sum()
        last_batch_list = sorted(last_batch_dict.items(), key=lambda x: x[1], reverse=True)
        
        # filter dosen dengan bobot tertinggi
        batch_dosen = dict(last_batch_list[:jumlah_mahasiswa])
        
        # do hungarian
        _df_bobot_proses_hungarian = _df_bobot_proses.loc[:, list(batch_dosen.keys())]
        _df_bobot_assignment, _pairs = balanced_hungarian(_df_bobot_proses_hungarian)
        
        # store the results
        for (mhs, dosen) in _pairs:
            assignment_dict[mhs].append(dosen)
    
    return assignment_dict
