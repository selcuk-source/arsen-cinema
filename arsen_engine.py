# ================================================================
# ARSEN PROCESS - CINEMA ENGINE v5.0
# Tüm üretim motorları: Ses, Video, Efekt, AI, Renk, Format
# ================================================================

import os, cv2, json, time, asyncio, subprocess, urllib.parse, urllib.request
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

# ================================================================
# YAPILANDIRMA
# ================================================================
ASSETS = "assets"
PHOTOS = f"{ASSETS}/photos"
VIDEOS = f"{ASSETS}/videos"
LOGOS  = f"{ASSETS}/logos"
MUSIC  = f"{ASSETS}/music"
OUTPUT = "output_clips"
AI_OUT = "ai_generated"
AUDIO  = "audio_temp"
SUBS   = "subtitles"

for d in [PHOTOS, VIDEOS, LOGOS, MUSIC, OUTPUT, AI_OUT, AUDIO, SUBS]:
    os.makedirs(d, exist_ok=True)

# Renk Paleti
PALETTE = {
    "amber":  "#1A0F00", "navy":   "#0A1628", "green":  "#0A1A0F",
    "dark":   "#0D0D1A", "purple": "#0F0A1A", "gold":   "#D4AF37",
    "teal":   "#00D2BA", "steel":  "#8E9AAF", "white":  "#F0F0F0",
}

# Çoklu Dil Ses Ayarları (FAZA 1)
VOICES = {
    "Türkçe":    {"male": "tr-TR-AhmetNeural",   "female": "tr-TR-EmelNeural"},
    "English":   {"male": "en-US-GuyNeural",      "female": "en-US-JennyNeural"},
    "العربية":   {"male": "ar-SA-HamedNeural",    "female": "ar-SA-ZariyahNeural"},
    "Deutsch":   {"male": "de-DE-ConradNeural",   "female": "de-DE-KatjaNeural"},
    "Français":  {"male": "fr-FR-HenriNeural",    "female": "fr-FR-DeniseNeural"},
}


