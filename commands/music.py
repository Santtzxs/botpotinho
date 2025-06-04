import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import imageio_ffmpeg

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.current_song = None
        self.spotify = None
        self.last_spotify_request = 0
        
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                self.spotify = spotipy.Spotify(auth_manager=auth_manager)
                self.spotify.search('test', limit=1)
                print("✅ Conexão com Spotify estabelecida com sucesso")
            except Exception as e:
                print(f"⚠️ Falha ao conectar com Spotify: {e}")
                self.spotify = None
        else:
            print("⚠️ Credenciais do Spotify não configuradas - funcionalidade desativada")

    async def ensure_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Você precisa estar em um canal de voz!")
            return False
        return True

    async def ensure_spotify_connection(self):
        if not self.spotify:
            return False
        
        try:
            current_time = time.time()
            if current_time - self.last_spotify_request < 1.0:
                await asyncio.sleep(1.0 - (current_time - self.last_spotify_request))
            
            self.spotify.search('test', limit=1)
            self.last_spotify_request = time.time()
            return True
        except Exception as e:
            print(f"Erro na conexão com Spotify: {e}")
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                self.spotify = spotipy.Spotify(auth_manager=auth_manager)
                return True
            except Exception as e:
                print(f"Falha ao reconectar com Spotify: {e}")
                return False

    async def play_next(self, ctx):
        if len(self.song_queue) > 0:
            self.current_song = self.song_queue.pop(0)
            voice_client = ctx.voice_client
            await self.play_yt(ctx, self.current_song)
        else:
            self.current_song = None
            await ctx.send("🎶 Fila de reprodução terminada")

    async def play_yt(self, ctx, query):
        ytdl_format_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

        try:
            info = ytdl.extract_info(f"ytsearch:{query}" if not query.startswith(('http://', 'https://')) else query, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]

            audio_url = info['url']
            title = info.get('title', 'Música Desconhecida')
            webpage_url = info.get('webpage_url', 'URL não disponível')

            source = discord.FFmpegPCMAudio(
                audio_url,
                executable=self.ffmpeg_path,
                **ffmpeg_options
            )
            
            audio_source = discord.PCMVolumeTransformer(source, volume=0.7)

            def after_playing(error):
                if error:
                    print(f"Erro: {error}")
                asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

            ctx.voice_client.play(audio_source, after=after_playing)
            await ctx.send(f"▶️ Tocando: **{title}**\n🔗 {webpage_url}")

        except Exception as e:
            await ctx.send(f"❌ Erro ao tocar: {e}")
            print(f"Erro: {e}")
            await self.play_next(ctx)

    async def process_spotify_url(self, ctx, url):
        if not await self.ensure_spotify_connection():
            return await ctx.send("❌ Problema na conexão com o Spotify. Tente novamente mais tarde.")

        try:
            if 'track' in url:
                
                track_id = re.search(r'track/([a-zA-Z0-9]+)', url).group(1)
                track = self.spotify.track(track_id)
                query = f"{track['name']} {track['artists'][0]['name']}"
                self.song_queue.append(query)
                await ctx.send(f"✅ Música adicionada: **{track['name']}** - **{track['artists'][0]['name']}**")
                
            elif 'album' in url:
                await ctx.send("🔍 Processando álbum do Spotify...")
                album_id = re.search(r'album/([a-zA-Z0-9]+)', url).group(1)
                tracks = []
                results = self.spotify.album_tracks(album_id)
                tracks.extend(results['items'])
                
                while results['next']:
                    results = self.spotify.next(results)
                    tracks.extend(results['items'])
                
                for track in tracks:
                    query = f"{track['name']} {track['artists'][0]['name']}"
                    self.song_queue.append(query)
                
                await ctx.send(f"✅ Álbum adicionado: {len(tracks)} músicas na fila!")
                
            elif 'playlist' in url:
                await ctx.send("🔍 Processando playlist do Spotify...")
                playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url).group(1)
                
               
                playlist_info = self.spotify.playlist(playlist_id)
                playlist_name = playlist_info['name']
                
               
                results = self.spotify.playlist_items(playlist_id, additional_types=['track'])
                tracks = results['items']
                
                while results['next']:
                    results = self.spotify.next(results)
                    tracks.extend(results['items'])
                
                added = 0
                for item in tracks:
                    if item.get('track'):
                        track = item['track']
                        if track and track['type'] == 'track':  
                            query = f"{track['name']} {track['artists'][0]['name']}"
                            self.song_queue.append(query)
                            added += 1
                
                await ctx.send(f"✅ Playlist '{playlist_name}' adicionada: {added} músicas na fila!")
            
            else:
                return await ctx.send("❌ Tipo de link do Spotify não suportado")
            
            if not ctx.voice_client.is_playing() and not self.current_song:
                await self.play_next(ctx)
                
        except spotipy.SpotifyException as e:
            error_msg = f"❌ Erro no Spotify: A playlist pode ser privada ou não existir."
            if "404" in str(e):
                error_msg += "\n🔍 A playlist pode ser privada ou não existir."
            await ctx.send(error_msg)
            print(f"Spotify Error: {e}")
        except Exception as e:
            await ctx.send(f"❌ Erro ao processar link: {str(e)}")
            print(f"Error: {e}")

    @commands.command(name="entrar")
    async def join(self, ctx):
        if not await self.ensure_voice(ctx):
            return
            
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
                await ctx.send(f"✅ Movido para: {channel.name}")
            return
            
        await channel.connect()
        await ctx.send(f"✅ Conectado a: {channel.name}")

    @commands.command(name="sair")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.song_queue = []
            self.current_song = None
            await ctx.send("👋 Desconectado")
        else:
            await ctx.send("❌ Não estou em um canal de voz")

    @commands.command(name="tocar")
    async def play(self, ctx, *, query):
        if not await self.ensure_voice(ctx):
            return
            
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        if 'open.spotify.com' in query:
            return await self.process_spotify_url(ctx, query)

        self.song_queue.append(query)
        
        if query.startswith(('http://', 'https://')):
            await ctx.send(f"✅ Adicionado à fila: **{query}**")
        else:
            await ctx.send(f"🔍 Adicionado à fila: Pesquisa por **'{query}'**")

        if not ctx.voice_client.is_playing() and not self.current_song:
            await self.play_next(ctx)

    @commands.command(name="pausar")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Pausado")
        else:
            await ctx.send("❌ Nada tocando para pausar")

    @commands.command(name="continuar")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Retomado")
        else:
            await ctx.send("❌ Nada pausado para retomar")

    @commands.command(name="parar")
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            self.song_queue = []
            self.current_song = None
            await ctx.send("⏹️ Parado e fila limpa")
        else:
            await ctx.send("❌ Nada tocando para parar")

    @commands.command(name="pular")
    async def skip(self, ctx):
        if not ctx.voice_client:
            return await ctx.send("❌ Não estou conectado a um canal de voz")
        
        if not ctx.voice_client.is_playing():
            return await ctx.send("❌ Nenhuma música tocando no momento")
        
        if len(self.song_queue) == 0:
            ctx.voice_client.stop()
            self.current_song = None
            return await ctx.send("⏭️ Música pulada (fila vazia)")
        
        ctx.voice_client.stop()
        await ctx.send("⏭️ Música pulada - indo para a próxima")

    @commands.command(name="fila")
    async def show_queue(self, ctx):
        if not self.song_queue:
            await ctx.send("📭 Fila vazia")
            return
            
        queue_list = []
        for i, song in enumerate(self.song_queue, 1):
            song_display = song if len(song) <= 50 else f"{song[:47]}..."
            queue_list.append(f"{i}. {song_display}")
        
        for i in range(0, len(queue_list), 10):
            chunk = queue_list[i:i + 10]
            await ctx.send("🎶 Fila de reprodução:\n" + "\n".join(chunk))

    @commands.command(name="limpar")
    async def clear_queue(self, ctx):
        self.song_queue = []
        await ctx.send("🧹 Fila de reprodução limpa!")

async def setup(bot):
    await bot.add_cog(Music(bot))