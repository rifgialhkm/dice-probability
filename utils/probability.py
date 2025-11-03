from .formatters import format_set, fraction_to_string, fraction_to_decimal
import math 
import itertools 

def calculate_union(A, B, C=None):
    if C is None: return sorted(list(set(A) | set(B)))
    else: return sorted(list(set(A) | set(B) | set(C)))

def calculate_intersection(A, B, C=None):
    if C is None: return sorted(list(set(A) & set(B)))
    else: return sorted(list(set(A) & set(B) & set(C)))

def build_calculation_steps(num_dice, num_events, operation, A, A_name, B=None, B_name=None, C=None, C_name=None):
    steps = []
    
    S_size = int(math.pow(6, num_dice))
    show_sets = (num_dice <= 2) 
    
    # Step 1: Ruang Sampel
    step1_content = [
        f"Setiap dadu punya 6 sisi. Karena ada {num_dice} dadu, total kemungkinannya adalah 6 x 6 x ... ({num_dice} kali).",
        f"Total ada <strong>{S_size}</strong> kemungkinan hasil."
    ]
    
    if show_sets:
        S = list(itertools.product(range(1, 7), repeat=num_dice)) if num_dice > 1 else list(range(1,7))
        step1_content.insert(0, f"Semua hasil yang mungkin keluar: {format_set(S)}")
    steps.append({ 'title': 'Langkah 1: Mencari Tahu Ada Berapa Total Hasil', 'content': step1_content })
    
    # Step 2: Kejadian A
    A_size = len(A)
    A_prob = fraction_to_string(A_size, S_size)
    A_decimal = fraction_to_decimal(A_size, S_size)
    
    step2_content = [
        f"Ada <strong>{A_size}</strong> hasil yang sesuai.",
        f"Peluangnya adalah: (Jumlah yang Sesuai) / (Total Semua Kemungkinan)",
        f"<div class='formula'>{A_size} / {S_size} = <strong>{A_prob}</strong></div>"
    ]
    if show_sets:
        step2_content.insert(0, f"Hasil yang kita cari (A): {format_set(A)}")
    steps.append({ 'title': f'Langkah 2: Mencari Skenario A ("{A_name}")', 'content': step2_content })
    
    # Menangani operasi komplementer
    if num_events == 1 and operation == 'complement':
        return _build_complement_steps(steps, A, A_name, S_size, num_dice)
    
    if num_events == 1:
        conclusion = f"Jadi, kemungkinan terjadinya '{A_name}' adalah <strong>{A_prob}</strong> (atau <strong>{A_decimal}</strong> / <strong>{A_decimal * 100:.2f}%</strong>)"
        return {'steps': steps, 'conclusion': conclusion}
    
    # Step 3: Kejadian B
    B_size = len(B)
    B_prob = fraction_to_string(B_size, S_size)
    B_decimal = fraction_to_decimal(B_size, S_size)
    
    step3_content = [
        f"Ada <strong>{B_size}</strong> hasil yang sesuai.",
        f"Peluangnya adalah: {B_size} / {S_size} = <strong>{B_prob}</strong>"
    ]
    if show_sets:
        step3_content.insert(0, f"Hasil yang kita cari (B): {format_set(B)}")
    steps.append({ 'title': f'Langkah 3: Mencari Skenario B ("{B_name}")', 'content': step3_content })
    
    if num_events == 2:
        return _build_two_events_steps(steps, A, B, A_name, B_name, A_prob, B_prob, S_size, show_sets, operation)
    
    if num_events == 3:
        return _build_three_events_steps(steps, A, B, C, A_name, B_name, C_name, A_prob, B_prob, S_size, show_sets, operation)
    
