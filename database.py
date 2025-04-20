import json
import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Create and return a database connection with proper error handling"""
    os.makedirs("data", exist_ok=True)
    try:
        conn = sqlite3.connect('data/diagnosa_jeruk.db')
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def init_db():
    """Initialize database tables with proper schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables with explicit column definitions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gejala (
            kode_gejala VARCHAR(10) PRIMARY KEY,
            deskripsi TEXT NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS penyakit (
            kode_penyakit VARCHAR(10) PRIMARY KEY,
            nama_penyakit VARCHAR(255) NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS basis_pengetahuan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_penyakit VARCHAR(10) NOT NULL,
            kode_gejala VARCHAR(10) NOT NULL,
            nilai_probabilitas FLOAT NOT NULL,
            FOREIGN KEY (kode_penyakit) REFERENCES penyakit(kode_penyakit),
            FOREIGN KEY (kode_gejala) REFERENCES gejala(kode_gejala),
            UNIQUE (kode_penyakit, kode_gejala)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hasil_diagnosa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gejala_terpilih TEXT NOT NULL,
            hasil TEXT NOT NULL,
            tanggal_diagnosa DATETIME NOT NULL
        )
        """)
        
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM penyakit")
        if cursor.fetchone()[0] == 0:
            insert_initial_data(cursor)
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def insert_initial_data(cursor):
    """Insert initial data with transaction handling"""
    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Insert penyakit data
        penyakit_data = [
            ('P01', 'Busuk Akar dan Pangkal Batang'),
            ('P02', 'Embun Tepung'),
            ('P03', 'Blendok'),
            ('P04', 'Jamur Upas'),
            ('P05', 'Kudis'),
            ('P06', 'Tristeza CTV (Citrus Tristeza Virus)'),
            ('P07', 'CVPD (Citrus Vein Phloem Degeneration)')
        ]
        cursor.executemany("INSERT INTO penyakit VALUES (?, ?)", penyakit_data)
        
        # Insert gejala data
        gejala_data = [
            ('G01', 'Cabang atau ranting tampak menguning'),
            ('G02', 'Terlihat bagian batang ataupun akar yang membusuk apabila digali'),
            ('G03', 'Jamur berwarna putih tumbuh dan terlihat pada kulit akar yang terserang'),
            ('G04', 'Tanaman tampak segar pada pagi hari dan layu pada siang hari'),
            ('G05', 'Pangkal batang berubah menjadi berwarna kecoklatan'),
            ('G06', 'Pangkal batang layu dan mengering'),
            ('G07', 'Daun menguning dan layu'),
            ('G08', 'Jika batang tanaman dipotong maka akan terlihat jelas jaringan bawahnya berwarna cokelat kemerahan'),
            ('G09', 'Terdapat bintik bintik putih seperti tepung pada daun'),
            ('G10', 'Terdapat bintik bintik putih seperti tepung pada tangkai'),
            ('G11', 'Daun mengering akan tetapi tidak gugur'),
            ('G12', 'Daun bolong-bolong'),
            ('G13', 'Daun layu'),
            ('G14', 'Daun menghitam'),
            ('G15', 'Batang atau cabang mengeluarkan getah berwarna kuning keemasan'),
            ('G16', 'Warna batang atau cabang menjadi ke abu-abuan'),
            ('G17', 'Kulit batang mengelupas'),
            ('G18', 'Kulit batang akan mengering'),
            ('G19', 'Tangkai batang kering dan sulit dikelupas'),
            ('G20', 'Pertumbuhan terhambat atau kerdil'),
            ('G21', 'Retakan melintang pada batang'),
            ('G22', 'Pemucatan tulang daun'),
            ('G23', 'Daun kaku'),
            ('G24', 'Buah Kecil'),
            ('G25', 'Seperti ada gabus berwarna kuning pada daun'),
            ('G26', 'Seperti ada gabus berwarna kuning pada buah'),
            ('G27', 'Timbulnya kudis berupa bercak kasar dan menonjol pada buah'),
            ('G28', 'Seperti ada gabus berwarna kuning pada batang'),
            ('G29', 'Timbulnya kudis berupa bercak kasar dan menonjol pada ranting'),
            ('G30', 'Daun kecil'),
            ('G31', 'Tepi daun melengkung ke atas')
        ]
        cursor.executemany("INSERT INTO gejala VALUES (?, ?)", gejala_data)
        
        # Insert basis_pengetahuan data
        basis_data = [
            ('P01', 'G02', 0.84),
            ('P01', 'G03', 0.60),
            ('P01', 'G04', 0.58),
            ('P01', 'G05', 0.82),
            ('P01', 'G06', 0.82),
            ('P01', 'G07', 0.42),
            ('P01', 'G08', 0.78),
            ('P02', 'G09', 0.94),
            ('P02', 'G10', 0.62),
            ('P02', 'G11', 0.94),
            ('P02', 'G12', 0.64),
            ('P02', 'G13', 0.90),
            ('P02', 'G14', 0.96),
            ('P03', 'G15', 0.62),
            ('P03', 'G16', 0.86),
            ('P03', 'G17', 0.58),
            ('P03', 'G18', 0.78),
            ('P04', 'G19', 0.90),
            ('P04', 'G20', 0.82),
            ('P04', 'G21', 0.84),
            ('P04', 'G22', 0.80),
            ('P04', 'G23', 0.74),
            ('P04', 'G24', 0.96),
            ('P05', 'G20', 0.46),
            ('P05', 'G25', 0.82),
            ('P05', 'G26', 0.66),
            ('P05', 'G27', 0.56),
            ('P05', 'G28', 0.54),
            ('P05', 'G29', 0.76),
            ('P06', 'G07', 0.80),
            ('P06', 'G20', 0.22),
            ('P06', 'G22', 0.76),
            ('P06', 'G23', 0.58),
            ('P06', 'G24', 0.80),
            ('P06', 'G30', 0.38),
            ('P06', 'G31', 0.26),
            ('P07', 'G20', 0.55),
            ('P07', 'G23', 0.25),
            ('P07', 'G25', 0.65),
            ('P07', 'G26', 0.70),
            ('P07', 'G27', 0.90)
        ]
        cursor.executemany(
            "INSERT INTO basis_pengetahuan (kode_penyakit, kode_gejala, nilai_probabilitas) VALUES (?, ?, ?)", 
            basis_data
        )
        
        # Commit transaction
        cursor.execute("COMMIT")
        
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")
        print(f"Error inserting initial data: {e}")
        raise

def get_gejala():
    """Get all gejala data with error handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kode_gejala, deskripsi FROM gejala")
        return {row[0]: row[1] for row in cursor.fetchall()}
    except sqlite3.Error as e:
        print(f"Error fetching gejala: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def get_data_penyakit():
    """Get all penyakit and basis pengetahuan data with error handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT kode_penyakit, nama_penyakit FROM penyakit")
        penyakit_rows = cursor.fetchall()

        cursor.execute("""
        SELECT kode_penyakit, kode_gejala, nilai_probabilitas 
        FROM basis_pengetahuan
        """)
        basis_rows = cursor.fetchall()

        data = {}
        for kode, nama in penyakit_rows:
            data[kode] = {"nama": nama, "gejala": {}}

        for kode_penyakit, kode_gejala, nilai in basis_rows:
            if kode_penyakit in data:
                data[kode_penyakit]["gejala"][kode_gejala] = nilai

        return data
    except sqlite3.Error as e:
        print(f"Error fetching penyakit data: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def simpan_diagnosa(gejala, hasil):
    """Save diagnosis results with comprehensive error handling"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO hasil_diagnosa 
        (gejala_terpilih, hasil, tanggal_diagnosa) 
        VALUES (?, ?, ?)
        """
        
        cursor.execute(query, (
            json.dumps(gejala, ensure_ascii=False),
            json.dumps(hasil, ensure_ascii=False),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        return True
        
    except json.JSONEncodeError as e:
        print(f"JSON encoding error: {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()
    return False

# Test the database connection when run directly
if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print("Sample gejala data:", get_gejala())