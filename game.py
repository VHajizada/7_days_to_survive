import pygame
import random
import sys
import json
import os

# Pygame-in işə salınması
pygame.init()
pygame.mixer.init()

# Ekran Parametrləri
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Rənglər (Post-Apokaliptik Tünd Dizayn)
BG_COLOR = (12, 15, 20)
PANEL_COLOR = (22, 28, 38)
ACCENT_RED = (217, 4, 41)
ACCENT_GREEN = (46, 196, 182)
ACCENT_YELLOW = (255, 159, 28)
TEXT_WHITE = (240, 243, 246)
TEXT_MUTED = (138, 147, 157)
BORDER_COLOR = (43, 58, 79)

# Yaddaş Faylı
SAVE_FILE = "savegame.json"

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("7 Days to Survive // Post-Apocalyptic Simulation")
        self.clock = pygame.time.Clock()
        
        # Şriftlər
        try:
            self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_large = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_med = pygame.font.SysFont("Arial", 16)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_large = pygame.font.Font(None, 26)
            self.font_med = pygame.font.Font(None, 20)

        self.state = "MENU" # MENU, GAME, HOW_TO, SETTINGS, GAMEOVER, VICTORY
        self.sound_enabled = True
        
        self.reset_stats()
        self.logs = ["Simulyasiya başladı. Hərbi xilasetmə dəstəsi gələnə qədər 7 gün sağ qalın."]

    def reset_stats(self):
        self.health = 100.0
        self.hunger = 100.0
        self.thirst = 100.0
        self.energy = 100.0
        self.day = 1
        self.hour = 8
        self.minute = 0
        self.inventory = {
            "Canned Food": 2,
            "Water Bottle": 2,
            "Medkit": 1,
            "Wood": 3,
            "Scrap Metal": 2
        }
        self.shelter_defense = 10
        self.logs = ["1-ci Gün başladı. Ehtiyatlar tapın, sığınacağınızı gücləndirin."]

    def save_game(self):
        data = {
            "health": self.health, "hunger": self.hunger, "thirst": self.thirst,
            "energy": self.energy, "day": self.day, "hour": self.hour,
            "minute": self.minute, "inventory": self.inventory,
            "shelter_defense": self.shelter_defense, "logs": self.logs
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
            self.add_log("Oyun yaddaşa yazıldı.")
        except Exception as e:
            self.add_log(f"Yaddaşa yazma xətası: {e}")

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                self.health = data["health"]
                self.hunger = data["hunger"]
                self.thirst = data["thirst"]
                self.energy = data["energy"]
                self.day = data["day"]
                self.hour = data["hour"]
                self.minute = data["minute"]
                self.inventory = data["inventory"]
                self.shelter_defense = data.get("shelter_defense", 10)
                self.logs = data.get("logs", ["Oyun yükləndi."])
                self.state = "GAME"
                self.add_log("Oyun uğurla yükləndi.")
            except Exception as e:
                self.add_log(f"Yükləmə xətası: {e}")
        else:
            self.add_log("Yaddaş faylı tapılmadı.")

    def add_log(self, text):
        time_str = f"[Gün {self.day} {self.hour:02d}:{self.minute:02d}]"
        self.logs.insert(0, f"{time_str} {text}")
        if len(self.logs) > 30:
            self.logs.pop()

    def advance_time(self, hours=1):
        self.hour += hours
        self.hunger -= hours * 1.5
        self.thirst -= hours * 2.2
        self.energy -= hours * 1.2
        
        if self.hunger <= 0:
            self.hunger = 0
            self.health -= 3 * hours
        if self.thirst <= 0:
            self.thirst = 0
            self.health -= 5 * hours
        if self.energy <= 0:
            self.energy = 0
            self.health -= 2 * hours
            
        if self.health <= 0:
            self.health = 0
            self.state = "GAMEOVER"

        if self.hour >= 24:
            self.hour -= 24
            self.day += 1
            self.trigger_night_event()
            if self.day > 7:
                self.state = "VICTORY"

    def trigger_night_event(self):
        event_roll = random.random()
        if event_roll < 0.4:
            damage = random.randint(5, 15) - int(self.shelter_defense / 5)
            damage = max(0, damage)
            if damage > 0:
                self.health -= damage
                self.add_log(f"Gecə hücumu! Məxluqlar sığınacağı yarıb keçdi. {damage} zərər aldınız.")
            else:
                self.add_log("Gecə hücumu! Sığınacaq müdafiəsi dayanıqlı oldu.")
        elif event_roll < 0.7:
            found_wood = random.randint(1, 3)
            self.inventory["Wood"] = self.inventory.get("Wood", 0) + found_wood
            self.add_log(f"Sakit gecə. Ətrafdan {found_wood} odun topladınız.")
        else:
            self.add_log("Soyuq gecə. Enerji daha sürətlə tükəndi.")
            self.energy = max(0, self.energy - 15)

    def run(self):
        while True:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.state == "MENU":
                    if self.btn_new_game.collidepoint(mouse_pos):
                        self.reset_stats()
                        self.state = "GAME"
                    elif self.btn_continue.collidepoint(mouse_pos):
                        self.load_game()
                    elif self.btn_how.collidepoint(mouse_pos):
                        self.state = "HOW_TO"
                    elif self.btn_settings.collidepoint(mouse_pos):
                        self.state = "SETTINGS"
                    elif self.btn_exit.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                        
                elif self.state in ["HOW_TO", "SETTINGS"]:
                    if self.btn_back.collidepoint(mouse_pos):
                        self.state = "MENU"
                        
                elif self.state in ["GAMEOVER", "VICTORY"]:
                    if self.btn_menu.collidepoint(mouse_pos):
                        self.state = "MENU"

                elif self.state == "GAME":
                    if self.btn_supermarket.collidepoint(mouse_pos):
                        self.explore_location("Supermarket")
                    elif self.btn_hospital.collidepoint(mouse_pos):
                        self.explore_location("Hospital")
                    elif self.btn_police.collidepoint(mouse_pos):
                        self.explore_location("Police Station")
                    elif self.btn_industrial.collidepoint(mouse_pos):
                        self.explore_location("Industrial Zone")
                    elif self.btn_rest.collidepoint(mouse_pos):
                        self.rest_action()
                    elif self.btn_craft.collidepoint(mouse_pos):
                        self.craft_action()
                    elif self.btn_eat.collidepoint(mouse_pos):
                        self.consume_item("Canned Food", "hunger", 35)
                    elif self.btn_drink.collidepoint(mouse_pos):
                        self.consume_item("Water Bottle", "thirst", 40)
                    elif self.btn_medkit.collidepoint(mouse_pos):
                        self.consume_item("Medkit", "health", 50)
                    elif self.btn_save.collidepoint(mouse_pos):
                        self.save_game()

    def explore_location(self, loc_name):
        self.advance_time(2)
        roll = random.random()
        if loc_name == "Supermarket":
            if roll < 0.6:
                food = random.randint(1, 2)
                self.inventory["Canned Food"] = self.inventory.get("Canned Food", 0) + food
                self.add_log(f"Supermarket: {food} konserv tapıldı.")
            else:
                self.health -= 10
                self.add_log("Supermarket tələsi! 10 HP itirdiniz.")
        elif loc_name == "Hospital":
            if roll < 0.65:
                meds = random.randint(1, 2)
                self.inventory["Medkit"] = self.inventory.get("Medkit", 0) + meds
                self.add_log(f"Xəstəxana: {meds} tibbi dəst tapıldı.")
            else:
                self.thirst = max(0, self.thirst - 15)
                self.add_log("Xəstəxana boş idi. Susuzluq artdı.")
        elif loc_name == "Police Station":
            if roll < 0.5:
                scrap = random.randint(2, 4)
                self.inventory["Scrap Metal"] = self.inventory.get("Scrap Metal", 0) + scrap
                self.add_log(f"Polis İdarəsi: {scrap} metal qırıntısı tapıldı.")
            else:
                self.health -= 15
                self.add_log("Polis İdarəsində qarətçilərlə toqquşma! 15 zərər aldınız.")
        elif loc_name == "Industrial Zone":
            if roll < 0.55:
                wood = random.randint(2, 5)
                self.inventory["Wood"] = self.inventory.get("Wood", 0) + wood
                self.add_log(f"Sənaye Zonası: {wood} odun toplandı.")
            else:
                self.energy = max(0, self.energy - 20)
                self.add_log("Sənaye zonasında maneələr enerjinizi tükەتdi.")

    def rest_action(self):
        self.advance_time(4)
        self.energy = min(100.0, self.energy + 40.0)
        self.health = min(100.0, self.health + 10.0)
        self.add_log("Sığınacaqda dincəldiniz: Enerji və sağlamlıq bərpa olundu.")

    def craft_action(self):
        wood = self.inventory.get("Wood", 0)
        scrap = self.inventory.get("Scrap Metal", 0)
        if wood >= 3 and scrap >= 2:
            self.inventory["Wood"] -= 3
            self.inventory["Scrap Metal"] -= 2
            self.shelter_defense += 5
            self.advance_time(2)
            self.add_log("Sığınacaq müdafiəsi gücləndirildi!")
        else:
            self.add_log("Resurs çatışmır! (Lazımdır: 3 Odun, 2 Metal)")

    def consume_item(self, item_name, stat_type, amount):
        count = self.inventory.get(item_name, 0)
        if count > 0:
            self.inventory[item_name] -= 1
            if stat_type == "hunger":
                self.hunger = min(100.0, self.hunger + amount)
            elif stat_type == "thirst":
                self.thirst = min(100.0, self.thirst + amount)
            elif stat_type == "health":
                self.health = min(100.0, self.health + amount)
            self.add_log(f"{item_name} istifadə edildi. +{amount} {stat_type}.")
        else:
            self.add_log(f"Ehtiyatda {item_name} yoxdur!")

    def render(self):
        self.screen.fill(BG_COLOR)
        if self.state == "MENU":
            self.render_menu()
        elif self.state == "HOW_TO":
            self.render_how_to()
        elif self.state == "SETTINGS":
            self.render_settings()
        elif self.state == "GAME":
            self.render_game()
        elif self.state == "GAMEOVER":
            self.render_gameover()
        elif self.state == "VICTORY":
            self.render_victory()
        pygame.display.flip()

    def render_menu(self):
        title = self.font_title.render("7 DAYS TO SURVIVE", True, ACCENT_RED)
        subtitle = self.font_med.render("Post-Apokalipsi Simulyasiyası", True, TEXT_MUTED)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 180))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 230))
        
        btn_w, btn_h = 280, 50
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        
        self.btn_new_game = pygame.Rect(cx, 320, btn_w, btn_h)
        self.btn_continue = pygame.Rect(cx, 385, btn_w, btn_h)
        self.btn_how = pygame.Rect(cx, 450, btn_w, btn_h)
        self.btn_settings = pygame.Rect(cx, 515, btn_w, btn_h)
        self.btn_exit = pygame.Rect(cx, 580, btn_w, btn_h)
        
        buttons = [
            (self.btn_new_game, "YENİ OYUN", ACCENT_RED),
            (self.btn_continue, "DAVAM ET", BORDER_COLOR),
            (self.btn_how, "NECƏ OYNAMALI", BORDER_COLOR),
            (self.btn_settings, "TƏNZİMLƏMƏLƏR", BORDER_COLOR),
            (self.btn_exit, "ÇIXIŞ", BORDER_COLOR)
        ]
        
        for rect, text, col in buttons:
            pygame.draw.rect(self.screen, PANEL_COLOR, rect, border_radius=6)
            pygame.draw.rect(self.screen, col, rect, 2, border_radius=6)
            txt_surf = self.font_large.render(text, True, TEXT_WHITE)
            self.screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

    def render_how_to(self):
        title = self.font_title.render("NECƏ OYNAMALI", True, ACCENT_GREEN)
        self.screen.blit(title, (50, 50))
        instructions = [
            "1. Məqsəd: Hərbi xilasetmə gələnə qədər 7 gün sağ qalmaq.",
            "2. İdarəetmə: Sağlamlıq, Aclıq, Susuzluq və Enerjini izləyin.",
            "3. Kəşfiyyat: Supermarket, Xəstəxana, Polis və ya Sənaye zonasına gedin.",
            "4. Müdafiə: Sığınacağı odun və metal ilə qoruyun.",
            "5. İstehlak: Konserv, su və medkitlərdən istifadə edin."
        ]
        y = 130
        for line in instructions:
            txt = self.font_med.render(line, True, TEXT_WHITE)
            self.screen.blit(txt, (50, y))
            y = y + 40
            
        self.btn_back = pygame.Rect(50, 650, 200, 45)
        pygame.draw.rect(self.screen, PANEL_COLOR, self.btn_back, border_radius=6)
        pygame.draw.rect(self.screen, BORDER_COLOR, self.btn_back, 2, border_radius=6)
        txt = self.font_large.render("MENÜYƏ QAYIT", True, TEXT_WHITE)
        self.screen.blit(txt, (self.btn_back.centerx - txt.get_width()//2, self.btn_back.centery - txt.get_height()//2))

    def render_settings(self):
        title = self.font_title.render("TƏNZİMLƏMƏLƏR", True, ACCENT_YELLOW)
        self.screen.blit(title, (50, 50))
        status = f"Səs Effekti: {'AÇIQ' if self.sound_enabled else 'BAĞLI'}"
        txt = self.font_large.render(status, True, TEXT_WHITE)
        self.screen.blit(txt, (50, 150))
        
        self.btn_back = pygame.Rect(50, 650, 200, 45)
        pygame.draw.rect(self.screen, PANEL_COLOR, self.btn_back, border_radius=6)
        pygame.draw.rect(self.screen, BORDER_COLOR, self.btn_back, 2, border_radius=6)
        txt_b = self.font_large.render("MENÜYƏ QAYIT", True, TEXT_WHITE)
        self.screen.blit(txt_b, (self.btn_back.centerx - txt_b.get_width()//2, self.btn_back.centery - txt_b.get_height()//2))

    def render_game(self):
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, BORDER_COLOR, (0, 60), (SCREEN_WIDTH, 60), 2)
        
        time_str = f"GÜN {self.day}/7  //  {self.hour:02d}:{self.minute:02d}"
        t_surf = self.font_large.render(time_str, True, ACCENT_RED)
        self.screen.blit(t_surf, (30, 18))
        
        stats_str = f"HP: {int(self.health)}%  |  Aclıq: {int(self.hunger)}%  |  Susuzluq: {int(self.thirst)}%  |  Enerji: {int(self.energy)}%  |  Müdafiə: {self.shelter_defense}"
        s_surf = self.font_med.render(stats_str, True, ACCENT_GREEN)
        self.screen.blit(s_surf, (320, 20))
        
        pygame.draw.rect(self.screen, PANEL_COLOR, (20, 80, 320, 650), border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COLOR, (20, 80, 320, 650), 2, border_radius=8)
        
        lbl_act = self.font_large.render("KƏŞFİYYAT VƏ FƏALİYYƏT", True, ACCENT_YELLOW)
        self.screen.blit(lbl_act, (40, 100))
        
        btn_w, btn_h = 280, 42
        bx, by = 40, 150
        
        self.btn_supermarket = pygame.Rect(bx, by, btn_w, btn_h); by += 52
        self.btn_hospital = pygame.Rect(bx, by, btn_w, btn_h); by += 52
        self.btn_police = pygame.Rect(bx, by, btn_w, btn_h); by += 52
        self.btn_industrial = pygame.Rect(bx, by, btn_w, btn_h); by += 70
        self.btn_rest = pygame.Rect(bx, by, btn_w, btn_h); by += 52
        self.btn_craft = pygame.Rect(bx, by, btn_w, btn_h); by += 70
        self.btn_eat = pygame.Rect(bx, by, btn_w, btn_h); by += 52
        self.btn_drink = pygame.Rect(bx, by, btn_w, btn_h); by += 52
        self.btn_medkit = pygame.Rect(bx, by, btn_w, btn_h); by += 70
        self.btn_save = pygame.Rect(bx, by, btn_w, btn_h)
        
        actions = [
            (self.btn_supermarket, "🛒 Supermarket (-2s)", BORDER_COLOR),
            (self.btn_hospital, "🏥 Xəstəxana (-2s)", BORDER_COLOR),
            (self.btn_police, "🛡️ Polis İdarəsi (-2s)", BORDER_COLOR),
            (self.btn_industrial, "🏭 Sənaye Zonası (-2s)", BORDER_COLOR),
            (self.btn_rest, "💤 Dincəlmək (-4s)", ACCENT_GREEN),
            (self.btn_craft, "🔨 Sığınacağı Qoru (-2s)", ACCENT_GREEN),
            (self.btn_eat, f"🥫 Qida Yeyin ({self.inventory.get('Canned Food', 0)})", TEXT_WHITE),
            (self.btn_drink, f"💧 Su İçin ({self.inventory.get('Water Bottle', 0)})", TEXT_WHITE),
            (self.btn_medkit, f"💉 Medkit ({self.inventory.get('Medkit', 0)})", TEXT_WHITE),
            (self.btn_save, "💾 Oyunu Yadda Saxla", ACCENT_YELLOW)
        ]
        
        for rect, text, col in actions:
            pygame.draw.rect(self.screen, BG_COLOR, rect, border_radius=4)
            pygame.draw.rect(self.screen, col, rect, 1, border_radius=4)
            txt = self.font_med.render(text, True, TEXT_WHITE)
            self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

        pygame.draw.rect(self.screen, PANEL_COLOR, (360, 80, 644, 650), border_radius=8)
        pygame.draw.rect(self.screen, BORDER_COLOR, (360, 80, 644, 650), 2, border_radius=8)
        
        lbl_inv = self.font_large.render("İNVENTAR VƏ EHTİYATLAR", True, ACCENT_YELLOW)
        self.screen.blit(lbl_inv, (390, 100))
        
        inv_text = f"Odun: {self.inventory.get('Wood', 0)}  |  Metal: {self.inventory.get('Scrap Metal', 0)}  |  Qida: {self.inventory.get('Canned Food', 0)}  |  Su: {self.inventory.get('Water Bottle', 0)}  |  Med: {self.inventory.get('Medkit', 0)}"
        i_surf = self.font_med.render(inv_text, True, TEXT_WHITE)
        self.screen.blit(i_surf, (390, 135))
        
        pygame.draw.line(self.screen, BORDER_COLOR, (390, 170), (974, 170), 1)
        
        lbl_log = self.font_large.render("SİMULASİYA JURNALI", True, ACCENT_GREEN)
        self.screen.blit(lbl_log, (390, 190))
        
        ly = 230
        for log in self.logs[:16]:
            l_surf = self.font_med.render(log, True, TEXT_MUTED if "zərər" not in log and "tələsi" not in log else ACCENT_RED)
            self.screen.blit(l_surf, (390, ly))
            ly += 26

    def render_gameover(self):
        title = self.font_title.render("ÖLDÜNÜZ - SİMULASİYA UĞURSUZ OLDU", True, ACCENT_RED)
        desc = self.font_large.render(f"Gün {self.day}, Saat {self.hour:02d}-ə qədər sağ qala bildiniz.", True, TEXT_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 250))
        self.screen.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 310))
        
        self.btn_menu = pygame.Rect(SCREEN_WIDTH//2 - 150, 420, 300, 50)
        pygame.draw.rect(self.screen, PANEL_COLOR, self.btn_menu, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_RED, self.btn_menu, 2, border_radius=6)
        txt = self.font_large.render("ƏSAS MENÜYƏ QAYIT", True, TEXT_WHITE)
        self.screen.blit(txt, (self.btn_menu.centerx - txt.get_width()//2, self.btn_menu.centery - txt.get_height()//2))

    def render_victory(self):
        title = self.font_title.render("XİLASETMƏ DƏSTƏSİ GƏLDİ - SAĞ QALDINIZ!", True, ACCENT_GREEN)
        desc = self.font_large.render("7 günü uğurla başa vurdunuz və xilas olundunuz.", True, TEXT_WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 250))
        self.screen.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 310))
        
        self.btn_menu = pygame.Rect(SCREEN_WIDTH//2 - 150, 420, 300, 50)
        pygame.draw.rect(self.screen, PANEL_COLOR, self.btn_menu, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_GREEN, self.btn_menu, 2, border_radius=6)
        txt = self.font_large.render("ƏSAS MENÜYƏ QAYIT", True, TEXT_WHITE)
        self.screen.blit(txt, (self.btn_menu.centerx - txt.get_width()//2, self.btn_menu.centery - txt.get_height()//2))

if __name__ == "__main__":
    game = Game()
    game.run()