def _build_two_events_steps(steps, A, B, A_name, B_name, A_prob, B_prob, S_size, show_sets, operation):
    A_intersect_B = calculate_intersection(A, B)
    AB_size = len(A_intersect_B)
    AB_prob = fraction_to_string(AB_size, S_size)
    
    step4_content = [
        f"Jumlah hasil yang sama: <strong>{AB_size}</strong>",
        f"Peluang tumpang tindih: {AB_size} / {S_size} = <strong>{AB_prob}</strong>"
    ]
    if show_sets:
        step4_content.insert(0, f"Hasil yang sama persis (ada di A dan B): {format_set(A_intersect_B)}")

    steps.append({
        'title': 'Langkah 4: Mencari Hasil yang Tumpang Tindih (Ada di A dan B)',
        'content': step4_content
    })
    
    if operation == 'union':
        is_exclusive = (AB_size == 0)
        steps.append({
            'title': 'Langkah 5: Cek Apakah A dan B Bisa Terjadi Bersamaan?',
            'content': [f"Karena <strong>{'tidak ada' if is_exclusive else 'ada'}</strong> hasil yang tumpang tindih (jumlahnya {AB_size}), maka kedua skenario ini <span class='highlight'>{'TIDAK BISA' if is_exclusive else 'BISA'} terjadi bersamaan</span>."]
        })
        
        A_union_B = calculate_union(A, B)
        union_size = len(A_union_B)
        
        if is_exclusive:
            steps.append({
                'title': 'Langkah 6: Menghitung Peluang (A atau B)',
                'content': [
                    "Karena tidak bisa terjadi bersamaan, kita tinggal menjumlahkan peluangnya:",
                    "<div class='formula'>Peluang(A) + Peluang(B)</div>",
                    f"<div class='formula'>{A_prob} + {B_prob} = <strong>{fraction_to_string(union_size, S_size)}</strong></div>"
                ]
            })
        else:
            steps.append({
                'title': 'Langkah 6: Menghitung Peluang (A atau B)',
                'content': [
                    "Karena ada yang tumpang tindih, kita harus kurangi agar tidak dihitung dua kali:",
                    "<div class='formula'>Peluang(A) + Peluang(B) - Peluang(Tumpang Tindih)</div>",
                    f"<div class='formula'>{A_prob} + {B_prob} - {AB_prob} = <strong>{fraction_to_string(union_size, S_size)}</strong></div>"
                ]
            })
        
        union_prob = fraction_to_string(union_size, S_size)
        union_decimal = fraction_to_decimal(union_size, S_size)
        
        step7_content = [
            f"Jumlah total hasil gabungan: <strong>{union_size}</strong>",
            f"<div class='formula'>Peluang: {union_size} / {S_size} = <strong>{union_prob}</strong> ✓ (Hasilnya cocok!)</div>"
        ]
        if show_sets:
            step7_content.insert(0, f"Total hasil gabungan (A atau B): {format_set(A_union_B)}")
            
        steps.append({ 'title': 'Langkah 7: Pengecekan Ulang', 'content': step7_content })
        
        conclusion = f"Jadi, kemungkinan terjadinya '{A_name}' atau '{B_name}' adalah <strong>{union_prob}</strong> (atau <strong>{union_decimal}</strong> / <strong>{union_decimal * 100:.2f}%</strong>)"
        return {'steps': steps, 'conclusion': conclusion}

    elif operation == 'intersection':
        AB_decimal = fraction_to_decimal(AB_size, S_size)
        steps.append({
            'title': 'Langkah 5: Menghitung Peluang (A dan B)',
            'content': [
                "Peluangnya adalah hasil yang tumpang tindih tadi.",
                f"<div class='formula'>{AB_size} / {S_size} = <strong>{AB_prob}</strong></div>"
            ]
        })
        conclusion = f"Jadi, kemungkinan terjadinya '{A_name}' dan '{B_name}' secara bersamaan adalah <strong>{AB_prob}</strong> (atau <strong>{AB_decimal}</strong> / <strong>{AB_decimal * 100:.2f}%</strong>)"
        return {'steps': steps, 'conclusion': conclusion}

    elif operation == 'cond_B_A':
        return _build_conditional_steps(steps, A, B, A_name, B_name, A_intersect_B, AB_size, AB_prob, len(A), A_prob, S_size, 'B|A')
    elif operation == 'cond_A_B':
        return _build_conditional_steps(steps, B, A, B_name, A_name, A_intersect_B, AB_size, AB_prob, len(B), B_prob, S_size, 'A|B')

