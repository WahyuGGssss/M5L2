from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Menginisiasi pengelola database
manager = DB_Map("database.db")
manager.create_user_table()  # buat tabel users_cities + user_settings jika belum ada

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot started")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Halo, {ctx.author.name}. Masukkan !help_me untuk mengeksplorasi daftar perintah yang tersedia")

@bot.command()
async def help_me(ctx: commands.Context):
    await ctx.send(
        # Implementasi perintah yang akan menampilkan daftar perintah yang tersedia
        "`!start` - mulai menggunakan bot dan menerima pesan sambutan.\n"
        "`!help_me` - dapatkan daftar perintah yang tersedia.\n"
        "`!show_city <city_name>` - tampilkan kota yang ditentukan di peta.\n"
        "`!remember_city <city_name>` - simpan kota ke daftar favorit.\n"
        "`!show_my_cities` - tampilkan semua kota yang tersimpan.\n"
        "`!set_color <warna>` - pilih warna penanda kota di peta.\n"
        "`!set_map <warna_benua> <warna_laut>` - atur warna benua dan laut.\n"
        "`!add_geo` - tampilkan objek geografis tambahan (sungai, batas negara)."
    )

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    # Implementasi perintah yang akan menampilkan peta dengan kota yang ditentukan
    if not city_name:
        await ctx.send("Format salah. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")
        return
    marker = manager.get_marker_color(ctx.author.id)
    manager.create_graph(f'{ctx.author.id}.png', [city_name], marker_color=marker)
    await ctx.send(file=discord.File(f'{ctx.author.id}.png'))

@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Mengambil daftar kota yang diingat oleh pengguna
    # Implementasi perintah yang akan menampilkan peta dengan kota pengguna
    if cities:
        marker = manager.get_marker_color(ctx.author.id)
        manager.create_graph(f'{ctx.author.id}_cities.png', cities, marker_color=marker)
        await ctx.send(file=discord.File(f'{ctx.author.id}_cities.png'))
    else:
        await ctx.send("Belum ada kota yang kamu simpan.")

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Memeriksa apakah kota ada dalam database; jika ya, menambahkannya ke memori pengguna
        await ctx.send(f'Kota {city_name} telah berhasil disimpan!')
    else:
        await ctx.send("Format tidak benar. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")

# ===== FITUR BARU M5L2 =====

@bot.command(name="set_color")
async def set_color(ctx: commands.Context, *, color_name=""):
    """Fitur 1 — pengguna memilih warna penanda kota sendiri."""
    if not color_name:
        await ctx.send("Format salah. Contoh: `!set_color hijau` atau `!set_color ungu`")
        return
    saved = manager.set_marker_color(ctx.author.id, color_name)
    await ctx.send(
        f"Warna penanda kota kamu disimpan sebagai **{saved}**.\n"
        f"Coba `!show_city Tokyo` atau `!show_my_cities` untuk melihat hasilnya."
    )

@bot.command(name="set_map")
async def set_map(ctx: commands.Context, *, colors=""):
    """Fitur 2 — mewarnai benua dan lautan sesuai pilihan pengguna."""
    parts = colors.split()
    land = parts[0] if len(parts) >= 1 else '#c2b280'
    ocean = parts[1] if len(parts) >= 2 else '#a6cee3'
    land = normalize_color(land, '#c2b280')
    ocean = normalize_color(ocean, '#a6cee3')

    cities = manager.select_cities(ctx.author.id) or ['Tokyo']
    marker = manager.get_marker_color(ctx.author.id)
    path = f'{ctx.author.id}_styled.png'
    manager.create_graph(path, cities, marker_color=marker, land_color=land, ocean_color=ocean)
    await ctx.send(
        f"Peta dicetak dengan benua **{land}** dan laut **{ocean}**.\n"
        f"Contoh warna: `!set_map hijau biru`"
    )
    await ctx.send(file=discord.File(path))

@bot.command(name="add_geo")
async def add_geo(ctx: commands.Context):
    """Fitur 3 — menambahkan objek geografis ke peta."""
    cities = manager.select_cities(ctx.author.id) or ['Tokyo']
    marker = manager.get_marker_color(ctx.author.id)
    path = f'{ctx.author.id}_geo.png'
    manager.create_graph(path, cities, marker_color=marker, show_geo=True)
    await ctx.send(
        "Objek geografis ditambahkan: **pantai, sungai, dan batas negara**.\n"
        f"Contoh: `!add_geo`"
    )
    await ctx.send(file=discord.File(path))

if __name__ == "__main__":
    bot.run(TOKEN)
