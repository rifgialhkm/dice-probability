import re

# KAMUS (DATABASE)
# Menerjemahkan kata kunci dari soal ke kode internal aplikasi Anda
# (Ini bagian paling penting dan bisa terus Anda tambah)

KAMUS_EVENT_1_DADU = {
    r'angka genap': ('face_even', None, None),
    r'angka ganjil': ('face_odd', None, None),
    r'angka prima': ('face_prime', None, None),
    r'angka (2|3|4|5|6|1)': ('custom_face', 'eq', r'\1'), # "angka 5"
    r'angka (\d+)': ('custom_face', 'eq', r'\1'),
    r'angka lebih besar dari (\d+)': ('custom_face', 'gt', r'\1'),
    r'angka kurang dari (\d+)': ('custom_face', 'lt', r'\1'),
    r'angka < (\d+)': ('custom_face', 'lt', r'\1'),
    r'angka > (\d+)': ('custom_face', 'gt', r'\1'),
    r'angka ([\=\>\<\!\≥\≤]+) (\d+)': ('custom_face', r'\1', r'\2'), # "angka >= 4"
    r'habis dibagi 3': ('custom_face', 'custom_div_3', None) # Contoh, perlu logika di events.py
    # Jika Anda menambah 'custom_div_3', Anda harus menambahkannya di parse_event_1_dice
}

KAMUS_EVENT_2_DADU = {
    r'jumlah genap': ('sum_even', None, None),
    r'jumlah ganjil': ('sum_odd', None, None),
    r'jumlahnya genap': ('sum_even', None, None),
    r'jumlahnya ganjil': ('sum_odd', None, None),
    r'kedua mata dadu sama': ('same', None, None),
    r'kedua mata dadu beda': ('different', None, None),
    r'kedua dadu genap': ('both_even', None, None),
    r'kedua dadu ganjil': ('both_odd', None, None),
    r'jumlah (2|3|4|5|6|7|8|9|10|11|12)': ('custom_sum', 'eq', r'\1'), # "jumlah 8"
    r'jumlahnya (2|3|4|5|6|7|8|9|10|11|12)': ('custom_sum', 'eq', r'\1'), # "jumlahnya 8"
    r'jumlah (\d+)': ('custom_sum', 'eq', r'\1'),
    r'jumlahnya (\d+)': ('custom_sum', 'eq', r'\1'),
    r'jumlah lebih besar dari (\d+)': ('custom_sum', 'gt', r'\1'),
    r'jumlah kurang dari (\d+)': ('custom_sum', 'lt', r'\1'),
    r'jumlahnya ([\=\>\<\!\≥\≤]+) (\d+)': ('custom_sum', r'\1', r'\2'), # "jumlahnya > 10"
}

# Kamus operator
KAMUS_OPERASI = {
    'atau': 'union',
    'dan': 'intersection',
    'bukan': 'complement',
    'tidak': 'complement'
}

# Fungsi untuk menerjemahkan string kejadian (misal "angka genap")
def _terjemahkan_event(event_str, kamus):
    event_str = event_str.strip()
    for key, (event_type, op, val) in kamus.items():
        # Kita gunakan re.fullmatch agar lebih ketat
        match = re.fullmatch(key, event_str)
        if match:
            # Mengganti placeholder (cth: r'\1') dengan nilai yg ditangkap regex
            real_val = match.expand(val) if val else None
            real_op = match.expand(op) if op else None
            
            if real_op: 
                # Konversi simbol
                real_op = {'=': 'eq', '>': 'gt', '<': 'lt', '≥': 'gte', '≤': 'lte', '!=': 'ne'}.get(real_op, real_op)
                
            return {
                'type': event_type,
                'operator': real_op,
                'value': real_val
            }
    # Jika tidak ada yang cocok sama sekali
    raise ValueError(f"Kejadian '{event_str}' tidak dapat saya pahami.")