def _build_three_events_steps(steps, A, B, C, A_name, B_name, C_name, A_prob, B_prob, S_size, show_sets, operation):
    C_size = len(C)
    C_prob = fraction_to_string(C_size, S_size)
    
    step4_content_c = [
        f"Ada <strong>{C_size}</strong> hasil yang sesuai.",
        f"Peluangnya adalah: {C_size} / {S_size} = <strong>{C_prob}</strong>"
    ]
    if show_sets:
        step4_content_c.insert(0, f"Hasil yang kita cari (C): {format_set(C)}")
    steps.append({ 'title': f'Langkah 4: Mencari Skenario C ("{C_name}")', 'content': step4_content_c })
    
    AB = calculate_intersection(A, B); AC = calculate_intersection(A, C); BC = calculate_intersection(B, C); ABC = calculate_intersection(A, B, C)
    
    step5_content = [
        f"Jumlah A dan B: {len(AB)}, Peluang: {fraction_to_string(len(AB), S_size)}",
        f"Jumlah A dan C: {len(AC)}, Peluang: {fraction_to_string(len(AC), S_size)}",
        f"Jumlah B dan C: {len(BC)}, Peluang: {fraction_to_string(len(BC), S_size)}",
        f"Jumlah A, B, dan C: {len(ABC)}, Peluang: {fraction_to_string(len(ABC), S_size)}"
    ]
    if show_sets:
        step5_content = [
            f"Hasil A dan B: {format_set(AB)}, Jumlah: {len(AB)}",
            f"Hasil A dan C: {format_set(AC)}, Jumlah: {len(AC)}",
            f"Hasil B dan C: {format_set(BC)}, Jumlah: {len(BC)}",
            f"Hasil A, B, dan C bersamaan: {format_set(ABC)}, Jumlah: {len(ABC)}"
        ]
    steps.append({ 'title': 'Langkah 5: Mencari Semua Hasil yang Tumpang Tindih', 'content': step5_content })
    
    union_ABC = calculate_union(A, B, C); union_size = len(union_ABC)
    
    steps.append({
        'title': 'Langkah 6: Menghitung Peluang (A atau B atau C)',
        'content': [
            "Ini agak rumit! Kita jumlahkan semua peluang, kurangi yang tumpang tindih berdua, lalu tambahkan kembali yang tumpang tindih bertiga (agar pas).",
            "<div class='formula'>P(A) + P(B) + P(C) - P(A&B) - P(A&C) - P(B&C) + P(A&B&C)</div>",
            f"<div class='formula'>= {A_prob} + {B_prob} + {C_prob} - {fraction_to_string(len(AB), S_size)} - {fraction_to_string(len(AC), S_size)} - {fraction_to_string(len(BC), S_size)} + {fraction_to_string(len(ABC), S_size)}</div>",
            f"<div class='formula'>= <strong>{fraction_to_string(union_size, S_size)}</strong></div>"
        ]
    })
    
    union_prob = fraction_to_string(union_size, S_size); union_decimal = fraction_to_decimal(union_size, S_size)
    
    step7_content = [
        f"Jumlah total hasil gabungan: <strong>{union_size}</strong>",
        f"<div class='formula'>Peluang: {union_size} / {S_size} = <strong>{union_prob}</strong> ✓ (Hasilnya cocok!)</div>"
    ]
    if show_sets:
        step7_content.insert(0, f"Total hasil gabungan (A atau B atau C): {format_set(union_ABC)}")

    steps.append({ 'title': 'Langkah 7: Pengecekan Ulang', 'content': step7_content })
    
    conclusion = f"Jadi, kemungkinan terjadinya '{A_name}' atau '{B_name}' atau '{C_name}' adalah <strong>{union_prob}</strong> (atau <strong>{union_decimal}</strong> / <strong>{union_decimal * 100:.2f}%</strong>)"
    return {'steps': steps, 'conclusion': conclusion}