# ================================================================
# FAZA 1: SES MOTORU (Çoklu Dil + SFX + Müzik)
# ================================================================
class AudioEngine:
    """Çoklu dil seslendirme, ses efektleri ve müzik üretimi."""

    @staticmethod
    async def generate_voice(text, lang="Türkçe", gender="male", rate="-3%", output_path=None):
        """Çoklu dilde profesyonel seslendirme üretir."""
        import edge_tts
        voice = VOICES.get(lang, VOICES["Türkçe"])[gender]
        if not output_path:
            output_path = f"{AUDIO}/voice_{int(time.time())}.mp3"
        try:
            comm = edge_tts.Communicate(text, voice, rate=rate)
            await comm.save(output_path)
            return output_path
        except Exception as e:
            print(f"   ⚠ Ses hatası: {e}")
            return None

    @staticmethod
    def generate_sfx(sfx_type, duration=2.0, output_path=None):
        """Basit ses efektleri üretir (numpy synthesizer)."""
        import struct, wave
        if not output_path:
            output_path = f"{AUDIO}/sfx_{sfx_type}_{int(time.time())}.wav"

        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        samples = np.zeros(n_samples, dtype=np.float32)

        if sfx_type == "factory_hum":
            # Fabrika uğultusu: düşük frekanslı drone
            t = np.linspace(0, duration, n_samples)
            samples = 0.3 * np.sin(2 * np.pi * 60 * t)
            samples += 0.15 * np.sin(2 * np.pi * 120 * t)
            samples += 0.05 * np.random.randn(n_samples)

        elif sfx_type == "pressure_valve":
            # Basınç valfi: beyaz gürültü + filtre
            t = np.linspace(0, duration, n_samples)
            noise = np.random.randn(n_samples)
            envelope = np.exp(-3 * t) * np.sin(20 * t)
            samples = noise * envelope * 0.5

        elif sfx_type == "liquid_flow":
            # Sıvı akışı: modüle edilmiş gürültü
            t = np.linspace(0, duration, n_samples)
            carrier = np.sin(2 * np.pi * 200 * t)
            mod = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
            samples = carrier * mod * 0.2 + np.random.randn(n_samples) * 0.05

        elif sfx_type == "welding":
            # Kaynak kıvılcımı: crackle
            t = np.linspace(0, duration, n_samples)
            crackle = np.random.randn(n_samples) * np.exp(-8 * t)
            buzz = 0.2 * np.sin(2 * np.pi * 800 * t) * np.exp(-2 * t)
            samples = crackle * 0.4 + buzz

        elif sfx_type == "whoosh":
            # Geçiş sesi
            t = np.linspace(0, duration, n_samples)
            freq = 200 + 2000 * t / duration
            samples = 0.3 * np.sin(2 * np.pi * freq * t) * np.exp(-2 * t)

        else:
            t = np.linspace(0, duration, n_samples)
            samples = 0.1 * np.sin(2 * np.pi * 440 * t) * np.exp(-3 * t)

        # Normalize
        peak = np.max(np.abs(samples))
        if peak > 0:
            samples = samples / peak * 0.8

        # Fade in/out
        fade = min(int(n_samples * 0.05), 1000)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)

        # WAV olarak kaydet
        samples_16 = (samples * 32767).astype(np.int16)
        with wave.open(output_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples_16.tobytes())

        return output_path

    @staticmethod
    def generate_ambient_music(duration=60, mood="epic", output_path=None):
        """Basit ambient arka plan müziği üretir."""
        import struct, wave
        if not output_path:
            output_path = f"{MUSIC}/ambient_{mood}_{int(time.time())}.wav"

        sr = 44100
        n = int(sr * duration)
        t = np.linspace(0, duration, n)
        mix = np.zeros(n, dtype=np.float32)

        if mood == "epic":
            # Epik: derin pad + yükselen ton
            mix += 0.15 * np.sin(2 * np.pi * 55 * t)   # A1 drone
            mix += 0.10 * np.sin(2 * np.pi * 82.4 * t)  # E2
            mix += 0.08 * np.sin(2 * np.pi * 110 * t)   # A2
            # Yükselen melodi
            freq = 220 + 110 * np.sin(2 * np.pi * 0.05 * t)
            mix += 0.06 * np.sin(2 * np.pi * freq * t)
            # Pad
            mix += 0.04 * np.sin(2 * np.pi * 165 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t))

        elif mood == "tech":
            # Teknolojik: pulse + beep
            mix += 0.12 * np.sin(2 * np.pi * 80 * t)
            pulse = np.sin(2 * np.pi * 2 * t) > 0.7
            mix += 0.08 * np.sin(2 * np.pi * 440 * t) * pulse
            mix += 0.05 * np.sin(2 * np.pi * 660 * t) * (1 - pulse)

        elif mood == "calm":
            # Sakin: yumuşak pad
            mix += 0.10 * np.sin(2 * np.pi * 130.8 * t)  # C3
            mix += 0.08 * np.sin(2 * np.pi * 164.8 * t)  # E3
            mix += 0.06 * np.sin(2 * np.pi * 196 * t)    # G3
            mix *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * t)

        # Normalize ve fade
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = mix / peak * 0.5
        fade = min(int(n * 0.03), sr * 2)
        mix[:fade] *= np.linspace(0, 1, fade)
        mix[-fade:] *= np.linspace(1, 0, fade)

        s16 = (mix * 32767).astype(np.int16)
        with wave.open(output_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(s16.tobytes())

        return output_path

    @staticmethod
    def generate_subtitle_file(scenes, lang="Türkçe", output_path=None):
        """Sahne listesinden .srt altyazı dosyası üretir."""
        if not output_path:
            output_path = f"{SUBS}/subtitles_{lang}.srt"

        lines = []
        current_time = 0.0
        for i, sc in enumerate(scenes):
            vo = sc.get("vo", "")
            if not vo:
                continue
            # Tahmini süre (ses hızına göre ~4 harf/saniye)
            duration = max(len(vo) / 12, 3.0)
            start = current_time
            end = current_time + duration

            sh, sm, ss_ms = int(start//3600), int((start%3600)//60), start%60
            eh, em, es_ms = int(end//3600), int((end%3600)//60), end%60

            lines.append(f"{i+1}")
            lines.append(f"{sh:02d}:{sm:02d}:{ss_ms:06.3f} --> {eh:02d}:{em:02d}:{es_ms:06.3f}".replace(".", ","))
            lines.append(vo)
            lines.append("")

            current_time = end + 0.5

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return output_path


# ================================================================
# FAZA 2: GÖRSEL KALİTE MOTORU (Renk, Efekt, Upscale)
# ================================================================
class VisualEngine:
    """Sinematik renk düzeltme, parçacık efektleri, upscale."""

    @staticmethod
    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def apply_color_grade(frame, style="teal_orange"):
        """Hollywood tarzı sinematik renk düzeltme."""
        if style == "teal_orange":
            # Teal & Orange: gölgeler mavi-yeşil, parlaklar turuncu
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
            l, a, b = lab[:,:,0], lab[:,:,1], lab[:,:,2]
            # Gölgelere teal ekle
            shadow_mask = l < 128
            a[shadow_mask] -= 5
            b[shadow_mask] -= 8
            # Parlaklara turuncu ekle
            highlight_mask = l >= 128
            a[highlight_mask] += 3
            b[highlight_mask] += 8
            lab = np.clip(np.stack([l, a, b], axis=2), 0, 255).astype(np.uint8)
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        elif style == "bleach_bypass":
            # Bleach Bypass: düşük doygunluk, yüksek kontrast
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_3ch = cv2.merge([gray, gray, gray])
            result = cv2.addWeighted(frame, 0.5, gray_3ch, 0.5, 0)
            # Kontrast artır
            result = np.clip((result - 128) * 1.3 + 128, 0, 255).astype(np.uint8)
            return result

        elif style == "vintage_amber":
            # Vintage Amber: sıcak, soluk tonlar
            result = frame.copy().astype(np.float32)
            result[:,:,0] *= 0.85  # Mavi azalt
            result[:,:,1] *= 0.95  # Yeşil hafif azalt
            result[:,:,2] *= 1.1   # Kırmızı artır
            result = np.clip(result, 0, 255).astype(np.uint8)
            # Hafif solma
            result = cv2.addWeighted(result, 0.85,
                np.full_like(result, 200), 0.15, 0)
            return result

        elif style == "cold_tech":
            # Soğuk teknoloji: mavi-çelik tonlar
            result = frame.copy().astype(np.float32)
            result[:,:,0] *= 1.15  # Mavi artır
            result[:,:,1] *= 1.0   # Yeşil sabit
            result[:,:,2] *= 0.85  # Kırmızı azalt
            return np.clip(result, 0, 255).astype(np.uint8)

        elif style == "noir":
            # Film Noir: siyah-beyaz + yüksek kontrast
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = np.clip((gray - 128) * 1.5 + 128, 0, 255).astype(np.uint8)
            return cv2.merge([gray, gray, gray])

        return frame

    @staticmethod
    def add_particles(frame, n=30, color=(0, 210, 186), speed=1.0):
        """Video karesine yüzen parçacık efekti ekler."""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        for _ in range(n):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            r = np.random.randint(1, 4)
            alpha = np.random.uniform(0.2, 0.7)
            cv2.circle(overlay, (x, y), r, color, -1)
        return cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

    @staticmethod
    def add_lens_flare(frame, position=(0.7, 0.3), intensity=0.3):
        """Sinematik lens flare efekti."""
        h, w = frame.shape[:2]
        cx, cy = int(w * position[0]), int(h * position[1])
        overlay = frame.copy()

        # Ana parlama
        for r in range(80, 0, -2):
            alpha = intensity * (1 - r / 80)
            color = (int(255 * alpha), int(215 * alpha), int(55 * alpha))
            cv2.circle(overlay, (cx, cy), r, color, -1)

        # Işık çizgisi
        cv2.line(overlay, (0, cy), (w, cy), (100, 180, 255), 1)

        return cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

    @staticmethod
    def add_vignette(frame, strength=0.5):
        """Sinematik kenar karartma."""
        h, w = frame.shape[:2]
        Y, X = np.ogrid[:h, :w]
        r = np.sqrt((X - w/2)**2 + (Y - h/2)**2) / np.sqrt((w/2)**2 + (h/2)**2)
        vig = np.clip(1.0 - r**1.5 * strength, 0.3, 1.0)
        result = frame.copy()
        for c in range(3):
            result[:,:,c] = (result[:,:,c] * vig).astype(np.uint8)
        return result

    @staticmethod
    def upscale_frame(frame, scale=2):
        """Basit AI upscale (Lanczos + sharpening)."""
        h, w = frame.shape[:2]
        upscaled = cv2.resize(frame, (w*scale, h*scale), interpolation=cv2.INTER_LANCZOS4)
        # Keskinleştirme
        kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]) / 1.5
        sharpened = cv2.filter2D(upscaled, -1, kernel)
        return cv2.addWeighted(upscaled, 0.7, sharpened, 0.3, 0)

    @staticmethod
    def process_video(input_path, output_path, color_grade="teal_orange",
                      particles=False, vignette=True, flare=False, upscale=False):
        """Videoya tüm görsel efektleri uygular."""
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        if upscale:
            w, h = w * 2, h * 2

        writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'),
                                  fps, (w, h))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if upscale:
                frame = VisualEngine.upscale_frame(frame)

            frame = VisualEngine.apply_color_grade(frame, color_grade)

            if particles:
                frame = VisualEngine.add_particles(frame)
            if flare:
                frame = VisualEngine.add_lens_flare(frame)
            if vignette:
                frame = VisualEngine.add_vignette(frame)

            writer.write(frame)

        cap.release()
        writer.release()
        return True


