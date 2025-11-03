def gcd(a, b):
    """Menghitung GCD untuk menyederhanakan pecahan"""
    while b:
        a, b = b, a % b
    return a


def simplify_fraction(numerator, denominator):
    """Menyederhanakan pecahan"""
    if numerator == 0:
        return 0, 1
    if denominator == 0: # Mencegah error pembagian nol
        return 0, 0
    common = gcd(numerator, denominator)
    return numerator // common, denominator // common


def fraction_to_string(numerator, denominator):
    """Mengubah pecahan ke string"""
    if denominator == 0:
        return "N/A (Pembagian 0)"
    num, den = simplify_fraction(numerator, denominator)
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def fraction_to_decimal(numerator, denominator):
    """Mengubah pecahan ke desimal"""
    if denominator == 0:
        return 0
    return round(numerator / denominator, 4)


def format_set(items, max_display=10):
    """Format himpunan untuk ditampilkan"""
    if not items:
        return "∅ (Kosong)"
    
    # Cek jika item pertama adalah tuple (untuk N dadu)
    if items and isinstance(items[0], tuple):
        if len(items) <= max_display:
            # Ubah tuple menjadi string yang lebih rapi
            return "{" + ", ".join([str(item) for item in items]) + "}"
        else:
            displayed = ", ".join([str(item) for item in items[:max_display]])
            return "{" + displayed + ", ...}"
    # Jika bukan tuple (untuk 1 dadu)
    elif items:
        if len(items) <= max_display:
            return "{" + ", ".join(map(str, items)) + "}"
        else:
            displayed = ", ".join(map(str, items[:max_display]))
            return "{" + displayed + ", ...}"
    return "∅ (Kosong)"