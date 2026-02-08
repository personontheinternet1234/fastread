import pygame
from openai import OpenAI
import time
import re
import os

# Constants
COLOR_BLACK = (0, 0, 0)
COLOR_DARK_GRAY = (10, 10, 10)
COLOR_DARK_GRAY_2 = (20, 20, 20)
COLOR_DARKER_GRAY = (30, 30, 30)
COLOR_GRAY = (40, 40, 40)
COLOR_GRAY_2 = (50, 50, 50)
COLOR_GRAY_3 = (60, 60, 60)
COLOR_MEDIUM_GRAY = (80, 80, 80)
COLOR_LIGHT_GRAY = (100, 100, 100)
COLOR_LIGHTER_GRAY = (180, 180, 180)
COLOR_WHITE = (200, 200, 200)
COLOR_WHITE_2 = (255, 255, 255)
COLOR_ACCENT = (255, 100, 100)
COLOR_ACCENT_LIGHT = (255, 150, 150)

FONT_SIZE_LARGE = 70
FONT_SIZE_SMALL = 22
FONT_SIZE_TINY = 18
FONT_SIZE_LABEL = 20

MIN_WPM = 100
MAX_WPM = 1200
DEFAULT_WPM = 900
SECONDS_PER_MINUTE = 60

SLIDER_X = 50
SLIDER_Y = 20
SLIDER_WIDTH = 200
SLIDER_HEIGHT = 8

BOX_PADDING = 12
FULL_BOX_WIDTH_RATIO = 5
FULL_BOX_HEIGHT_RATIO = 2
TEXT_BOX_OFFSET_FROM_BOTTOM = 60
TEXT_BOX_HEIGHT = 40

LINE_HEIGHT = 40
FRAME_TIME = 0.016  # ~60 FPS