# TEMPLATE SOAL (DAFTAR REGEX)
# Dibuat dari yang paling kompleks ke yang paling sederhana
TEMPLATES = [
    # 2 Dadu, 2 Kejadian, Bersyarat: "peluang [B] jika diketahui [A]"
    (re.compile(r".*peluang (.*) (?:jika|bila) diketahui (.*)", re.IGNORECASE), {
        'numDice': 2, 'numEvents': 2, 'operation': 'cond_B_A', 'kamus': KAMUS_EVENT_2_DADU
    }),
    
    # 2 Dadu, 2 Kejadian, Gabungan/Irisan: "peluang [A] (atau|dan) [B]"
    # PERHATIKAN: .* telah diubah menjadi .*? (non-greedy)
    (re.compile(r"(?:dua|2) buah dadu.*?peluang .*?(?:mendapatkan|munculnya) (.*) (atau|dan) (.*)", re.IGNORECASE), {
        'numDice': 2, 'numEvents': 2, 'operation': r'\2', 'kamus': KAMUS_EVENT_2_DADU
    }),
    
    # 1 Dadu, 2 Kejadian, Gabungan/Irisan: "peluang [A] (atau|dan) [B]"
    # PERHATIKAN: .* telah diubah menjadi .*? (non-greedy)
    (re.compile(r"(?:sebuah|1) dadu.*?peluang .*?(?:munculnya|kejadian) (.*) (atau|dan) (.*)", re.IGNORECASE), {
        'numDice': 1, 'numEvents': 2, 'operation': r'\2', 'kamus': KAMUS_EVENT_1_DADU
    }),
    
    # 2 Dadu, 1 Kejadian, Komplementer: "peluang bukan/tidak [A]"
    (re.compile(r"(?:dua|2) buah dadu.*?peluang (bukan|tidak) (.*)", re.IGNORECASE), {
        'numDice': 2, 'numEvents': 1, 'operation': 'complement', 'kamus': KAMUS_EVENT_2_DADU
    }),
    
    # 1 Dadu, 1 Kejadian, Komplementer: "peluang bukan/tidak [A]"
    (re.compile(r"(?:sebuah|1) dadu.*?peluang (bukan|tidak) (.*)", re.IGNORECASE), {
        'numDice': 1, 'numEvents': 1, 'operation': 'complement', 'kamus': KAMUS_EVENT_1_DADU
    }),

    # 2 Dadu, 1 Kejadian: "peluang [A]"
    # PERHATIKAN: .* telah diubah menjadi .*? (non-greedy)
    (re.compile(r"(?:dua|2) buah dadu.*?peluang .*?(?:munculnya|jumlahnya|kejadian|jumlah) (.*)", re.IGNORECASE), {
        'numDice': 2, 'numEvents': 1, 'operation': 'union', 'kamus': KAMUS_EVENT_2_DADU # Operasi default
    }),
    
    # 1 Dadu, 1 Kejadian: "peluang [A]"
    # PERHATIKAN: .* telah diubah menjadi .*? (non-greedy)
    (re.compile(r"(?:sebuah|1) dadu.*?peluang .*?(?:munculnya|angka|kejadian) (.*)", re.IGNORECASE), {
        'numDice': 1, 'numEvents': 1, 'operation': 'union', 'kamus': KAMUS_EVENT_1_DADU
    }),
]

# FUNGSI UTAMA PARSER
def parse_soal(text):
    text = text.lower().strip().replace("?", "").replace(".", "")
    
    for regex, params in TEMPLATES:
        match = regex.match(text)
        if not match:
            continue

        # Jika cocok dengan template
        data = {
            'numDice': params['numDice'],
            'numEvents': params['numEvents'],
        }
        
        kamus = params['kamus']
        
        try:
            # Ekstrak Kejadian A
            if params['operation'] == 'cond_B_A':
                 # Untuk P(B|A), grup 1 adalah B, grup 2 adalah A
                event_b_str = match.group(1).strip()
                event_a_str = match.group(2).strip()
                
                event_a = _terjemahkan_event(event_a_str, kamus)
                event_b = _terjemahkan_event(event_b_str, kamus)
                
                data['operation'] = 'cond_B_A'
                data['eventA'] = event_a['type']
                data['eventAOperator'] = event_a['operator']
                data['eventAValue'] = event_a['value']
                data['eventB'] = event_b['type']
                data['eventBOperator'] = event_b['operator']
                data['eventBValue'] = event_b['value']

            elif data['numEvents'] == 1:
                event_a_str = match.group(1).strip()
                if params['operation'] == 'complement':
                    event_a_str = match.group(2).strip() # "bukan [grup 2]"
                
                event_a = _terjemahkan_event(event_a_str, kamus)
                
                data['operation'] = params['operation']
                data['eventA'] = event_a['type']
                data['eventAOperator'] = event_a['operator']
                data['eventAValue'] = event_a['value']
            
            elif data['numEvents'] == 2:
                event_a_str = match.group(1).strip()
                event_b_str = match.group(3).strip()
                op_str = match.group(2).strip() # "atau" atau "dan"
                
                # --- LOGIKA KONTEKS BARU ---
                # Cek jika event B "incomplete" (cth: "jumlah 8 atau 10")
                if event_b_str.isdigit() and 'jumlah' in event_a_str:
                    event_b_str = 'jumlah ' + event_b_str
                # Cek jika event B "incomplete" (cth: "angka 5 atau 6")
                elif event_b_str.isdigit() and 'angka' in event_a_str:
                     event_b_str = 'angka ' + event_b_str
                # --- AKHIR LOGIKA KONTEKS BARU ---
            
                event_a = _terjemahkan_event(event_a_str, kamus)
                event_b = _terjemahkan_event(event_b_str, kamus)
                
                data['operation'] = KAMUS_OPERASI.get(op_str, 'union')
                data['eventA'] = event_a['type']
                data['eventAOperator'] = event_a['operator']
                data['eventAValue'] = event_a['value']
                data['eventB'] = event_b['type']
                data['eventBOperator'] = event_b['operator']
                data['eventBValue'] = event_b['value']
            
            return data # Sukses parsing!

        except ValueError as e:
            # Jika _terjemahkan_event gagal, lanjut ke template berikutnya
            print(f"Gagal menerjemahkan: {e}") # Untuk debug
            continue 

    # Jika tidak ada template yang cocok
    raise ValueError("Format soal tidak dikenali. Pastikan sesuai template yang ada.")