def _build_complement_steps(steps, A, A_name, S_size, num_dice):
    A_size = len(A); A_prob = fraction_to_string(A_size, S_size)
    A_comp_size = S_size - A_size; A_comp_prob = fraction_to_string(A_comp_size, S_size); A_comp_decimal = fraction_to_decimal(A_comp_size, S_size)

    steps.append({
        'title': f'Langkah 3: Menghitung Skenario Sebaliknya (Yang *Bukan* {A_name})',
        'content': [
            f"Caranya: 1 (utuh) dikurangi Peluang A.",
            f"<div class='formula'>1 - Peluang(A) = 1 - {A_prob} = <strong>{A_comp_prob}</strong></div>",
            f"Verifikasi: Jumlah hasil yang *bukan* A adalah {S_size} - {A_size} = {A_comp_size}. Peluangnya {A_comp_size}/{S_size} = {A_comp_prob}. ✓"
        ]
    })
    
    conclusion = f"Jadi, kemungkinan terjadinya 'Bukan {A_name}' adalah <strong>{A_comp_prob}</strong> (atau <strong>{A_comp_decimal}</strong> / <strong>{A_comp_decimal * 100:.2f}%</strong>)"
    return {'steps': steps, 'conclusion': conclusion}

def _build_conditional_steps(steps, known_event, unknown_event, known_name, unknown_name, intersection_set, intersection_size, intersection_prob_str, known_size, known_prob_str, S_size, cond_type):
    if cond_type == 'B|A':
        title = f"Langkah 5: Menghitung Peluang '{unknown_name}' (Dengan Syarat '{known_name}' Sudah Terjadi)"
        calc_events = f"'{unknown_name}' bila diketahui '{known_name}'"
    else:
        title = f"Langkah 5: Menghitung Peluang '{unknown_name}' (Dengan Syarat '{known_name}' Sudah Terjadi)"
        calc_events = f"'{unknown_name}' bila diketahui '{known_name}'"

    steps.append({'title': title, 'content': [
        f"Bayangkan kita hanya melihat hasil di Skenario A ('{known_name}').",
        f"Jumlah hasil di skenario ini ada <strong>{known_size}</strong>. Ini adalah 'Total Kemungkinan' kita yang baru.",
        f"Dari {known_size} hasil ini, kita cari mana yang juga termasuk Skenario B ('{unknown_name}').",
        f"Itu adalah hasil yang tumpang tindih, yang sudah kita hitung di Langkah 4, yaitu sejumlah <strong>{intersection_size}</strong>."
        ]})

    if known_size == 0:
        conclusion = f"Tidak bisa dihitung, karena skenario '{known_name}' tidak mungkin terjadi (peluangnya 0)."
        steps.append({
            'title': 'Langkah 6: Hasil',
            'content': [f"Skenario '{known_name}' tidak memiliki hasil. Pembagian dengan nol tidak bisa dilakukan."]
        })
        return {'steps': steps, 'conclusion': conclusion}

    cond_prob_val = fraction_to_string(intersection_size, known_size); cond_decimal_val = fraction_to_decimal(intersection_size, known_size)
    
    steps.append({
        'title': 'Langkah 6: Kalkulasi',
        'content': [
            "Cara hitungnya: (Jumlah hasil tumpang tindih) / (Jumlah hasil Skenario A)",
            f"<div class='formula'><strong>{intersection_size} / {known_size} = {cond_prob_val}</strong></div>"
        ]
    })
    
    conclusion = f"Jadi, jika kita tahu '{known_name}' sudah terjadi, peluang '{unknown_name}' adalah <strong>{cond_prob_val}</strong> (atau <strong>{cond_decimal_val}</strong> / <strong>{cond_decimal_val * 100:.2f}%</strong>)"
    return {'steps': steps, 'conclusion': conclusion}