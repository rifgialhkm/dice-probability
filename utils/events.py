import itertools

def _get_all_outcomes(num_dice):
    """
    Menghasilkan semua kemungkinan hasil lemparan dadu.
    """
    if num_dice == 1:
        return list(range(1, 7))
    else:
        return list(itertools.product(range(1, 7), repeat=num_dice))

def _compare(val1, operator, val2):
    """Fungsi helper untuk membandingkan dua nilai."""
    if operator == 'eq': return val1 == val2
    if operator == 'ne': return val1 != val2
    if operator == 'gt': return val1 > val2
    if operator == 'lt': return val1 < val2
    if operator == 'gte': return val1 >= val2
    if operator == 'lte': return val1 <= val2
    return False

def parse_event_logic(num_dice, event_type, operator=None, custom_value=None):
    """
    Satu fungsi untuk mem-parse semua logika event untuk 1 sampai N dadu.
    """
    S = _get_all_outcomes(num_dice)
    
    event_set = []
    event_name = ""

    # 2. Logika untuk 1 Dadu
    if num_dice == 1:
        if event_type == 'face_even':
            event_name = 'Angka Genap'
            event_set = [v for v in S if v % 2 == 0]
        elif event_type == 'face_odd':
            event_name = 'Angka Ganjil'
            event_set = [v for v in S if v % 2 != 0]
        elif event_type == 'face_prime':
            event_name = 'Angka Prima'
            event_set = [v for v in S if v in [2, 3, 5]]
        elif event_type == 'custom_face_1':
            if custom_value is None or operator is None:
                raise ValueError("Nilai dan operator custom harus diisi untuk custom_face_1")
            n = int(custom_value)
            if n < 1 or n > 6: raise ValueError("Nilai custom harus antara 1–6")
            op_symbol = {'eq': '=', 'ne': '≠', 'gt': '>', 'lt': '<', 'gte': '≥', 'lte': '≤'}.get(operator, '')
            event_name = f'Angka {op_symbol} {n}'
            event_set = [v for v in S if _compare(v, operator, n)]
        else:
            raise ValueError(f"Tipe kejadian '{event_type}' tidak dikenal untuk 1 dadu.")
    
    # 3. Logika untuk N Dadu (n >= 2)
    else:
        if event_type == 'sum_even':
            event_name = 'Jumlah Genap'
            event_set = [outcome for outcome in S if sum(outcome) % 2 == 0]
        elif event_type == 'sum_odd':
            event_name = 'Jumlah Ganjil'
            event_set = [outcome for outcome in S if sum(outcome) % 2 != 0]
        elif event_type == 'all_same':
            event_name = 'Semua Mata Dadu Sama'
            event_set = [outcome for outcome in S if len(set(outcome)) == 1]
        elif event_type == 'all_different':
            event_name = 'Semua Mata Dadu Beda'
            event_set = [outcome for outcome in S if len(set(outcome)) == num_dice]
        elif event_type == 'all_even':
            event_name = 'Semua Dadu Genap'
            event_set = [outcome for outcome in S if all(x % 2 == 0 for x in outcome)]
        elif event_type == 'all_odd':
            event_name = 'Semua Dadu Ganjil'
            event_set = [outcome for outcome in S if all(x % 2 != 0 for x in outcome)]
        elif event_type == 'at_least_one_even':
            event_name = 'Setidaknya Satu Dadu Genap'
            event_set = [outcome for outcome in S if any(x % 2 == 0 for x in outcome)]
        elif event_type == 'at_least_one_odd':
            event_name = 'Setidaknya Satu Dadu Ganjil'
            event_set = [outcome for outcome in S if any(x % 2 != 0 for x in outcome)]
        elif event_type == 'custom_sum':
            if custom_value is None or operator is None:
                raise ValueError("Nilai dan operator custom harus diisi untuk custom_sum")
            n = int(custom_value)
            min_sum, max_sum = num_dice, num_dice * 6
            if n < min_sum or n > max_sum:
                raise ValueError(f"Nilai jumlah harus antara {min_sum}–{max_sum}")
            op_symbol = {'eq': '=', 'ne': '≠', 'gt': '>', 'lt': '<', 'gte': '≥', 'lte': '≤'}.get(operator, '')
            event_name = f'Jumlah {op_symbol} {n}'
            event_set = [outcome for outcome in S if _compare(sum(outcome), operator, n)]
        elif event_type == 'custom_face_n':
            if custom_value is None or operator is None:
                raise ValueError("Nilai dan operator custom harus diisi untuk custom_face_n")
            n = int(custom_value)
            if n < 1 or n > 6: raise ValueError("Nilai angka harus antara 1–6")
            op_symbol = {'eq': '=', 'ne': '≠', 'gt': '>', 'lt': '<', 'gte': '≥', 'lte': '≤'}.get(operator, '')
            event_name = f'Setidaknya satu dadu {op_symbol} {n}'
            event_set = [outcome for outcome in S if any(_compare(x, operator, n) for x in outcome)]
        else:
            raise ValueError(f"Tipe kejadian '{event_type}' tidak dikenal untuk {num_dice} dadu.")

    return event_set, event_name