# ================================================================
# FAZA 3: AKILLI İÇERİK MOTORU (Senaryo, Kişiselleştirme, Format)
# ================================================================
class ContentEngine:
    """AI senaryo yazarı, müşteri kişiselleştirme, format dönüşümü."""

    @staticmethod
    def generate_script_with_ai(client_name, project_details, lang="English"):
        """Pollinations AI ile otomatik senaryo üretir."""
        prompt = (
            f"Write a professional corporate documentary script for {client_name}. "
            f"Project details: {project_details}. "
            f"Language: {lang}. "
            f"Format: 10 scenes, each with a title and 1-sentence narration. "
            f"Return as numbered list."
        )
        try:
            encoded = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                script = resp.read().decode("utf-8")
            return script
        except Exception as e:
            return f"AI senaryo üretilemedi: {e}"

    @staticmethod
    def personalize_scenes(scenes, client_name, project_data):
        """Sahne listesini müşteriye göre kişiselleştirir."""
        personalized = []
        for sc in scenes:
            new_sc = dict(sc)
            # Müşteri adını başlığa ekle
            if "KAPANIŞ" in new_sc.get("title", ""):
                new_sc["vo"] = f"Sayın {client_name}, {new_sc['vo']}"
            # Proje verilerini ekle
            if "data" in new_sc and project_data:
                new_sc["data"] = project_data
            personalized.append(new_sc)
        return personalized

    @staticmethod
    def convert_to_vertical(input_path, output_path):
        """16:9 videoyu 9:16 dikey formata çevirir (Reels/Shorts)."""
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        # 9:16 oranı (1080x1920)
        out_w, out_h = 1080, 1920
        writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'),
                                  fps, (out_w, out_h))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Merkezden kırp
            crop_h = int(w * 16 / 9)
            if crop_h > h:
                crop_h = h
            y1 = (h - crop_h) // 2
            cropped = frame[y1:y1+crop_h, :]
            resized = cv2.resize(cropped, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)

            # Üst ve alt siyah şeritler (gerekirse)
            canvas = np.zeros((out_h, out_w, 3), dtype=np.uint8)
            fh = int(out_w * h / w)
            fy = (out_h - fh) // 2
            canvas[fy:fy+fh, :] = cv2.resize(frame, (out_w, fh))

            writer.write(canvas)

        cap.release()
        writer.release()
        return True

    @staticmethod
    def generate_social_cuts(input_path, output_dir):
        """Bir videodan sosyal medya kesitleri üretir."""
        os.makedirs(output_dir, exist_ok=True)
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total / fps

        formats = {
            "reel_15s": 15,
            "reel_30s": 30,
            "story_10s": 10,
        }

        results = []
        for name, secs in formats.items():
            if duration < secs:
                continue
            out_path = os.path.join(output_dir, f"{name}.mp4")
            start_frame = int((duration - secs) / 2 * fps)  # Ortadan al
            end_frame = start_frame + int(secs * fps)

            writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'),
                                      fps, (1080, 1920))
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            for _ in range(end_frame - start_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                # Dikey kırp
                h, w = frame.shape[:2]
                crop_w = int(h * 9 / 16)
                x1 = (w - crop_w) // 2
                cropped = frame[:, x1:x1+crop_w]
                resized = cv2.resize(cropped, (1080, 1920))
                writer.write(resized)
            writer.release()
            results.append(out_path)

        cap.release()
        return results


# ================================================================
# FAZA 4: İLERİ AI MOTORU (Altyazı, Stil, Analiz)
# ================================================================
class AdvancedAIEngine:
    """Gelişmiş AI özellikleri."""

    @staticmethod
    def auto_subtitle_from_text(scenes, output_dir=None):
        """Sahne metinlerinden otomatik .srt altyazı üretir."""
        if not output_dir:
            output_dir = SUBS
        os.makedirs(output_dir, exist_ok=True)

        for lang_name, voices in VOICES.items():
            srt_path = os.path.join(output_dir, f"sub_{lang_name}.srt")
            lines = []
            t = 0.0
            for i, sc in enumerate(scenes):
                vo = sc.get("vo", "")
                dur = max(len(vo) / 12, 3.0)
                sh, sm = int(t//3600), int((t%3600)//60)
                ss = t % 60
                eh, em = int((t+dur)//3600), int(((t+dur)%3600)//60)
                es = (t + dur) % 60
                lines.append(f"{i+1}")
                lines.append(f"{sh:02d}:{sm:02d}:{ss:06.3f} --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ","))
                lines.append(vo)
                lines.append("")
                t += dur + 0.5

            with open(srt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

        return output_dir

    @staticmethod
    def apply_style_transfer(frame, style="cinematic"):
        """Basit stil transferi (renk manipülasyonu)."""
        if style == "cinematic":
            return VisualEngine.apply_color_grade(frame, "teal_orange")
        elif style == "documentary":
            return VisualEngine.apply_color_grade(frame, "vintage_amber")
        elif style == "scifi":
            return VisualEngine.apply_color_grade(frame, "cold_tech")
        elif style == "noir":
            return VisualEngine.apply_color_grade(frame, "noir")
        return frame

    @staticmethod
    def analyze_video_quality(video_path):
        """Video kalite analizi yapar."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "Video açılamadı"}

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0

        # Parlaklık analizi (ilk 10 kare)
        brightness_values = []
        for _ in range(min(10, frames)):
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))

        cap.release()

        avg_brightness = np.mean(brightness_values) if brightness_values else 0

        quality_score = "Yüksek" if w >= 1920 else "Orta" if w >= 1280 else "Düşük"

        return {
            "Çözünürlük": f"{w}x{h}",
            "FPS": f"{fps:.1f}",
            "Süre": f"{duration:.1f} sn",
            "Kare Sayısı": frames,
            "Ortalama Parlaklık": f"{avg_brightness:.0f}/255",
            "Kalite": quality_score,
        }


# ================================================================
# FAZA 5: DAĞITIM VE PROJE YÖNETİMİ
# ================================================================
class DistributionEngine:
    """Format dönüşümü, proje yönetimi, export."""

    @staticmethod
    def export_formats(input_path, output_dir=None):
        """Tek videodan tüm formatları üretir."""
        if not output_dir:
            output_dir = "exports"
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return []

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        formats = {
            "4K_UHD": (3840, 2160),
            "1080p_FHD": (1920, 1080),
            "720p_HD": (1280, 720),
            "480p_SD": (854, 480),
            "Vertical_Reels": (1080, 1920),
            "Square_Instagram": (1080, 1080),
        }

        results = []
        for name, (ow, oh) in formats.items():
            out_path = os.path.join(output_dir, f"{name}.mp4")
            writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'),
                                      fps, (ow, oh))
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if name == "Vertical_Reels":
                    fh, fw = frame.shape[:2]
                    crop_w = int(fh * 9 / 16)
                    x1 = (fw - crop_w) // 2
                    frame = frame[:, x1:x1+crop_w]
                elif name == "Square_Instagram":
                    fh, fw = frame.shape[:2]
                    size = min(fw, fh)
                    x1 = (fw - size) // 2
                    y1 = (fh - size) // 2
                    frame = frame[y1:y1+size, x1:x1+size]

                resized = cv2.resize(frame, (ow, oh), interpolation=cv2.INTER_LANCZOS4)
                writer.write(resized)
            writer.release()
            results.append(out_path)

        cap.release()
        return results

    @staticmethod
    def save_project(scenes, project_name="arsen_project"):
        """Projeyi JSON olarak kaydeder."""
        project_data = {
            "name": project_name,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scenes": scenes,
            "version": "5.0"
        }
        path = f"{project_name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        return path

    @staticmethod
    def load_project(project_path):
        """Kaydedilmiş projeyi yükler."""
        try:
            with open(project_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("scenes", [])
        except Exception as e:
            print(f"Proje yüklenemedi: {e}")
            return None