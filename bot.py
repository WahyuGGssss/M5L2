from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Menginisiasi pengelola database
manager = DB_Map("database.db")

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
        "`!show_my_cities` - tampilkan semua kota yang tersimpan."
    )

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    # Implementasi perintah yang akan menampilkan peta dengan kota yang ditentukan
    if not city_name:
        await ctx.send("Format salah. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")
        return
    manager.create_graph(f'{ctx.author.id}.png', [city_name])  
    await ctx.send(file=discord.File(f'{ctx.author.id}.png'))

@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Mengambil daftar kota yang diingat oleh pengguna
    # Implementasi perintah yang akan menampilkan peta dengan kota pengguna
    if cities:
        manager.create_graph(f'{ctx.author.id}_cities.png', cities)  
        await ctx.send(file=discord.File(f'{ctx.author.id}_cities.png'))
    else:
        await ctx.send("Belum ada kota yang kamu simpan.")

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Memeriksa apakah kota ada dalam database; jika ya, menambahkannya ke memori pengguna
        await ctx.send(f'Kota {city_name} telah berhasil disimpan!')
    else:
        await ctx.send("Format tidak benar. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")

if __name__ == "__main__":
    bot.run(TOKEN)