class FastReadApp:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.font = pygame.font.SysFont('Courier', FONT_SIZE_LARGE)
        self.bold_font = pygame.font.SysFont('Courier', FONT_SIZE_LARGE, bold=True)
        self.italic_font = pygame.font.SysFont('Courier', FONT_SIZE_LARGE, italic=True)
        self.small_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.tiny_font = pygame.font.Font(None, FONT_SIZE_TINY)
        self.label_font = pygame.font.Font(None, FONT_SIZE_LABEL)

        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("fastread")

        self.running = True
        self.current_wpm = DEFAULT_WPM
        self.text_input = ""
        self.slider_dragging = False
        self.full_current_response = ""
        self.full_box_minimized = False
        self.full_scroll = 0
        self.full_response_lines = []
        self.full_max_lines = 0
        self.full_box_rect = (0, 0, 0, 0)
        self.last_string = None

    def draw_vertical_indicator(self):
        cx, cy = self.screen.get_rect().center
        pygame.draw.line(self.screen, COLOR_LIGHT_GRAY, (cx, 50), (cx, self.screen.get_height() / 2 - 50), 3)
        pygame.draw.line(self.screen, COLOR_LIGHT_GRAY, (cx, self.screen.get_height() / 2 + 50), (cx, self.screen.get_height() - 100), 3)

    def handle_event(self, event, in_fastread=False):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.MOUSEBUTTONUP:
            self.slider_dragging = False

        if event.type == pygame.MOUSEMOTION and self.slider_dragging:
            self.handle_slider_click(event.pos[0])

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.text_input and not in_fastread:
                # Submit prompt for processing
                return ("submit_prompt", self.text_input)
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            elif event.unicode.isprintable():
                self.text_input += event.unicode

        if event.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(self.full_response_lines) - self.full_max_lines)
            self.full_scroll = max(0, min(self.full_scroll - event.y, max_scroll))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            bx, by, bw, bh = self.full_box_rect
            padding = BOX_PADDING
            min_rect = pygame.Rect(bx + bw - 34, by + 4, 24, 20)
            if min_rect.collidepoint(mx, my):
                self.full_box_minimized = not self.full_box_minimized

            slider_rect = pygame.Rect(SLIDER_X, SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT + 10)
            if slider_rect.collidepoint(mx, my):
                self.slider_dragging = True
                track_x = bx + bw - 14
                track_y = by + padding
                track_h = bh - padding * 2
                if track_x <= mx <= track_x + 8 and track_y <= my <= track_y + track_h:
                    max_scroll = max(0, len(self.full_response_lines) - self.full_max_lines)
                    if max_scroll > 0:
                        rel = (my - track_y) / track_h
                        self.full_scroll = int(rel * max_scroll)
        return None

    def create_new_response(self, prompt):
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

    def run_fastread(self, response):
        self.full_current_response = ""
        self.last_string = None

        for chunk in response:
            for inner_event in pygame.event.get():
                self.handle_event(inner_event, in_fastread=True)

            if not self.running:
                break

            pause_time = (1 / self.current_wpm) * SECONDS_PER_MINUTE
            time.sleep(pause_time)
            self.screen.fill(COLOR_BLACK)

            content = chunk.choices[0].delta.content
            self.full_current_response += "" if content is None else content
            markdown_string = self.raw_string_to_markdown_string(content)

            short_pause_sep = [","]
            long_pause_sep = [".", "!", "?"]
            junk_sep = ["\"", "\'", "-", " ", "\t", "\n", "", "—", ":", "###", "(", ")", "[", "]", "{", "}"]

            if markdown_string in short_pause_sep:
                time.sleep(1 * pause_time)
                self.blit_center_text(self.last_string)
            elif markdown_string in long_pause_sep:
                time.sleep(3 * pause_time)
                self.blit_center_text(self.last_string)
            elif markdown_string in junk_sep:
                self.blit_center_text(self.last_string)
            elif markdown_string is None:
                self.blit_center_text(self.last_string)
            elif markdown_string is not None:
                self.last_string = markdown_string
                self.blit_center_text(markdown_string)

            self.draw_slider()
            self.draw_text_box()
            self.draw_full_current_response()
            self.draw_vertical_indicator()
            pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                result = self.handle_event(event)
                if result and result[0] == "submit_prompt":
                    prompt = result[1]
                    self.text_input = ""
                    response = self.create_new_response(prompt)
                    self.run_fastread(response)

            self.draw_frame()
            time.sleep(FRAME_TIME)

    def draw_frame(self):
        self.screen.fill(COLOR_BLACK)
        self.draw_slider()
        self.draw_text_box()
        self.draw_full_current_response()
        self.draw_vertical_indicator()
        pygame.display.flip()

    def draw_text_box(self):
        box_y = self.screen.get_height() - TEXT_BOX_OFFSET_FROM_BOTTOM
        box_x = BOX_PADDING
        box_width = self.screen.get_width() - 2 * BOX_PADDING
        box_height = TEXT_BOX_HEIGHT
        pygame.draw.rect(self.screen, COLOR_GRAY, (box_x, box_y, box_width, box_height), border_radius=6)
        pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, (box_x, box_y, box_width, box_height), 2, border_radius=6)
        text_label = self.small_font.render(f"Prompt: {self.text_input}", True, COLOR_WHITE)
        self.screen.blit(text_label, (box_x + 15, box_y + 10))

        return box_x, box_y, box_width, box_height

    def draw_slider(self):
        pygame.draw.line(self.screen, COLOR_MEDIUM_GRAY, (SLIDER_X, SLIDER_Y + SLIDER_HEIGHT // 2), (SLIDER_X + SLIDER_WIDTH, SLIDER_Y + SLIDER_HEIGHT // 2), SLIDER_HEIGHT)

        progress = (self.current_wpm - MIN_WPM) / (MAX_WPM - MIN_WPM)
        filled_width = SLIDER_WIDTH * progress
        pygame.draw.line(self.screen, COLOR_ACCENT, (SLIDER_X, SLIDER_Y + SLIDER_HEIGHT // 2), (SLIDER_X + filled_width, SLIDER_Y + SLIDER_HEIGHT // 2), SLIDER_HEIGHT)
        thumb_pos = SLIDER_X + filled_width
        pygame.draw.circle(self.screen, COLOR_ACCENT, (int(thumb_pos), SLIDER_Y + SLIDER_HEIGHT // 2), 8)
        pygame.draw.circle(self.screen, COLOR_ACCENT_LIGHT, (int(thumb_pos), SLIDER_Y + SLIDER_HEIGHT // 2), 6)

        wpm_label = self.label_font.render(f"WPM: {self.current_wpm}", True, COLOR_WHITE_2)
        wpm_label_w, wpm_label_h = wpm_label.get_size()
        label_bg_rect = wpm_label.get_rect(topleft=(SLIDER_X + SLIDER_WIDTH + wpm_label_w / 2, SLIDER_Y))
        label_bg_rect.inflate_ip(15, 15)
        pygame.draw.rect(self.screen, COLOR_GRAY_2, label_bg_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, label_bg_rect, 1, border_radius=4)
        self.screen.blit(wpm_label, (SLIDER_X + SLIDER_WIDTH + 35, SLIDER_Y))

        return SLIDER_X, SLIDER_Y, SLIDER_WIDTH, SLIDER_HEIGHT

    def handle_slider_click(self, mouse_x):
        relative_x = max(0, min(mouse_x - SLIDER_X, SLIDER_WIDTH))
        new_wpm = MIN_WPM + (relative_x / SLIDER_WIDTH) * (MAX_WPM - MIN_WPM)
        self.current_wpm = int(new_wpm)

    def draw_full_current_response(self):
        box_width = int(self.screen.get_width() / FULL_BOX_WIDTH_RATIO)
        box_height = int(self.screen.get_height() / FULL_BOX_HEIGHT_RATIO)
        box_y = int(self.screen.get_height() / 2 - box_height / 2)
        box_x = BOX_PADDING
        padding = BOX_PADDING
        text_starty = box_y + padding + 20
        line_height = self.tiny_font.get_linesize()
        text = (self.full_current_response or "").strip()

        if self.full_box_minimized:
            header_rect = pygame.Rect(box_x, box_y, box_width, 28)

            pygame.draw.rect(self.screen, COLOR_DARK_GRAY_2, header_rect, border_radius=4)
            title = self.tiny_font.render("Full Response (minimized)", True, COLOR_LIGHTER_GRAY)
            self.screen.blit(title, (box_x + padding, box_y + 6))

            btn_rect = pygame.Rect(box_x + box_width - 34, box_y + 4, 24, 20)
            pygame.draw.rect(self.screen, COLOR_GRAY_3, btn_rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, btn_rect, 1, border_radius=4)
            plus = self.tiny_font.render("+", True, COLOR_WHITE)
            self.screen.blit(plus, (btn_rect.x + 6, btn_rect.y + 1))
            self.full_box_rect = (box_x, box_y, box_width, box_height)

            return box_x, box_y, box_width, box_height

        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (box_x, box_y, box_width, box_height), border_radius=6)
        pygame.draw.rect(self.screen, COLOR_DARKER_GRAY, (box_x, box_y, box_width, box_height), 2, border_radius=6)
        title = self.tiny_font.render("Full Response", True, COLOR_LIGHTER_GRAY)
        self.screen.blit(title, (box_x + padding, box_y + 6))

        btn_rect = pygame.Rect(box_x + box_width - 34, box_y + 4, 24, 20)
        pygame.draw.rect(self.screen, COLOR_GRAY_3, btn_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, btn_rect, 1, border_radius=4)
        minus = self.tiny_font.render("-", True, COLOR_WHITE)
        self.screen.blit(minus, (btn_rect.x + 6, btn_rect.y + 1))

        self.full_box_rect = (box_x, box_y, box_width, box_height)
        if not text:
            placeholder = self.tiny_font.render("(no response yet)", True, COLOR_GRAY_2)
            self.screen.blit(placeholder, (box_x + padding, text_starty))
            self.full_response_lines = []
            self.full_max_lines = max(1, (box_height - (padding * 2 + 20)) // line_height)
            return box_x, box_y, box_width, box_height

        words = text.split()
        lines = []
        current = ""
        max_inner_width = box_width - padding * 2
        for w in words:
            test = w if not current else current + " " + w
            if self.tiny_font.size(test)[0] <= max_inner_width:
                current = test
            else:
                if current:
                    lines.append(current)
                if self.tiny_font.size(w)[0] > max_inner_width:
                    part = ""
                    for ch in w:
                        if self.tiny_font.size(part + ch)[0] <= max_inner_width:
                            part += ch
                        else:
                            lines.append(part)
                            part = ch
                    if part:
                        current = part
                    else:
                        current = ""
                else:
                    current = w
        if current:
            lines.append(current)

        max_lines = max(1, (box_height - (padding * 2 + 20)) // line_height)
        self.full_response_lines = lines
        self.full_max_lines = max_lines

        visible_lines = lines[self.full_scroll:self.full_scroll + max_lines]
        y = text_starty
        for ln in visible_lines:
            surf = self.tiny_font.render(ln, True, COLOR_GRAY_3)
            self.screen.blit(surf, (box_x + padding, y))
            y += line_height

        total_lines = len(lines)
        if total_lines > max_lines:
            track_x = box_x + box_width - 14
            track_y = text_starty
            track_h = box_height - (padding * 2 + 20)
            track_w = 6
            pygame.draw.rect(self.screen, COLOR_DARKER_GRAY, (track_x, track_y, track_w, track_h), border_radius=4)

            thumb_h = max(20, int(track_h * (max_lines / total_lines)))
            thumb_w = track_w + 2
            max_scroll = total_lines - max_lines
            thumb_y = track_y + int((track_h - thumb_h) * (self.full_scroll / max_scroll)) if max_scroll > 0 else track_y
            thumb_rect = pygame.Rect(track_x - (thumb_w - track_w) / 2, thumb_y, thumb_w, thumb_h)
            pygame.draw.rect(self.screen, COLOR_MEDIUM_GRAY, thumb_rect, border_radius=4)

        return box_x, box_y, box_width, box_height

    def blit_center_text(self, text):
        if text is not None:
            cx, cy = self.screen.get_rect().center
            mid = len(text) // 2
            glyph_w = self.font.size('M')[0]
            spacing = glyph_w + 6
            lshift = mid * spacing
            x = cx - lshift
            for ch_i, ch in enumerate(text):
                color = COLOR_WHITE if ch_i != mid else COLOR_ACCENT
                surf = self.font.render(ch, True, color)
                w, h = surf.get_size()
                pos = (x - (w/2), cy - h/2)
                self.screen.blit(surf, pos)
                x += spacing

    def raw_string_to_markdown_string(self, text):
        if text is None:
            return None
        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                continue
            if line.startswith('### '):
                content = line[4:].strip()
            elif line.startswith('## '):
                content = line[3:].strip()
            elif line.startswith('# '):
                content = line[2:].strip()
            elif line.startswith('- '):
                content = '• ' + line[2:].strip()
            else:
                content = line.strip()
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
            content = re.sub(r'\*(.*?)\*', r'\1', content)
            content = re.sub(r'`(.*?)`', r'\1', content)
            if content:
                return content
