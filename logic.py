import sqlite3
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Warna yang boleh dipilih pengguna (contoh; matplotlib menerima banyak nama lain juga)
VALID_COLORS = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'black', 'pink', 'cyan', 'brown']


def normalize_color(color_name, default='red'):
    """Kembalikan nama warna yang valid untuk matplotlib, fallback ke default jika tidak dikenal."""
    if not color_name:
        return default
    try:
        mcolors.to_rgba(color_name)
    except (ValueError, TypeError):
        return default
    return color_name.strip().lower()


class DB_Map():
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            # Tabel baru: preferensi warna per pengguna (fitur 1)
            conn.execute('''CREATE TABLE IF NOT EXISTS user_settings (
                                user_id INTEGER PRIMARY KEY,
                                marker_color TEXT DEFAULT 'red'
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng FROM cities WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    # ── Fitur 1: warna penanda pilihan pengguna ──
    def get_marker_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT marker_color FROM user_settings WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                return row[0] if row else 'red'
            except sqlite3.OperationalError:
                return 'red'

    def set_marker_color(self, user_id, color_name):
        color_name = normalize_color(color_name)
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS user_settings (user_id INTEGER PRIMARY KEY, marker_color TEXT)")
            conn.execute(
                "INSERT INTO user_settings (user_id, marker_color) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET marker_color=excluded.marker_color",
                (user_id, color_name))
            conn.commit()
        return color_name

    # ── create_graph LAMA tetap ada, sekarang diperkaya fitur 1-3 ──
    # Tanda tangan tetap kompatibel: create_graph(path, cities) masih jalan.
    # Parameter tambahan opsional untuk fitur baru.
    def create_graph(self, path, cities, marker_color=None, land_color='#c2b280', ocean_color='#a6cee3', show_geo=True):
        """Menggambar peta. Jika marker_color None, pakai merah (default lama).
        Fitur baru:
          1) marker_color — warna penanda kota pilihan user
          2) land_color / ocean_color — mewarnai benua & lautan via cfeature
          3) show_geo — tambah COASTLINE, BORDERS, RIVERS
        """
        if marker_color is None:
            marker_color = 'red'
        marker_color = normalize_color(marker_color)
        land_color = normalize_color(land_color, '#c2b280')
        ocean_color = normalize_color(ocean_color, '#a6cee3')

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()

        # Fitur 2: warnai benua & lautan
        ax.add_feature(cfeature.LAND, facecolor=land_color)
        ax.add_feature(cfeature.OCEAN, facecolor=ocean_color)

        # Fitur 3: objek geografis tambahan
        if show_geo:
            ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
            ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
            ax.add_feature(cfeature.RIVERS, linewidth=0.4)

        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                plt.plot([lng], [lat], color=marker_color, linewidth=1, marker='.',
                         markersize=10, transform=ccrs.Geodetic())
                plt.text(lng + 3, lat + 12, city, horizontalalignment='left',
                         color=marker_color, transform=ccrs.Geodetic())

        plt.savefig(path)
        plt.close()

    # Alias untuk tugas — memanggil create_graph dengan warna eksplisit
    def create_graph_colored(self, path, cities, marker_color='red',
                             land_color='#c2b280', ocean_color='#a6cee3', show_geo=True):
        return self.create_graph(path, cities, marker_color=marker_color,
                                 land_color=land_color, ocean_color=ocean_color, show_geo=show_geo)

    def draw_distance(self, city1, city2):
        pass


if __name__ == "__main__":
    m = DB_Map("database.db")
    m.create_user_table()
