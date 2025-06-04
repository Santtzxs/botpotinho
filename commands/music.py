import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import imageio_ffmpeg

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.current_song = None
        self.spotify = None
        self.last_spotify_request = 0
        
        print("[Music Cog] Inicializando cog de música...")
        
        # Verificar FFmpeg
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"[FFmpeg] Caminho do executável: {self.ffmpeg_path}")
        
        if not os.path.exists(self.ffmpeg_path):
            print("[ERRO FFmpeg] Executável não encontrado no caminho especificado!")
        else:
            print("[FFmpeg] Executável encontrado com sucesso")
        
        # Configurar Spotify
        if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            print("[Spotify] Credenciais encontradas, tentando conectar...")
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                self.spotify = spotipy.Spotify(auth_manager=auth_manager)
                self.spotify.search('test', limit=1)
                print("✅ [Spotify] Conexão estabelecida com sucesso")
            except Exception as e:
                print(f"⚠️ [Spotify] Falha ao conectar: {e}")
                self.spotify = None
        else:
            print("⚠️ [Spotify] Credenciais não configuradas - funcionalidade desativada")

    async def ensure_voice(self, ctx):
        print(f"[ensure_voice] Verificando conexão de voz para {ctx.author}")
        if not ctx.author.voice:
            print("[ensure_voice] Usuário não está em canal de voz")
            await ctx.send("❌ Você precisa estar em um canal de voz!")
            return False
        print("[ensure_voice] Usuário está em canal de voz")
        return True

    async def ensure_spotify_connection(self):
        print("[ensure_spotify_connection] Verificando conexão com Spotify")
        if not self.spotify:
            print("[ensure_spotify_connection] Spotify não configurado")
            return False
        
        try:
            current_time = time.time()
            if current_time - self.last_spotify_request < 1.0:
                wait_time = 1.0 - (current_time - self.last_spotify_request)
                print(f"[ensure_spotify_connection] Esperando {wait_time}s para evitar rate limit")
                await asyncio.sleep(wait_time)
            
            print("[ensure_spotify_connection] Testando conexão com Spotify")
            self.spotify.search('test', limit=1)
            self.last_spotify_request = time.time()
            return True
        except Exception as e:
            print(f"[ERRO Spotify] Erro na conexão: {e}")
            try:
                print("[Spotify] Tentando reconectar...")
                auth_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                self.spotify = spotipy.Spotify(auth_manager=auth_manager)
                return True
            except Exception as e:
                print(f"[ERRO Spotify] Falha ao reconectar: {e}")
                return False

    async def play_next(self, ctx):
        print(f"[play_next] Iniciando próxima música. Fila: {len(self.song_queue)} itens")
        if len(self.song_queue) > 0:
            self.current_song = self.song_queue.pop(0)
            print(f"[play_next] Preparando para tocar: {self.current_song}")
            voice_client = ctx.voice_client
            if not voice_client:
                print("[ERRO play_next] Nenhum cliente de voz encontrado!")
                return
            await self.play_yt(ctx, self.current_song)
        else:
            print("[play_next] Fila vazia")
            self.current_song = None
            await ctx.send("🎶 Fila de reprodução terminada")

    async def play_yt(self, ctx, query):
    ytdl_options = {
        'format': 'bestaudio/best',
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'extract_flat': False,
        'socket_timeout': 15,
        'retries': 3,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.youtube.com/'
        }
    }

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -filter:a "volume=0.7"'
    }

    try:
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            info = await self.bot.loop.run_in_executor(
                None,
                lambda: ytdl.extract_info(
                    f"ytsearch:{query}" if not query.startswith(('http://', 'https://')) else query,
                    download=False
                )
            )

            if not info:
                await ctx.send("❌ Nenhum resultado encontrado.")
                return await self.play_next(ctx)
                
            if 'entries' in info:
                info = info['entries'][0]

            if not info.get('url'):
                await ctx.send("❌ Não foi possível obter o stream de áudio.")
                return await self.play_next(ctx)

            audio_url = info['url']
            title = info.get('title', query)
            webpage_url = info.get('webpage_url', f"https://youtu.be/{info.get('id', '')}")

            source = discord.FFmpegPCMAudio(
                executable=self.ffmpeg_path,
                source=audio_url,
                **ffmpeg_options
            )

            ctx.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx),
                    self.bot.loop
                )
            )

            await ctx.send(f"▶️ Tocando: **{title}**\n🔗 {webpage_url}")

    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)[:200]}")
        await self.play_next(ctx)

    async def process_spotify_url(self, ctx, url):
        print(f"[process_spotify_url] Processando URL do Spotify: {url}")
        if not await self.ensure_spotify_connection():
            print("[process_spotify_url] Conexão com Spotify falhou")
            return await ctx.send("❌ Problema na conexão com o Spotify. Tente novamente mais tarde.")

        try:
            if 'track' in url:
                print("[process_spotify_url] Tipo: Track")
                track_id = re.search(r'track/([a-zA-Z0-9]+)', url).group(1)
                track = self.spotify.track(track_id)
                query = f"{track['name']} {track['artists'][0]['name']}"
                self.song_queue.append(query)
                await ctx.send(f"✅ Música adicionada: **{track['name']}** - **{track['artists'][0]['name']}**")
                
            elif 'album' in url:
                print("[process_spotify_url] Tipo: Album")
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
                print("[process_spotify_url] Tipo: Playlist")
                await ctx.send("🔍 Processando playlist do Spotify...")
                playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', url).group(1)
                
                playlist_info = self.spotify.playlist(playlist_id)
                playlist_name = playlist_info['name']
                print(f"[process_spotify_url] Nome da playlist: {playlist_name}")
                
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
                print("[process_spotify_url] Tipo não suportado")
                return await ctx.send("❌ Tipo de link do Spotify não suportado")
            
            if not ctx.voice_client.is_playing() and not self.current_song:
                print("[process_spotify_url] Nada tocando, iniciando reprodução")
                await self.play_next(ctx)
                
        except spotipy.SpotifyException as e:
            print(f"[ERRO Spotify] Exception: {e}")
            error_msg = f"❌ Erro no Spotify: A playlist pode ser privada ou não existir."
            if "404" in str(e):
                error_msg += "\n🔍 A playlist pode ser privada ou não existir."
            await ctx.send(error_msg)
        except Exception as e:
            print(f"[ERRO process_spotify_url] Exception: {e}")
            await ctx.send(f"❌ Erro ao processar link: {str(e)}")

    @commands.command(name="entrar")
    async def join(self, ctx):
        print(f"[comando entrar] Chamado por {ctx.author}")
        if not await self.ensure_voice(ctx):
            return
            
        channel = ctx.author.voice.channel
        print(f"[comando entrar] Canal alvo: {channel}")
        
        if ctx.voice_client:
            print(f"[comando entrar] Bot já está em um canal de voz")
            if ctx.voice_client.channel != channel:
                print("[comando entrar] Movendo para novo canal")
                await ctx.voice_client.move_to(channel)
                await ctx.send(f"✅ Movido para: {channel.name}")
            return
            
        print("[comando entrar] Conectando ao canal de voz")
        try:
            await channel.connect()
            await ctx.send(f"✅ Conectado a: {channel.name}")
            print("[comando entrar] Conexão estabelecida com sucesso")
        except Exception as e:
            print(f"[ERRO entrar] Falha ao conectar: {e}")
            await ctx.send(f"❌ Falha ao conectar: {e}")

    @commands.command(name="sair")
    async def leave(self, ctx):
        print(f"[comando sair] Chamado por {ctx.author}")
        if ctx.voice_client:
            print("[comando sair] Desconectando do canal de voz")
            await ctx.voice_client.disconnect()
            self.song_queue = []
            self.current_song = None
            await ctx.send("👋 Desconectado")
        else:
            print("[comando sair] Nenhum canal de voz para desconectar")
            await ctx.send("❌ Não estou em um canal de voz")

    @commands.command(name="tocar")
    async def play(self, ctx, *, query):
        print(f"[comando tocar] Chamado por {ctx.author} com query: {query}")
        
        if not await self.ensure_voice(ctx):
            return
            
        if not ctx.voice_client:
            print("[comando tocar] Bot não está em canal de voz, conectando...")
            try:
                await ctx.author.voice.channel.connect()
                print("[comando tocar] Conectado com sucesso")
            except Exception as e:
                print(f"[ERRO tocar] Falha ao conectar: {e}")
                await ctx.send(f"❌ Falha ao conectar: {e}")
                return

        if 'open.spotify.com' in query:
            print("[comando tocar] Detectado link do Spotify")
            return await self.process_spotify_url(ctx, query)

        self.song_queue.append(query)
        print(f"[comando tocar] Música adicionada à fila. Tamanho da fila: {len(self.song_queue)}")
        
        if query.startswith(('http://', 'https://')):
            await ctx.send(f"✅ Adicionado à fila: **{query}**")
        else:
            await ctx.send(f"🔍 Adicionado à fila: Pesquisa por **'{query}'**")

        if not ctx.voice_client.is_playing() and not self.current_song:
            print("[comando tocar] Nada tocando, iniciando reprodução")
            await self.play_next(ctx)
        else:
            print("[comando tocar] Já há música tocando, adicionado à fila")

    @commands.command(name="pausar")
    async def pause(self, ctx):
        print(f"[comando pausar] Chamado por {ctx.author}")
        if ctx.voice_client and ctx.voice_client.is_playing():
            print("[comando pausar] Pausando reprodução")
            ctx.voice_client.pause()
            await ctx.send("⏸️ Pausado")
        else:
            print("[comando pausar] Nada tocando para pausar")
            await ctx.send("❌ Nada tocando para pausar")

    @commands.command(name="continuar")
    async def resume(self, ctx):
        print(f"[comando continuar] Chamado por {ctx.author}")
        if ctx.voice_client and ctx.voice_client.is_paused():
            print("[comando continuar] Retomando reprodução")
            ctx.voice_client.resume()
            await ctx.send("▶️ Retomado")
        else:
            print("[comando continuar] Nada pausado para retomar")
            await ctx.send("❌ Nada pausado para retomar")

    @commands.command(name="parar")
    async def stop(self, ctx):
        print(f"[comando parar] Chamado por {ctx.author}")
        if ctx.voice_client:
            print("[comando parar] Parando reprodução e limpando fila")
            ctx.voice_client.stop()
            self.song_queue = []
            self.current_song = None
            await ctx.send("⏹️ Parado e fila limpa")
        else:
            print("[comando parar] Nada tocando para parar")
            await ctx.send("❌ Nada tocando para parar")

    @commands.command(name="pular")
    async def skip(self, ctx):
        print(f"[comando pular] Chamado por {ctx.author}")
        if not ctx.voice_client:
            print("[comando pular] Nenhum cliente de voz")
            return await ctx.send("❌ Não estou conectado a um canal de voz")
        
        if not ctx.voice_client.is_playing():
            print("[comando pular] Nada tocando no momento")
            return await ctx.send("❌ Nenhuma música tocando no momento")
        
        if len(self.song_queue) == 0:
            print("[comando pular] Fila vazia após pular")
            ctx.voice_client.stop()
            self.current_song = None
            return await ctx.send("⏭️ Música pulada (fila vazia)")
        
        print("[comando pular] Pulando para próxima música")
        ctx.voice_client.stop()
        await ctx.send("⏭️ Música pulada - indo para a próxima")

    @commands.command(name="fila")
    async def show_queue(self, ctx):
        print(f"[comando fila] Chamado por {ctx.author}")
        if not self.song_queue:
            print("[comando fila] Fila vazia")
            await ctx.send("📭 Fila vazia")
            return
            
        queue_list = []
        for i, song in enumerate(self.song_queue, 1):
            song_display = song if len(song) <= 50 else f"{song[:47]}..."
            queue_list.append(f"{i}. {song_display}")
        
        print(f"[comando fila] Exibindo fila com {len(queue_list)} itens")
        for i in range(0, len(queue_list), 10):
            chunk = queue_list[i:i + 10]
            await ctx.send("🎶 Fila de reprodução:\n" + "\n".join(chunk))

    @commands.command(name="limpar")
    async def clear_queue(self, ctx):
        print(f"[comando limpar] Chamado por {ctx.author}")
        self.song_queue = []
        print("[comando limpar] Fila limpa")
        await ctx.send("🧹 Fila de reprodução limpa!")

async def setup(bot):
    print("[setup] Registrando cog de música")
    await bot.add_cog(Music(bot))
    print("[setup] Cog de música registrado com sucesso")
