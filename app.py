import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import os
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException

# --- Impor Logika Inti Anda ---
from utils import (
    parse_event_logic, 
    build_calculation_steps
)

# --- KONFIGURASI GEMINI ---
API_KEY = os.getenv("GEMINI_API_KEY")

try:
    genai.configure(api_key=API_KEY)
    # Gunakan model yang cepat dan efisien
    model = genai.GenerativeModel('gemini-2.5-flash-lite') 
except Exception as e:
    print(f"Error Konfigurasi Gemini: {e}")
    print("Pastikan API_KEY sudah benar.")
    model = None

# --- PROMPT UNTUK LLM (PENGGANTI REGEX) ---
SYSTEM_PROMPT = """
Anda adalah asisten parser JSON yang sangat ketat. Tugas Anda HANYA mengubah soal probabilitas dadu dari pengguna menjadi format JSON yang spesifik.

JANGAN membalas apa pun selain JSON yang valid. Jangan gunakan markdown (```json ... ```), jangan beri penjelasan, jangan minta maaf.

Soal pengguna akan diberikan di akhir.

Gunakan `event_type` berikut:
1. UNTUK 1 DADU ('numDice': 1):
   - 'face_even': (angka genap)
   - 'face_odd': (angka ganjil)
   - 'face_prime': (angka prima)
   - 'custom_face_1': (angka custom, cth: "angka > 4" atau "angka 5")

2. UNTUK N DADU ('numDice' > 1):
   - 'sum_even': (jumlah genap)
   - 'sum_odd': (jumlah ganjil)
   - 'all_same': (semua dadu sama)
   - 'all_different': (semua dadu beda)
   - 'all_even': (semua dadu genap)
   - 'all_odd': (semua dadu ganjil)
   - 'at_least_one_even': (setidaknya satu genap)
   - 'at_least_one_odd': (setidaknya satu ganjil)
   - 'custom_sum': (jumlah custom, cth: "jumlah > 10" atau "jumlah 8")
   - 'custom_face_n': (setidaknya satu dadu custom, cth: "satu dadu angkanya 6")

Gunakan `operation` berikut:
- 'union': untuk "atau"
- 'intersection': untuk "dan"
- 'complement': untuk "bukan" atau "tidak"
- 'cond_B_A': untuk "peluang B jika diketahui A"
- 'union': (default jika hanya 1 kejadian)

Gunakan `operator` berikut (untuk 'custom_face_1', 'custom_sum', 'custom_face_n'):
- 'eq', 'gt', 'lt', 'gte', 'lte', 'ne'
- Gunakan 'eq' jika tidak ada operator (cth: "jumlah 8").
- Gunakan null jika tidak ada operator DAN tidak ada value.

Format JSON HARUS seperti ini:
{
  "numDice": (angka),
  "numEvents": (angka),
  "operation": "(string)",
  "eventA": "(string)",
  "eventAOperator": "(string atau null)",
  "eventAValue": "(string angka atau null)",
  "eventB": "(string atau null)",
  "eventBOperator": "(string atau null)",
  "eventBValue": "(string angka atau null)"
}

--- CONTOH ---
Soal: Sebuah dadu dilempar. Berapa peluang munculnya angka genap atau angka prima?
{
  "numDice": 1,
  "numEvents": 2,
  "operation": "union",
  "eventA": "face_even",
  "eventAOperator": null,
  "eventAValue": null,
  "eventB": "face_prime",
  "eventBOperator": null,
  "eventBValue": null
}

Soal: 3 dadu, peluang jumlahnya > 15 jika diketahui semua dadu genap?
{
  "numDice": 3,
  "numEvents": 2,
  "operation": "cond_B_A",
  "eventA": "all_even",
  "eventAOperator": null,
  "eventAValue": null,
  "eventB": "custom_sum",
  "eventBOperator": "gt",
  "eventBValue": "15"
}

Soal: 5 dadu, peluang jumlahnya 30?
{
  "numDice": 5,
  "numEvents": 1,
  "operation": "union",
  "eventA": "custom_sum",
  "eventAOperator": "eq",
  "eventAValue": "30",
  "eventB": null,
  "eventBOperator": null,
  "eventBValue": null
}

Soal: 5 buah dadu dilempar. Berapa peluang jumlahnya bukan 30?
{
  "numDice": 5,
  "numEvents": 1,
  "operation": "complement",
  "eventA": "custom_sum",
  "eventAOperator": "eq",
  "eventAValue": "30",
  "eventB": null,
  "eventBOperator": null,
  "eventBValue": null
}
--- AKHIR INSTRUKSI ---

Soal Pengguna:
"""

# --- Inisialisasi Flask ---
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Endpoint utama untuk kalkulasi dari teks soal."""
    if not model:
        return jsonify({'error': 'Model Gemini tidak terkonfigurasi. Cek API Key.'}), 500

    try:
        req_data = request.json
        soal_text = req_data.get('soal')
        if not soal_text:
            return jsonify({'error': 'Soal tidak boleh kosong'}), 400
        
        # 1. Buat Prompt Lengkap
        full_prompt = SYSTEM_PROMPT + soal_text
        
        # 2. Panggil LLM (Gemini API)
        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            temperature=0.0
        )
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
        }

        response = model.generate_content(
            full_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        llm_output_text = response.text
        
        # 3. Parse JSON dari LLM
        if llm_output_text.startswith("```json"):
            llm_output_text = llm_output_text.strip("```json\n").strip("```")
            
        data = json.loads(llm_output_text)

        # 4. Ambil data
        num_dice = int(data.get('numDice', 1))
        num_events = int(data.get('numEvents', 1))
        
        def parse_single_event(dice_count, event_key):
            event_type = data.get(f'event{event_key}')
            operator = data.get(f'event{event_key}Operator')
            value = data.get(f'event{event_key}Value')
            return parse_event_logic(dice_count, event_type, operator, value)

        A, A_name = parse_single_event(num_dice, 'A')
        B, B_name = (parse_single_event(num_dice, 'B') if num_events >= 2 else (None, None))
        C, C_name = (parse_single_event(num_dice, 'C') if num_events == 3 else (None, None))

        # 5. Hitung
        result = build_calculation_steps(
            num_dice=num_dice,
            num_events=num_events,
            operation=data.get('operation', 'union'),
            A=A, A_name=A_name,
            B=B, B_name=B_name,
            C=C, C_name=C_name
        )

        return jsonify(result)
        
    except json.JSONDecodeError:
        print(f"DEBUG: Output LLM yang gagal di-parse: {llm_output_text}")
        return jsonify({'error': 'Gagal mem-parse respons dari LLM. Output tidak valid.'}), 500
    except ValueError as e:
        # Ini akan menangkap error dari _terjemahkan_event atau parse_event_logic
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan internal: {str(e)}'}), 500


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description or 'HTTP error'}), e.code
    return jsonify({'error': str(e) or 'Internal server error'}), 500


if __name__ == '__main__':
    if API_KEY == "MASUKKAN_API_KEY_ANDA_DI_SINI":
        print("="*50)
        print("ERROR: Harap masukkan API Key Anda di file app.py")
        print("Dapatkan Key di: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")
        print("="*50)
    else:
        app.run(debug=True)