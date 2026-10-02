# ================================================================
# ARSEN PROCESS - AI DIRECTOR ENGINE v9.0 (CINEMATIC EDITION)
# 3 Katmanlı Sinematik Video Motoru
# ================================================================

import os, json, time, re, urllib.parse, urllib.request, textwrap, subprocess
import cv2
import numpy as np


# ================================================================
# 1. GELİŞMİŞ SİNEMATİK GÖRSEL MOTORU (ProceduralVisuals v2)
# ================================================================
class ProceduralVisuals:
    """
    Her sahne için çok katmanlı sinematik görseller üretir:
    - Arka plan gradyan + derinlik
    - Orta plan: sahneye özel geometri (reaktör, molekül, harita)
    - Ön plan: parçacık efekti + ışık huzmeleri + lens flare
    - Sinematik post-process: vignette + renk düzeltme + film grain
    """

    @staticmethod
    def _add_particles(img, n=120, color=(0, 210, 186), size_range=(1, 5), opacity=0.4):
        h, w = img.shape[:2]
        overlay = img.copy()
        for _ in range(n):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            r = np.random.randint(size_range[0], size_range[1])
            a = np.random.uniform(0.1, opacity)
            c = tuple(int(ch * a) for ch in color)
            cv2.circle(overlay, (x, y), r, c, -1)
        return cv2.addWeighted(overlay, 0.6, img, 0.4, 0)

    @staticmethod
    def _add_light_rays(img, n=5, color=(255, 220, 150)):
        h, w = img.shape[:2]
        overlay = img.copy()
        cx = np.random.randint(w // 4, 3 * w // 4)
        cy = np.random.randint(0, h // 3)
        for _ in range(n):
            angle = np.random.uniform(-0.8, 0.8)
            length = np.random.randint(h, h * 2)
            ex = int(cx + length * np.sin(angle))
            ey = int(cy + length * np.cos(angle))
            cv2.line(overlay, (cx, cy), (ex, ey), color, np.random.randint(1, 3))
        return cv2.addWeighted(overlay, 0.15, img, 0.85, 0)

    @staticmethod
    def _add_lens_flare(img, position=(0.7, 0.25), intensity=0.25):
        h, w = img.shape[:2]
        cx, cy = int(w * position[0]), int(h * position[1])
        overlay = img.copy()
        for r in range(100, 0, -3):
            alpha = intensity * (1 - r / 100)
            color = (int(255 * alpha), int(215 * alpha), int(55 * alpha))
            cv2.circle(overlay, (cx, cy), r, color, -1)
        cv2.line(overlay, (0, cy), (w, cy), (80, 120, 180), 1)
        return cv2.addWeighted(overlay, 0.3, img, 0.7, 0)

    @staticmethod
    def _add_film_grain(img, intensity=0.03):
        noise = np.random.randn(*img.shape).astype(np.float32) * intensity * 255
        result = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        return result

    @staticmethod
    def _add_depth_fog(img, color=(10, 22, 40), strength=0.3):
        h, w = img.shape[:2]
        fog = np.zeros_like(img)
        for y in range(h):
            ratio = y / h
            fog[y, :] = tuple(int(c * ratio * strength * 255) for c in (color[0]/255, color[1]/255, color[2]/255))
        return cv2.addWeighted(img, 0.8, fog, 0.2, 0)

    @staticmethod
    def _cinematic_post(img, grade="teal_orange"):
        h, w = img.shape[:2]
        # Renk düzeltme
        result = img.copy().astype(np.float32)
        if grade == "teal_orange":
            result[:,:,0] = np.clip(result[:,:,0] * 1.1 + 8, 0, 255)
            result[:,:,2] = np.clip(result[:,:,2] * 1.05 + 5, 0, 255)
        elif grade == "vintage_amber":
            result[:,:,0] *= 0.85
            result[:,:,2] *= 1.1
        elif grade == "cold_tech":
            result[:,:,0] *= 1.15
            result[:,:,2] *= 0.85
        result = np.clip(result, 0, 255).astype(np.uint8)

        # Vinyet
        Y, X = np.ogrid[:h, :w]
        r = np.sqrt((X - w/2)**2 + (Y - h/2)**2) / np.sqrt((w/2)**2 + (h/2)**2)
        vig = np.clip(1.0 - r**1.6 * 0.55, 0.25, 1.0)
        for c in range(3):
            result[:,:,c] = (result[:,:,c] * vig).astype(np.uint8)

        # Film grain
        result = ProceduralVisuals._add_film_grain(result, 0.02)
        return result

    @staticmethod
    def create_scene_visual(scene_data, output_path):
        v_type = scene_data.get("visual_type", "factory")
        title = scene_data.get("title", "ARŞEN PROCESS")
        w, h = 1920, 1080
        cx, cy = w // 2, h // 2

        # KATMAN 1: Derinlikli Arka Plan
        img = np.zeros((h, w, 3), dtype=np.uint8)
        for y in range(h):
            r = y / h
            if v_type in ["refinery", "closing"]:
                img[y, :] = (int(8+r*25), int(12+r*30), int(25+r*55))
            elif v_type in ["molecule", "laboratory"]:
                img[y, :] = (int(30+r*50), int(22+r*35), int(8+r*18))
            elif v_type == "product":
                img[y, :] = (int(15+r*20), int(20+r*25), int(8+r*12))
            elif v_type == "map":
                img[y, :] = (int(10+r*15), int(12+r*18), int(28+r*45))
            else:
                img[y, :] = (int(12+r*18), int(15+r*22), int(22+r*35))

        # Izgara dokusu
        for x in range(0, w, 80):
            cv2.line(img, (x, 0), (x, h), (35, 30, 25), 1)
        for y in range(0, h, 80):
            cv2.line(img, (0, y), (w, y), (35, 30, 25), 1)

        # KATMAN 2: Sahneye Özel Ana Görsel
        if v_type == "molecule":
            # CO2 molekülü - detaylı
            for ring_r in range(200, 50, -30):
                cv2.circle(img, (cx, cy), ring_r, (0, 60, 50), 1)
            cv2.circle(img, (cx, cy), 60, (100, 100, 100), -1)
            cv2.circle(img, (cx, cy), 55, (130, 130, 130), -1)
            cv2.circle(img, (cx-220, cy), 80, (50, 50, 200), -1)
            cv2.circle(img, (cx-220, cy), 75, (70, 70, 220), -1)
            cv2.circle(img, (cx+220, cy), 80, (50, 50, 200), -1)
            cv2.circle(img, (cx+220, cy), 75, (70, 70, 220), -1)
            cv2.line(img, (cx-140, cy), (cx-60, cy), (200, 200, 200), 10)
            cv2.line(img, (cx-140, cy-8), (cx-60, cy-8), (180, 180, 180), 4)
            cv2.line(img, (cx+60, cy), (cx+140, cy), (200, 200, 200), 10)
            cv2.line(img, (cx+60, cy-8), (cx+140, cy-8), (180, 180, 180), 4)
            cv2.putText(img, "C", (cx-20, cy+18), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255,255,255), 3)
            cv2.putText(img, "O", (cx-240, cy+18), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255,255,255), 3)
            cv2.putText(img, "O", (cx+200, cy+18), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255,255,255), 3)
            # Süperkritik bulut efekti
            for _ in range(60):
                px = cx + np.random.randint(-300, 300)
                py = cy + np.random.randint(-200, 200)
                pr = np.random.randint(20, 80)
                cv2.circle(img, (px, py), pr, (0, 80, 70), -1)

        elif v_type == "refinery":
            # Detaylı rafineri silüeti
            structures = [
                (cx-500, 200, 80, 600), (cx-350, 150, 60, 650),
                (cx-200, 250, 100, 550), (cx-50, 100, 70, 700),
                (cx+100, 180, 90, 620), (cx+250, 220, 75, 580),
                (cx+400, 160, 85, 640), (cx+550, 280, 65, 520),
            ]
            for sx, sy, sw, sh in structures:
                cv2.rectangle(img, (sx, sy), (sx+sw, sy+sh), (55, 50, 45), -1)
                cv2.rectangle(img, (sx+5, sy+5), (sx+sw-5, sy+sh), (65, 60, 55), -1)
                cv2.circle(img, (sx+sw//2, sy), sw//2, (70, 65, 60), -1)
            # Borular
            for py in [350, 450, 550]:
                cv2.line(img, (cx-550, py), (cx+600, py), (0, 150, 130), 3)
            # Buhar
            for _ in range(30):
                px = cx + np.random.randint(-400, 400)
                py = np.random.randint(50, 250)
                pr = np.random.randint(15, 50)
                cv2.circle(img, (px, py), pr, (60, 55, 50), -1)

        elif v_type == "factory":
            # 500 Bar Reaktör Sistemi - detaylı
            for rx, label in [(cx-300, "E-101"), (cx+300, "E-102")]:
                cv2.rectangle(img, (rx-80, cy-250), (rx+80, cy+250), (70, 65, 60), -1)
                cv2.rectangle(img, (rx-75, cy-245), (rx+75, cy+245), (85, 80, 75), -1)
                cv2.ellipse(img, (rx, cy-250), (80, 40), 0, 180, 360, (90, 85, 80), -1)
                cv2.ellipse(img, (rx, cy+250), (80, 40), 0, 0, 180, (90, 85, 80), -1)
                cv2.putText(img, label, (rx-35, cy+290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 210, 186), 1)
                # Basınç göstergesi
                cv2.circle(img, (rx+100, cy-100), 25, (40, 40, 40), -1)
                cv2.circle(img, (rx+100, cy-100), 22, (20, 20, 20), -1)
                cv2.line(img, (rx+100, cy-100), (rx+115, cy-115), (255, 50, 50), 2)
                cv2.putText(img, "500", (rx+82, cy-70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 200, 50), 1)
            # Boru bağlantıları
            cv2.line(img, (cx-220, cy), (cx+220, cy), (0, 180, 160), 6)
            cv2.line(img, (cx-220, cy-50), (cx+220, cy-50), (0, 150, 130), 4)
            cv2.line(img, (cx-220, cy+50), (cx+220, cy+50), (0, 150, 130), 4)
            # Seperatör
            cv2.rectangle(img, (cx-40, cy-150), (cx+40, cy+150), (60, 80, 75), -1)
            cv2.putText(img, "SEP", (cx-20, cy+180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 210, 186), 1)

        elif v_type == "laboratory":
            # Laboratuvar
            cv2.rectangle(img, (cx-400, cy-200), (cx+400, cy+200), (25, 30, 40), -1)
            cv2.rectangle(img, (cx-395, cy-195), (cx+395, cy+195), (30, 35, 50), -1)
            for mx in range(cx-350, cx+350, 120):
                cv2.rectangle(img, (mx, cy-150), (mx+80, cy-50), (20, 60, 50), -1)
                cv2.rectangle(img, (mx+5, cy-145), (mx+75, cy-55), (0, 120, 100), -1)
            # Faz diyagramı
            cv2.line(img, (cx-150, cy+150), (cx-150, cy-20), (150, 150, 150), 2)
            cv2.line(img, (cx-150, cy+150), (cx+200, cy+150), (150, 150, 150), 2)
            cv2.circle(img, (cx-50, cy+80), 8, (255, 255, 0), -1)
            cv2.putText(img, "CP", (cx-40, cy+75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        elif v_type == "product":
            # Altın ekstrakt
            pts = np.array([[cx, cy-250], [cx+150, cy+30], [cx+80, cy+200],
                           [cx-80, cy+200], [cx-150, cy+30]], np.int32)
            cv2.fillPoly(img, [pts], (40, 140, 180))
            cv2.fillPoly(img, [np.array([[cx, cy-200], [cx+100, cy+20], [cx+50, cy+150],
                           [cx-50, cy+150], [cx-100, cy+20]], np.int32)], (55, 175, 212))
            for _ in range(40):
                px = cx + np.random.randint(-100, 100)
                py = cy + np.random.randint(-150, 150)
                cv2.circle(img, (px, py), np.random.randint(2, 8), (80, 200, 230), -1)
            cv2.putText(img, "PURE EXTRACT", (cx-160, cy+270), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (55, 215, 255), 3)
            cv2.putText(img, "99.7% PURITY", (cx-120, cy+310), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)

        elif v_type == "map":
            # Küresel ağ
            cv2.circle(img, (cx, cy), 250, (30, 50, 60), 2)
            cv2.ellipse(img, (cx, cy), (250, 100), 0, 0, 360, (30, 50, 60), 1)
            cv2.ellipse(img, (cx, cy), (100, 250), 0, 0, 360, (30, 50, 60), 1)
            nodes = [(cx-350, cy-80), (cx-150, cy-180), (cx+50, cy-100),
                     (cx+300, cy-150), (cx+200, cy+120), (cx-100, cy+160),
                     (cx-280, cy+100), (cx+380, cy+50)]
            labels = ["Ankara", "Mersin", "Ordu", "Irak", "Sakarya", "Mertoglu", "EU", "USA"]
            for i, (nx, ny) in enumerate(nodes):
                cv2.circle(img, (nx, ny), 12, (0, 210, 186), -1)
                cv2.circle(img, (nx, ny), 20, (0, 210, 186), 2)
                cv2.circle(img, (nx, ny), 30, (0, 100, 90), 1)
                if i < len(labels):
                    cv2.putText(img, labels[i], (nx-30, ny-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    if np.random.random() > 0.4:
                        cv2.line(img, nodes[i], nodes[j], (0, 80, 70), 1)

        else:
            # Kapanış / Genel
            cv2.circle(img, (cx, cy), 200, (55, 175, 212), 3)
            cv2.circle(img, (cx, cy), 180, (55, 175, 212), 1)
            cv2.putText(img, "ARSEN PROCESS", (cx-250, cy+10), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (55, 215, 255), 4)
            cv2.putText(img, "SUPERCRITICAL CO2 TECHNOLOGIES", (cx-300, cy+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2)

        # KATMAN 3: Efektler
        img = ProceduralVisuals._add_particles(img, n=100, color=(0, 210, 186), opacity=0.35)
        img = ProceduralVisuals._add_light_rays(img, n=4)
        img = ProceduralVisuals._add_lens_flare(img, position=(0.75, 0.2), intensity=0.2)
        img = ProceduralVisuals._add_depth_fog(img)

        # Alt bilgi şeridi
        cv2.rectangle(img, (0, h-110), (w, h), (0, 0, 0), -1)
        cv2.line(img, (0, h-110), (w, h-110), (212, 175, 55), 2)
        cv2.putText(img, title.upper(), (50, h-45), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2)
        cv2.putText(img, "ARSEN PROCESS", (w-350, h-45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (212, 175, 55), 1)

        # Sinematik post-process
        img = ProceduralVisuals._cinematic_post(img)

        cv2.imwrite(output_path, img)
        return output_path


# ================================================================
# 2. RENK VE VİNYET YARDIMCILARI
# ================================================================
def apply_color_grade(frame, style="teal_orange"):
    result = frame.copy().astype(np.float32)
    if style == "teal_orange":
        result[:,:,0] = np.clip(result[:,:,0]*1.1+10, 0, 255)
        result[:,:,2] = np.clip(result[:,:,2]*1.05+5, 0, 255)
    elif style == "vintage_amber":
        result[:,:,0] *= 0.85; result[:,:,2] *= 1.1
        result = np.clip(result, 0, 255)
        return cv2.addWeighted(result.astype(np.uint8), 0.85, np.full_like(frame, 200), 0.15, 0)
    elif style == "cold_tech":
        result[:,:,0] *= 1.15; result[:,:,2] *= 0.85
    elif style == "noir":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = np.clip((gray-128)*1.5+128, 0, 255).astype(np.uint8)
        return cv2.merge([gray, gray, gray])
    elif style == "bleach_bypass":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        g3 = cv2.merge([gray, gray, gray])
        r = cv2.addWeighted(frame, 0.5, g3, 0.5, 0)
        return np.clip((r-128)*1.3+128, 0, 255).astype(np.uint8)
    return np.clip(result, 0, 255).astype(np.uint8)

def add_vignette(frame, strength=0.4):
    h, w = frame.shape[:2]
    Y, X = np.ogrid[:h, :w]
    r = np.sqrt((X-w/2)**2+(Y-h/2)**2)/np.sqrt((w/2)**2+(h/2)**2)
    vig = np.clip(1.0-r**1.5*strength, 0.3, 1.0)
    result = frame.copy()
    for c in range(3):
        result[:,:,c] = (result[:,:,c]*vig).astype(np.uint8)
    return result


# ================================================================
# 3. AI YÖNETMEN MOTORU
# ================================================================
class AIDirector:
    @staticmethod
    def _extract_json(raw_text):
        try:
            raw_text = raw_text.strip()
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = raw_text[start:end+1]
                json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                return json.loads(json_str)
        except: pass
        return None

    @staticmethod
    def _fallback_plan(brief):
        is_en = any(w in brief.lower() for w in ["the","and","for","with","project","create"])
        lang = "English" if is_en else "Türkçe"
        client = "Mr. Giorgi" if "giorgi" in brief.lower() else "Arşen Process"

        if lang == "English":
            scenes = [
                {"id":"S01","title":"SUPERCRITICAL DAWN","duration":10,"visual_type":"molecule","camera":"zoom_in",
                 "narration":f"Some transformations are invisible, but with supercritical technology they shape the future for {client}.",
                 "ai_image_prompt":"Extreme macro glowing CO2 molecule dark void supercritical mist blue green particles 8k cinematic photorealistic","sfx":"liquid_flow","transition":"crossfade"},
                {"id":"S02","title":"ENGINEERING ROOTS","duration":12,"visual_type":"refinery","camera":"aerial",
                 "narration":"Born from deep petrochemical roots in 2007, mastering extreme pressure systems and process engineering.",
                 "ai_image_prompt":"Cinematic aerial petrochemical refinery golden hour massive distillation columns steam rising steel pipelines 4k documentary","sfx":"factory_hum","transition":"dissolve"},
                {"id":"S03","title":"SC-CO2 BREAKTHROUGH","duration":12,"visual_type":"laboratory","camera":"zoom_in",
                 "narration":"In 2012, breakthrough R and D unlocked the green extraction power of supercritical carbon dioxide at the critical point.",
                 "ai_image_prompt":"Modern chemical engineering laboratory at night glowing phase diagram monitor stainless steel prototype cool blue fluorescent lighting 4k","sfx":"pressure_valve","transition":"cut"},
                {"id":"S04","title":"SYNTEGRA MANUFACTURING","duration":12,"visual_type":"factory","camera":"pan_right",
                 "narration":"SYNTEGRA manufacturing infrastructure delivers 500 bar industrial grade extraction systems with CNC precision and robotic welding.",
                 "ai_image_prompt":"Heavy industrial manufacturing floor robotic TIG welding on massive pressure vessel orange sparks flying steel blue dramatic lighting 4k","sfx":"welding","transition":"wipe"},
                {"id":"S05","title":"500 BAR POWER","duration":10,"visual_type":"factory","camera":"orbit",
                 "narration":"Operating at 500 bar maximum pressure ensuring unmatched extraction yield and molecular purity.",
                 "ai_image_prompt":"Twin massive 1000 liter stainless steel supercritical extraction vessels high pressure manifold digital gauges industrial lighting photorealistic 4k","sfx":"pressure_valve","transition":"crossfade"},
                {"id":"S06","title":"PURE EXTRACTS","duration":12,"visual_type":"product","camera":"macro",
                 "narration":"High value active compounds polyphenols carotenoids and essential oils isolated with zero toxic solvent residue.",
                 "ai_image_prompt":"Golden pure botanical extract dripping into amber glass vials scientific chromatography background warm golden macro lighting 4k","sfx":"liquid_flow","transition":"dissolve"},
                {"id":"S07","title":"FUWELL WELLNESS","duration":10,"visual_type":"product","camera":"pan_left",
                 "narration":"FUWELL translates pure supercritical bioactives into life enhancing functional wellness formulations for everyday health.",
                 "ai_image_prompt":"Modern minimalist wellness showroom premium supplement bottles fresh botanicals soft morning sunlight clean white interior 4k","sfx":"none","transition":"cut"},
                {"id":"S08","title":"GLOBAL PROJECTS","duration":12,"visual_type":"map","camera":"aerial",
                 "narration":"From Ankara to Mersin, Ordu to Iraq, engineering the future of green extraction across the globe.",
                 "ai_image_prompt":"Holographic world map with luminous teal connection lines radiating from Turkey to global industrial facility hubs dark navy background 4k","sfx":"whoosh","transition":"dissolve"},
                {"id":"S09","title":"SCALABLE DESIGN","duration":10,"visual_type":"factory","camera":"zoom_in",
                 "narration":"Modular expandable infrastructure ready for seamless capacity multiplication from 1000 to 10000 liters.",
                 "ai_image_prompt":"State of the art modular supercritical extraction facility clean room automated PLC control screens futuristic industrial design 4k","sfx":"factory_hum","transition":"crossfade"},
                {"id":"S10","title":"DESIGNING THE FUTURE","duration":10,"visual_type":"closing","camera":"slow_zoom",
                 "narration":f"Arşen Process. Designing the future today for {client} and the world.",
                 "ai_image_prompt":"Luminous golden Arsen Process logo floating in cosmic dark navy space surrounded by green supercritical particle nebula and light rays 8k epic","sfx":"whoosh","transition":"fade"}
            ]
        else:
            scenes = [
                {"id":"S01","title":"SÜPERKRİTİK DÖNÜŞÜM","duration":10,"visual_type":"molecule","camera":"zoom_in",
                 "narration":f"Bazı dönüşümler gözle görülmez ama doğru teknolojiyle {client} için geleceğe yön verir.",
                 "ai_image_prompt":"Extreme macro glowing CO2 molecule dark void supercritical mist 8k cinematic","sfx":"liquid_flow","transition":"crossfade"},
                {"id":"S02","title":"MÜHENDİSLİK MİRASI","duration":12,"visual_type":"refinery","camera":"aerial",
                 "narration":"2007 yılında petrokimya sektöründe yüksek basınç ve proses mühendisliği temelleriyle başlayan yolculuk.",
                 "ai_image_prompt":"Cinematic aerial petrochemical refinery golden hour steam steel columns 4k","sfx":"factory_hum","transition":"dissolve"},
                {"id":"S03","title":"2012 AR-GE ATILIMI","duration":12,"visual_type":"laboratory","camera":"zoom_in",
                 "narration":"2012 yılında süperkritik karbondioksit teknolojisinde başlatılan Ar-Ge atılımı.",
                 "ai_image_prompt":"Modern chemical engineering laboratory glowing phase diagram cool blue 4k","sfx":"pressure_valve","transition":"cut"},
                {"id":"S04","title":"SYNTEGRA İMALAT","duration":12,"visual_type":"factory","camera":"pan_right",
                 "narration":"SYNTEGRA imalat altyapısıyla 500 bar basınca dayanıklı endüstriyel sistemler üretilmektedir.",
                 "ai_image_prompt":"Heavy industrial manufacturing robotic TIG welding pressure vessel orange sparks 4k","sfx":"welding","transition":"wipe"},
                {"id":"S05","title":"500 BAR GÜÇ","duration":10,"visual_type":"factory","camera":"orbit",
                 "narration":"500 bar maksimum çalışma basıncında en yüksek saflık ve verim.",
                 "ai_image_prompt":"Twin 1000L stainless steel extraction vessels high pressure pipes digital gauges 4k","sfx":"pressure_valve","transition":"crossfade"},
                {"id":"S06","title":"SAF ÇIKTILAR","duration":12,"visual_type":"product","camera":"macro",
                 "narration":"Sıfır solvent kalıntısıyla yüksek konsantrasyonlu aktif bileşenler.",
                 "ai_image_prompt":"Golden botanical extract amber glass vials scientific lab warm light 4k","sfx":"liquid_flow","transition":"dissolve"},
                {"id":"S07","title":"FUWELL VİZYONU","duration":10,"visual_type":"product","camera":"pan_left",
                 "narration":"FUWELL ile süperkritik bilimi insan sağlığına dokunan wellness ürünlerine dönüşüyor.",
                 "ai_image_prompt":"Modern wellness showroom premium supplements fresh botanicals sunlight 4k","sfx":"none","transition":"cut"},
                {"id":"S08","title":"KÜRESEL PROJELER","duration":12,"visual_type":"map","camera":"aerial",
                 "narration":"Ankara Mersin Ordu ve uluslararası projelerle yerel hammaddeleri küresel değere dönüştürüyoruz.",
                 "ai_image_prompt":"Holographic world map luminous connection lines industrial facilities 4k","sfx":"whoosh","transition":"dissolve"},
                {"id":"S09","title":"MODÜLER MİMARİ","duration":10,"visual_type":"factory","camera":"zoom_in",
                 "narration":"Geleceğe hazır kapasitesi kolayca artırılabilir esnek proses mimarisi.",
                 "ai_image_prompt":"Modular extraction facility clean room automated control screens futuristic 4k","sfx":"factory_hum","transition":"crossfade"},
                {"id":"S10","title":"GELECEĞİ TASARLIYORUZ","duration":10,"visual_type":"closing","camera":"slow_zoom",
                 "narration":"Arşen Process. Geleceği bugün tasarlıyoruz.",
                 "ai_image_prompt":"Golden Arsen Process logo cosmic dark navy space supercritical particle nebula 8k","sfx":"whoosh","transition":"fade"}
            ]

        return {"film_title":f"Arşen Process — {client}","total_duration_seconds":112,
                "color_palette":"teal_orange","music_mood":"epic","narration_language":lang,"scenes":scenes}

    @staticmethod
    def plan_film(brief):
        prompt = f"Create a 10-scene film JSON plan for: {brief}. Return only valid JSON."
        try:
            encoded = urllib.parse.quote(prompt)
            url = f"https://text.pollinations.ai/{encoded}"
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
            parsed = AIDirector._extract_json(raw)
            if parsed and "scenes" in parsed and len(parsed["scenes"]) > 0:
                return parsed
        except: pass
        return AIDirector._fallback_plan(brief)

    @staticmethod
    def generate_all_images(plan, output_dir="ai_generated"):
        os.makedirs(output_dir, exist_ok=True)
        results = []
        for sc in plan.get("scenes", []):
            sid = sc.get("id", "S00")
            prompt = sc.get("ai_image_prompt", "")
            out_path = os.path.join(output_dir, f"{sid}.jpg")
            downloaded = False
            if prompt:
                for attempt in range(3):
                    try:
                        seed = np.random.randint(1, 99999)
                        encoded = urllib.parse.quote(prompt)
                        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed={seed}"
                        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            data = resp.read()
                            if len(data) > 5000:
                                with open(out_path, 'wb') as f:
                                    f.write(data)
                                downloaded = True
                                break
                    except: pass
                    time.sleep(1)
            if not downloaded:
                ProceduralVisuals.create_scene_visual(sc, out_path)
            results.append({"id":sid,"path":out_path,"status":"ok"})
        return results

    @staticmethod
    def save_plan(plan, filename="film_plan.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        return filename


# ================================================================
# 4. 3D REAKTÖR, BULUT, MÜŞTERİ, AVATAR
# ================================================================
class Reactor3D:
    @staticmethod
    def build_reactor(pressure=500, temperature=60, volume=1000):
        import plotly.graph_objects as go
        fig = go.Figure()
        theta = np.linspace(0, 2*np.pi, 40)
        z_body = np.linspace(-2, 2, 20)
        tg, zg = np.meshgrid(theta, z_body)
        r = 0.8
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg,
            colorscale=[[0,'#3a3a4a'],[0.5,'#8E9AAF'],[1,'#5a5a6a']], opacity=0.85, showscale=False))
        phi = np.linspace(0, np.pi/2, 15)
        tc = np.linspace(0, 2*np.pi, 40)
        pg, tcg = np.meshgrid(phi, tc)
        xt = r*np.sin(pg)*np.cos(tcg); yt = r*np.sin(pg)*np.sin(tcg); zt = r*np.cos(pg)+2
        fig.add_trace(go.Surface(x=xt, y=yt, z=zt, colorscale=[[0,'#5a5a6a'],[1,'#8E9AAF']], opacity=0.9, showscale=False))
        fig.add_trace(go.Surface(x=xt, y=yt, z=-r*np.cos(pg)-2, colorscale=[[0,'#5a5a6a'],[1,'#8E9AAF']], opacity=0.9, showscale=False))
        fc = '#00D2BA' if pressure >= 73.8 and temperature >= 31.1 else '#4488FF'
        fz, ft = np.meshgrid(np.linspace(-1.8, 1.2, 15), theta)
        fig.add_trace(go.Surface(x=0.7*np.cos(ft), y=0.7*np.sin(ft), z=fz, colorscale=[[0,fc],[1,'#FFFFFF']], opacity=0.3, showscale=False))
        fig.update_layout(title=dict(text=f"SC-CO2 | {volume}L | {pressure} Bar | {temperature}C", font=dict(color="#D4AF37")),
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='#0B0F19', camera=dict(eye=dict(x=2.2,y=2.2,z=1.2))),
            paper_bgcolor='#0B0F19', height=500, showlegend=False, margin=dict(l=0,r=0,t=40,b=0))
        return fig

    @staticmethod
    def build_process_flow():
        import plotly.graph_objects as go
        fig = go.Figure()
        for name, x, color in [("CO2 Tank",-4,"#4488FF"),("Pompa",-2,"#FF8C00"),("Isitici",0,"#FF4444"),("Ekstraktor",2,"#00D2BA"),("Seperator",4,"#D4AF37"),("Urun",6,"#4CAF50")]:
            fig.add_trace(go.Scatter3d(x=[x],y=[0],z=[0], mode="markers+text", marker=dict(size=14,color=color), text=[name], textposition="top center", textfont=dict(color="white",size=11), showlegend=False))
        fig.add_trace(go.Scatter3d(x=[-4,6],y=[0,0],z=[0,0], mode="lines", line=dict(color="#8E9AAF",width=6), showlegend=False))
        fig.update_layout(title=dict(text="SC-CO2 Proses Akisi", font=dict(color="#D4AF37",size=14)),
            scene=dict(xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False),bgcolor='#0B0F19'),
            paper_bgcolor='#0B0F19', height=300, margin=dict(l=0,r=0,t=30,b=0))
        return fig

class CloudRender:
    @staticmethod
    def generate_colab_notebook(scenes, project_name="arsen_film"):
        import nbformat
        nb = nbformat.v4.new_notebook()
        nb.cells = [nbformat.v4.new_markdown_cell(f"# {project_name}"), nbformat.v4.new_code_cell("!pip install manim moviepy edge-tts opencv-python pillow numpy -q"),
            nbformat.v4.new_code_cell(f"import json\nSCENES = {json.dumps(scenes, ensure_ascii=False)}")]
        path = f"{project_name}_colab.ipynb"
        with open(path, "w", encoding="utf-8") as f: nbformat.write(nb, f)
        return path

class ClientPortal:
    @staticmethod
    def generate_client_film(client_name, company, industry, project_specs, investment, location, products):
        brief = f"{client_name} ({company}) {industry}. {project_specs}. {investment}. {location}. {products}."
        plan = AIDirector.plan_film(brief)
        images = AIDirector.generate_all_images(plan, f"ai_generated/{client_name}")
        return {"client":client_name,"plan":plan,"images":images,"status":"ready"}

class AIAvatar:
    @staticmethod
    def generate_avatar_image(ref_path=None, output_path=None, expression="confident", setting="factory"):
        if not output_path: output_path = f"ai_generated/avatar_{int(time.time())}.jpg"
        prompts = {"confident_factory":"Professional Turkish male engineer 40s confident smile navy shirt modern factory stainless steel vessels cinematic 8K",
            "confident_lab":"Professional Turkish male engineer 40s white lab coat chemical laboratory glowing monitors cinematic 8K",
            "confident_office":"Professional Turkish male CEO 40s dark suit modern executive office glass walls cinematic 8K",
            "presentation":"Professional Turkish male presenter 40s gesturing holographic display dark stage spotlight 8K"}
        key = f"{expression}_{setting}" if f"{expression}_{setting}" in prompts else "confident_factory"
        try:
            encoded = urllib.parse.quote(prompts[key])
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
            urllib.request.urlretrieve(url, output_path)
            return output_path
        except:
            img = np.zeros((1024,1024,3), dtype=np.uint8)
            for y in range(1024): img[y,:] = (int(15+y/1024*20), int(20+y/1024*25), int(35+y/1024*40))
            cv2.circle(img, (512,350), 120, (60,55,50), -1)
            cv2.ellipse(img, (512,750), (200,280), 0, 180, 360, (60,55,50), -1)
            cv2.imwrite(output_path, img)
            return output_path

    @staticmethod
    def create_presentation_slides(client_name, project_data, avatar_path=None):
        os.makedirs("ai_generated/slides", exist_ok=True)
        slides_data = [
            (f"Hoş Geldiniz Sayın {client_name}", "Arşen Process olarak size özel sunum."),
            ("Süperkritik CO₂ Teknolojisi", f"Projeniz: {project_data}. 500 bar."),
            ("SYNTEGRA İmalat Gücü", "Uçtan uca kendi fabrikamızda üretim."),
            ("Yatırım Geri Dönüşü", "36 ay eşit taksit. Sıfır işletme maliyeti."),
            ("Sonraki Adımlar", "Ekibimiz 48 saat içinde iletişime geçecektir."),
        ]
        slides = []
        for i, (title, body) in enumerate(slides_data):
            path = f"ai_generated/slides/slide_{i+1}.jpg"
            img = np.zeros((1080,1920,3), dtype=np.uint8)
            for y in range(1080): img[y,:] = (int(10+y/1080*15), int(15+y/1080*20), int(30+y/1080*35))
            cv2.rectangle(img, (0,0), (600,1080), (20,18,15), -1)
            cv2.circle(img, (300,400), 150, (50,45,40), -1)
            cv2.line(img, (620,100), (620,980), (212,175,55), 2)
            cv2.putText(img, title, (660,200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
            cv2.putText(img, body[:60], (660,300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,200), 1)
            cv2.rectangle(img, (0,1000), (1920,1080), (0,0,0), -1)
            cv2.putText(img, f"Arşen Process | www.arsenprocess.com", (40,1050), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140,130,100), 1)
            cv2.imwrite(path, img)
            slides.append(path)
        return slides

    @staticmethod
    def generate_avatar_video(slides, audio_paths=None, output_path=None):
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        if not output_path: output_path = f"ai_generated/avatar_pres_{int(time.time())}.mp4"
        clips = []
        for i, sp in enumerate(slides):
            if not os.path.exists(sp): continue
            ic = ImageClip(sp).set_duration(8).resize((1920,1080))
            if audio_paths and i < len(audio_paths) and os.path.exists(audio_paths[i]):
                ac = AudioFileClip(audio_paths[i])
                ic = ic.set_duration(max(8, ac.duration+1)).set_audio(ac)
            clips.append(ic.crossfadein(0.5).crossfadeout(0.5))
        if not clips: return None
        final = concatenate_videoclips(clips, method="compose", padding=-0.5)
        final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")
        return output_path


# ================================================================
# 5. OTONOM FİLM ÜRETİM HATTI v9.0 (SİNEMATİK)
# ================================================================
class AutoPipeline:
    @staticmethod
    def run(brief, output_name="OTONOM_FILM", lang="Türkçe", progress_callback=None):
        import edge_tts, asyncio
        from moviepy.editor import (VideoFileClip, AudioFileClip,
            concatenate_videoclips, CompositeAudioClip, concatenate_audioclips)

        log = []
        def report(step, pct, msg):
            log.append(f"[{step}] {msg}")
            if progress_callback: progress_callback(pct, msg)

        report("SENARYO", 5, "AI senaryo yaziyor...")
        plan = AIDirector.plan_film(brief)
        scenes = plan.get("scenes", [])
        total = len(scenes)
        report("SENARYO", 15, f"{total} sahne hazir")

        report("GORSEL", 18, "Sinematik gorseller (AI + Procedural)...")
        img_dir = f"ai_generated/{output_name}"
        os.makedirs(img_dir, exist_ok=True)
        image_paths = {}
        for i, sc in enumerate(scenes):
            sid = sc.get("id", f"S{i+1:02d}")
            out_img = os.path.join(img_dir, f"{sid}.jpg")
            pct = 18 + int(22*(i+1)/total)
            downloaded = False
            prompt = sc.get("ai_image_prompt", "")
            if prompt:
                for attempt in range(3):
                    try:
                        seed = np.random.randint(1, 99999)
                        encoded = urllib.parse.quote(prompt)
                        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed={seed}"
                        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            data = resp.read()
                            if len(data) > 5000:
                                with open(out_img, 'wb') as f: f.write(data)
                                downloaded = True; break
                    except: time.sleep(1)
            if not downloaded:
                ProceduralVisuals.create_scene_visual(sc, out_img)
            image_paths[sid] = out_img
            report("GORSEL", pct, f"{sid} hazir")

        report("SES", 42, "Seslendirme...")
        os.makedirs("audio_temp", exist_ok=True)
        voice_map = {"Türkçe":"tr-TR-AhmetNeural","English":"en-US-GuyNeural","العربية":"ar-SA-HamedNeural"}
        voice = voice_map.get(lang, "tr-TR-AhmetNeural")
        audio_paths = {}
        async def make_audio():
            for sc in scenes:
                sid = sc.get("id","S00"); narr = sc.get("narration","")
                if not narr: continue
                out = f"audio_temp/{output_name}_{sid}.mp3"
                try:
                    comm = edge_tts.Communicate(narr, voice, rate="-3%")
                    await comm.save(out); audio_paths[sid] = out
                except: pass
        asyncio.run(make_audio())
        report("SES", 55, f"{len(audio_paths)} ses hazir")

        report("VIDEO", 57, "Sinematik klipler (Ken Burns + Efektler)...")
        clip_dir = f"output_clips/{output_name}"
        os.makedirs(clip_dir, exist_ok=True)
        color_grade = plan.get("color_palette", "teal_orange")
        clip_paths = []

        cam_map = {"zoom_in":(1.0,1.3,0.5,0.5,0.5,0.45),"zoom_out":(1.3,1.0,0.5,0.45,0.5,0.5),
            "pan_right":(1.2,1.2,0.35,0.5,0.65,0.5),"pan_left":(1.2,1.2,0.65,0.5,0.35,0.5),
            "orbit":(1.1,1.25,0.4,0.4,0.6,0.6),"aerial":(1.0,1.15,0.5,0.6,0.5,0.4),
            "macro":(1.0,1.5,0.5,0.5,0.5,0.5),"slow_zoom":(1.0,1.15,0.5,0.5,0.5,0.5)}

        for i, sc in enumerate(scenes):
            sid = sc.get("id", f"S{i+1:02d}")
            pct = 57 + int(28*(i+1)/total)
            duration = sc.get("duration", 8)
            camera = sc.get("camera", "zoom_in")
            title = sc.get("title", "")
            img_path = image_paths.get(sid)
            out_clip = os.path.join(clip_dir, f"{sid}.mp4")

            ap = audio_paths.get(sid)
            if ap and os.path.exists(ap):
                try:
                    ac = AudioFileClip(ap); duration = max(duration, ac.duration+1.0); ac.close()
                except: pass

            img_cv = cv2.imread(img_path) if img_path else None
            if img_cv is not None:
                h, w = img_cv.shape[:2]
                writer = cv2.VideoWriter(out_clip, cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920,1080))
                ss,es,sx,sy,ex,ey = cam_map.get(camera, cam_map["zoom_in"])
                tf = int(duration*30)
                for fi in range(tf):
                    t = fi/max(tf-1,1); ts = t*t*(3-2*t)
                    scale = ss+(es-ss)*ts; cx = sx+(ex-sx)*ts; cy = sy+(ey-sy)*ts
                    cw, ch = int(w/scale), int(h/scale)
                    x1 = max(0,min(int(cx*w-cw/2), w-cw))
                    y1 = max(0,min(int(cy*h-ch/2), h-ch))
                    crop = cv2.resize(img_cv[y1:y1+ch, x1:x1+cw], (1920,1080), interpolation=cv2.INTER_LANCZOS4)
                    crop = apply_color_grade(crop, color_grade)
                    crop = add_vignette(crop, 0.35)
                    # Hafif parçacık efekti (her 5 karede bir)
                    if fi % 5 == 0:
                        overlay = crop.copy()
                        for _ in range(8):
                            px, py = np.random.randint(0,1920), np.random.randint(0,1080)
                            cv2.circle(overlay, (px,py), np.random.randint(1,3), (0,180,160), -1)
                        crop = cv2.addWeighted(overlay, 0.15, crop, 0.85, 0)
                    if title and fi > 15 and fi < tf-15:
                        ov = crop.copy()
                        cv2.rectangle(ov, (0,990), (1920,1080), (0,0,0), -1)
                        cv2.addWeighted(ov, 0.5, crop, 0.5, 0, crop)
                        cv2.putText(crop, title[:50], (40,1045), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (212,175,55), 2)
                    writer.write(crop)
                writer.release()
                clip_paths.append(out_clip)
                report("VIDEO", pct, f"{sid} hazir ({duration:.1f}sn)")

        report("MONTAJ", 88, "Birlestiriliyor...")
        final_clips = []
        for sc in scenes:
            sid = sc.get("id","S00")
            cp = os.path.join(clip_dir, f"{sid}.mp4")
            ap = audio_paths.get(sid)
            if not os.path.exists(cp): continue
            vc = VideoFileClip(cp)
            if ap and os.path.exists(ap):
                ac = AudioFileClip(ap)
                vc = vc.set_duration(max(vc.duration, ac.duration+0.5)).set_audio(ac)
            vc = vc.crossfadein(0.4).crossfadeout(0.4)
            final_clips.append(vc)

        if not final_clips:
            return {"status":"error","log":log,"error":"Klip yok"}

        final = concatenate_videoclips(final_clips, method="compose", padding=-0.4)
        mp = "assets/music/bg_music.mp3"
        if os.path.exists(mp):
            try:
                bg = AudioFileClip(mp)
                if bg.duration < final.duration:
                    bg = concatenate_audioclips([bg]*(int(final.duration/bg.duration)+1)).subclip(0, final.duration)
                else: bg = bg.subclip(0, final.duration)
                bg = bg.volumex(0.06)
                if final.audio: final = final.set_audio(CompositeAudioClip([final.audio, bg]))
            except: pass

        out_path = f"{output_name}_FINAL.mp4"
        report("MONTAJ", 95, "MP4 yaziliyor...")
        final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", threads=4)
        for c in final_clips: c.close()
        final.close()
        report("TAMAM", 100, f"FILM HAZIR: {out_path}")
        return {"status":"success","output":out_path,"duration":final.duration,"scenes":total,"log":log,"plan":plan}
# ================================================================
# 6. GERÇEK AI VİDEO MOTORU (Hugging Face CogVideoX)
# OpenCV çizimi DEĞİL, gerçek fotogerçekçi AI video üretir
# ================================================================
class RealAIVideo:
    """
    Hugging Face Inference API kullanarak CogVideoX-5B modeli ile
    gerçek sinematik videolar üretir. Ücretsiz tier'da çalışır.
    """

    API_URL = "https://api-inference.huggingface.co/models/THUDM/CogVideoX-5b"

    @staticmethod
    def generate_video(prompt, api_key, output_path=None, duration_sec=6):
        """
        Metin prompt'undan gerçek AI videosu üretir.
        prompt: İngilizce, detaylı, sinematik açıklama
        api_key: Hugging Face access token (hf_xxxxx)
        output_path: Çıktı dosya yolu
        """
        import requests

        if not output_path:
            output_path = f"ai_generated/real_ai_{int(time.time())}.mp4"

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_frames": 49,
                "fps": 8,
                "guidance_scale": 6.0,
                "num_inference_steps": 50,
            }
        }

        try:
            response = requests.post(
                RealAIVideo.API_URL,
                headers=headers,
                json=payload,
                timeout=300  # 5 dakika timeout (AI video üretimi yavaş)
            )

            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return {"status": "ok", "path": output_path}

            elif response.status_code == 503:
                # Model yükleniyor, bekle ve tekrar dene
                wait_time = response.json().get("estimated_time", 60)
                return {"status": "loading", "wait": wait_time,
                        "msg": f"Model yükleniyor, {wait_time:.0f} saniye bekleyin"}

            elif response.status_code == 429:
                return {"status": "rate_limit",
                        "msg": "Ücretsiz kota doldu. Birkaç saat sonra tekrar deneyin."}

            else:
                return {"status": "error",
                        "msg": f"API hatası: {response.status_code} - {response.text[:200]}"}

        except requests.exceptions.Timeout:
            return {"status": "timeout", "msg": "İstek zaman aşımına uğradı (5dk). Tekrar deneyin."}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

    @staticmethod
    def generate_scene_video(scene_data, api_key, output_path=None):
        """Bir sahne için otomatik prompt oluşturup AI video üretir."""
        prompt = scene_data.get("ai_image_prompt", "")
        if not prompt:
            v_type = scene_data.get("visual_type", "factory")
            prompts = {
                "molecule": "Extreme macro shot of a glowing CO2 molecule transforming into supercritical fluid mist, blue-green particles swirling in dark void, cinematic 4K",
                "refinery": "Cinematic aerial drone shot of a massive petrochemical refinery at golden hour, steam rising from distillation columns, steel pipelines stretching to horizon, 4K documentary",
                "laboratory": "Modern chemical engineering laboratory at night, glowing blue phase diagram on monitor, stainless steel prototype extraction system, cool fluorescent lighting, 4K",
                "factory": "Heavy industrial manufacturing floor, robotic TIG welding on massive stainless steel pressure vessel, orange sparks flying in slow motion, dramatic steel-blue lighting, 4K cinematic",
                "product": "Macro shot of golden botanical extract dripping into amber glass vials, scientific laboratory background with chromatography equipment, warm golden lighting, 4K",
                "map": "Holographic 3D world map with luminous teal connection lines radiating from Turkey to global industrial hubs, dark navy space background, futuristic data visualization, 4K",
                "closing": "Luminous golden corporate logo floating in cosmic dark navy space, surrounded by green supercritical particle nebula and volumetric light rays, epic cinematic 8K",
            }
            prompt = prompts.get(v_type, prompts["factory"])

        return RealAIVideo.generate_video(prompt, api_key, output_path)

    @staticmethod
    def generate_full_film(plan, api_key, output_name="AI_FILM", progress_callback=None):
        """
        Tüm film planı için sahne sahne gerçek AI videoları üretir
        ve bunları seslendirme ile birleştirir.
        """
        import edge_tts
        import asyncio
        from moviepy.editor import (VideoFileClip, AudioFileClip,
            concatenate_videoclips, CompositeAudioClip, concatenate_audioclips)

        log = []
        def report(pct, msg):
            log.append(msg)
            if progress_callback: progress_callback(pct, msg)

        scenes = plan.get("scenes", [])
        total = len(scenes)
        clip_dir = f"ai_generated/{output_name}_clips"
        os.makedirs(clip_dir, exist_ok=True)
        os.makedirs("audio_temp", exist_ok=True)

        lang = plan.get("narration_language", "Türkçe")
        voice_map = {"Türkçe":"tr-TR-AhmetNeural","English":"en-US-GuyNeural"}
        voice = voice_map.get(lang, "tr-TR-AhmetNeural")

        clip_paths = []
        audio_paths = {}

        for i, sc in enumerate(scenes):
            sid = sc.get("id", f"S{i+1:02d}")
            pct = int(90 * (i + 1) / total)

            # 1. AI Video üret
            report(pct, f"{sid}: AI video üretiliyor...")
            video_path = os.path.join(clip_dir, f"{sid}.mp4")
            result = RealAIVideo.generate_scene_video(sc, api_key, video_path)

            if result["status"] == "ok":
                clip_paths.append(video_path)
                report(pct, f"{sid}: ✅ AI video hazır")
            elif result["status"] == "loading":
                report(pct, f"{sid}: ⏳ Model yükleniyor ({result.get('wait',60)}sn)...")
                time.sleep(min(result.get("wait", 60), 120))
                result = RealAIVideo.generate_scene_video(sc, api_key, video_path)
                if result["status"] == "ok":
                    clip_paths.append(video_path)
                else:
                    report(pct, f"{sid}: ⚠ AI video başarısız, procedural fallback")
            else:
                report(pct, f"{sid}: ⚠ {result.get('msg','hata')}, procedural fallback")

            # 2. Seslendirme üret
            narr = sc.get("narration", "")
            if narr:
                audio_path = f"audio_temp/{output_name}_{sid}.mp3"
                try:
                    comm = edge_tts.Communicate(narr, voice, rate="-3%")
                    asyncio.run(comm.save(audio_path))
                    audio_paths[sid] = audio_path
                except: pass

        # 3. Birleştir
        report(92, "Klipler birleştiriliyor...")
        final_clips = []
        for sc in scenes:
            sid = sc.get("id", "S00")
            # AI video varsa onu kullan, yoksa procedural
            cp = os.path.join(clip_dir, f"{sid}.mp4")
            if not os.path.exists(cp):
                cp = f"output_clips/{output_name}/{sid}.mp4"
            if not os.path.exists(cp):
                continue

            vc = VideoFileClip(cp)
            ap = audio_paths.get(sid)
            if ap and os.path.exists(ap):
                ac = AudioFileClip(ap)
                vc = vc.set_duration(max(vc.duration, ac.duration + 0.5)).set_audio(ac)
            vc = vc.crossfadein(0.5).crossfadeout(0.5)
            final_clips.append(vc)

        if not final_clips:
            return {"status": "error", "log": log, "error": "Hiç klip üretilemedi"}

        final = concatenate_videoclips(final_clips, method="compose", padding=-0.5)

        # Müzik
        mp = "assets/music/bg_music.mp3"
        if os.path.exists(mp):
            try:
                bg = AudioFileClip(mp)
                if bg.duration < final.duration:
                    bg = concatenate_audioclips([bg]*(int(final.duration/bg.duration)+1)).subclip(0, final.duration)
                else: bg = bg.subclip(0, final.duration)
                bg = bg.volumex(0.06)
                if final.audio: final = final.set_audio(CompositeAudioClip([final.audio, bg]))
            except: pass

        out_path = f"{output_name}_AI_FINAL.mp4"
        report(97, "Final MP4 yazılıyor...")
        final.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", threads=4)
        for c in final_clips: c.close()
        final.close()

        report(100, f"🎉 FİLM HAZIR: {out_path}")
        return {"status": "success", "output": out_path, "duration": final.duration,
                "scenes": len(final_clips), "log": log}