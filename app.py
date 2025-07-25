from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os
from models import FilmSedangTayang, FilmAkanDatang
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'rahasia_admin'

UPLOAD_FOLDER = 'static/images'
DATA_FOLDER = os.path.join('static', 'data')  # ⬅️ Path baru untuk JSON
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_films():
    with open(os.path.join(DATA_FOLDER, 'films.json'), 'r') as f:
        data = json.load(f)
    films = []
    for item in data:
        if item['status'] == 'sedang':
            films.append(FilmSedangTayang(**item))
        else:
            films.append(FilmAkanDatang(**item))
    return films

def save_film(film_data):
    with open(os.path.join(DATA_FOLDER, 'films.json'), 'r') as f:
        data = json.load(f)
    data.append(film_data)
    with open(os.path.join(DATA_FOLDER, 'films.json'), 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login_admin'))
    with open(os.path.join(DATA_FOLDER, 'films.json')) as f:
        films = json.load(f)
    return render_template('admin.html', films=films)

@app.route('/')
@app.route('/daftar-film')
def daftar_film():
    films = load_films()
    return render_template("daftar_film.html", films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_user = request.form['username']
        input_pass = request.form['password']

        with open(os.path.join(DATA_FOLDER, 'users.json'), 'r') as f:
            users = json.load(f)

        for user in users:
            if user['username'] == input_user and user['password'] == input_pass:
                session['admin'] = True
                session['username'] = user['username']
                return redirect(url_for('dashboard'))

        flash('Login gagal! Username atau password salah.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/tambah-film', methods=['GET', 'POST'])
def tambah_film():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Ambil semua data dari form
        judul = request.form['judul']
        sutradara = request.form['sutradara']
        durasi = int(request.form['durasi'])
        rating = request.form['rating']
        sinopsis = request.form['sinopsis']
        genre = request.form['genre']
        harga = int(request.form['harga'])
        status = request.form['status']
        lokasi_terpilih = request.form.getlist('lokasi[]')
        jadwal_list = request.form.getlist('jadwal[]')

        gambar = request.files['poster']
        filename = secure_filename(gambar.filename)
        gambar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        film_id = int(os.urandom(2).hex(), 16)

        # Simpan film
        film_data = {
            'id': film_id,
            'judul': judul,
            'sutradara': sutradara,
            'durasi': durasi,
            'rating': rating,
            'sinopsis': sinopsis,
            'genre': genre,
            'harga': harga,
            'status': status,
            'poster': filename
        }

        save_film(film_data)

        # Simpan lokasi
        lokasi_path = os.path.join(DATA_FOLDER, 'lokasi.json')
        try:
            with open(lokasi_path, 'r') as f:
                lokasi_data = json.load(f)
        except FileNotFoundError:
            lokasi_data = []

        for nama_lokasi in lokasi_terpilih:
            lokasi_data.append({
                'film_id': film_id,
                'nama': nama_lokasi
            })

        with open(lokasi_path, 'w') as f:
            json.dump(lokasi_data, f, indent=4)

        # Simpan jadwal
        jadwal_path = os.path.join(DATA_FOLDER, 'jadwal.json')
        try:
            with open(jadwal_path, 'r') as f:
                jadwal_data = json.load(f)
        except FileNotFoundError:
            jadwal_data = []

        for jadwal in jadwal_list:
            if jadwal:  # hanya jika tidak kosong
                tanggal, jam = jadwal.split('T')
                for nama_lokasi in lokasi_terpilih:
                    jadwal_data.append({
                        'id': int(os.urandom(2).hex(), 16),
                        'film_id': film_id,
                        'lokasi': nama_lokasi,
                        'tanggal': tanggal,
                        'jam': jam
                    })

        with open(jadwal_path, 'w') as f:
            json.dump(jadwal_data, f, indent=4)

        flash('Film, lokasi, dan jadwal berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_dashboard'))

    # INI BAGIAN YANG PENTING: ambil lokasi dan kirim ke template
    lokasi_path = os.path.join(DATA_FOLDER, 'lokasi.json')
    try:
        with open(lokasi_path, 'r') as f:
            lokasi_data = json.load(f)
    except FileNotFoundError:
        lokasi_data = []

    # Ambil hanya lokasi unik
    lokasi_unik = []
    nama_tercatat = set()
    for l in lokasi_data:
        if l['nama'] not in nama_tercatat:
            lokasi_unik.append({'nama': l['nama']})
            nama_tercatat.add(l['nama'])

    return render_template('tambah_film.html', lokasi=lokasi_unik)

@app.route('/dashboard')
def dashboard():
    with open(os.path.join(DATA_FOLDER, 'films.json')) as f:
        films = json.load(f)
    return render_template('admin.html', films=films)

@app.route('/tambah-jadwal', methods=['GET', 'POST'])
def tambah_jadwal():
    if not session.get('admin'):
        return redirect(url_for('login'))

    with open(os.path.join(DATA_FOLDER, 'films.json')) as f:
        daftar_film = json.load(f)
    with open(os.path.join(DATA_FOLDER, 'lokasi.json')) as f:
        daftar_lokasi = json.load(f)

    selected_film_id = request.args.get('film_id')

    if request.method == 'POST':
        try:
            film_id = int(request.form['film_id'])
            lokasi = request.form['lokasi']
            tanggal = request.form['tanggal']
            jam = request.form['jam']
            new_jadwal = {
                'id': int(os.urandom(2).hex(), 16),
                'film_id': film_id,
                'lokasi': lokasi,
                'tanggal': tanggal,
                'jam': jam
            }

            try:
                with open(os.path.join(DATA_FOLDER, 'jadwal.json'), 'r') as f:
                    semua_jadwal = json.load(f)
            except FileNotFoundError:
                semua_jadwal = []

            semua_jadwal.append(new_jadwal)
            with open(os.path.join(DATA_FOLDER, 'jadwal.json'), 'w') as f:
                json.dump(semua_jadwal, f, indent=4)

            flash('Jadwal berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            flash(f'Terjadi kesalahan saat menambahkan jadwal: {e}', 'danger')

    return render_template(
        'tambah_jadwal.html',
        films=daftar_film,
        lokasi=daftar_lokasi,
        selected_film_id=selected_film_id
    )

@app.route('/tambah_lokasi', methods=['GET', 'POST'])
def tambah_lokasi():
    if not session.get('admin'):
        return redirect(url_for('login'))

    with open(os.path.join(DATA_FOLDER, 'films.json')) as f:
        films = json.load(f)

    if request.method == 'POST':
        nama = request.form['nama']
        film_id_str = request.form['film_id']

        if not film_id_str:
            flash('Pilih film terlebih dahulu.', 'danger')
            return redirect(request.url)

        try:
            film_id = int(film_id_str)
        except ValueError:
            flash('Film ID tidak valid.', 'danger')
            return redirect(request.url)

        lokasi_path = os.path.join(DATA_FOLDER, 'lokasi.json')

        try:
            with open(lokasi_path, 'r') as f:
                lokasi = json.load(f)
        except FileNotFoundError:
            lokasi = []

        lokasi.append({
            'nama': nama,
            'film_id': film_id
        })

        with open(lokasi_path, 'w') as f:
            json.dump(lokasi, f, indent=4)

        flash('Lokasi berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_dashboard'))

    selected_film_id = request.args.get('film_id', '')
    return render_template('tambah_lokasi.html', films=films, selected_film_id=selected_film_id)


@app.route('/film/<int:film_id>')
def detail_film(film_id):
    with open(os.path.join(DATA_FOLDER, 'films.json')) as f:
        films = json.load(f)
    with open(os.path.join(DATA_FOLDER, 'jadwal.json')) as f:
        semua_jadwal = json.load(f)
    with open(os.path.join(DATA_FOLDER, 'lokasi.json')) as f:
        semua_lokasi = json.load(f)

    film = next((f for f in films if int(f['id']) == film_id), None)
    if not film:
        return "Film tidak ditemukan", 404

    jadwal_film = [j for j in semua_jadwal if int(j['film_id']) == film_id]
    lokasi_nama = set(j['lokasi'] for j in jadwal_film if 'lokasi' in j)
    lokasi_film = [l for l in semua_lokasi if l['nama'] in lokasi_nama]

    return render_template(
        'detail_film.html',
        film=film,
        jadwal=jadwal_film,
        lokasi=lokasi_film
    )

@app.route('/pesan/<int:film_id>', methods=['GET', 'POST'])
def pesan_tiket(film_id):
    try:
        with open(os.path.join(DATA_FOLDER, 'films.json')) as f:
            daftar_film = json.load(f)
        film = next((f for f in daftar_film if f['id'] == film_id), None)
        if not film:
            return "Film tidak ditemukan", 404

        with open(os.path.join(DATA_FOLDER, 'lokasi.json')) as f:
            lokasi_film = [l for l in json.load(f) if int(l['film_id']) == film_id]

        with open(os.path.join(DATA_FOLDER, 'jadwal.json')) as f:
            jadwal_film = [j for j in json.load(f) if int(j['film_id']) == film_id]

        if request.method == 'POST':
            nama = request.form['nama']
            email = request.form['email']
            jumlah = int(request.form['jumlah'])
            jam = request.form['jam']
            kursi = request.form['kursi']
            lokasi_selected = request.form['lokasi']
            harga = int(film.get('harga', 50000))
            total = harga * jumlah

            data = {
                'judul': film['judul'],
                'nama': nama,
                'email': email,
                'jumlah': jumlah,
                'jam': jam,
                'kursi': kursi,
                'lokasi': lokasi_selected,
                'harga': harga,
                'total': total
            }

            return render_template('bukti_pesan.html', data=data)

        return render_template('pesan.html', film=film, jadwal=jadwal_film, lokasi=lokasi_film)

    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}", 500

@app.route('/edit/<int:film_id>', methods=['GET', 'POST'])
def edit_film(film_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    with open(os.path.join(DATA_FOLDER, 'films.json'), 'r') as f:
        films = json.load(f)

    film = next((f for f in films if f['id'] == film_id), None)

    if request.method == 'POST':
        film['judul'] = request.form['judul']
        film['genre'] = request.form['genre']
        film['status'] = request.form['status']

        with open(os.path.join(DATA_FOLDER, 'films.json'), 'w') as f:
            json.dump(films, f, indent=2)

        return redirect(url_for('dashboard'))

    return render_template('edit_film.html', film=film)

@app.route('/hapus/<int:film_id>')
def hapus_film(film_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    with open(os.path.join(DATA_FOLDER, 'films.json'), 'r') as f:
        data = json.load(f)
    data = [film for film in data if film['id'] != film_id]

    with open(os.path.join(DATA_FOLDER, 'films.json'), 'w') as f:
        json.dump(data, f, indent=2)
    return redirect(url_for('dashboard'))
@app.route('/register-admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_path = os.path.join(DATA_FOLDER, 'users.json')
        try:
            with open(users_path, 'r') as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        # Cek apakah username sudah ada
        for user in users:
            if user['username'] == username:
                flash('Username sudah terdaftar!', 'danger')
                return redirect(request.url)

        users.append({'username': username, 'password': password})
        with open(users_path, 'w') as f:
            json.dump(users, f, indent=4)

        flash('Admin berhasil didaftarkan!', 'success')
        return redirect(url_for('login'))

    return render_template('register_admin.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
