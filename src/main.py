import pygame
from openai import OpenAI
import os
import time
import re

def raw_string_to_markdown_string(text):
    y_offset = 50
    x_offset = 50
    max_width = screen.get_width() - 100
    line_height = 40
    if text is None:
        return None
    lines = text.split('\n')
    for line in lines:
        if not line.strip():
            y_offset += line_height // 2
            continue
        if line.startswith('### '):
            content = line[4:].strip()
            font_to_use = bold_font
            size_factor = 1.8
        elif line.startswith('## '):
            content = line[3:].strip()
            font_to_use = bold_font
            size_factor = 1.6
        elif line.startswith('# '):
            content = line[2:].strip()
            font_to_use = bold_font
            size_factor = 1.4
        elif line.startswith('- '):
            content = '• ' + line[2:].strip()
            font_to_use = font
            size_factor = 1.0
        else:
            content = line.strip()
            font_to_use = font
            size_factor = 1.0
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
        content = re.sub(r'`(.*?)`', r'\1', content)  # Code
        if content:
            return content

def blit_string(text):
    if text is not None:
        markdown_string = text
        cx, cy = screen.get_rect().center
        mid = len(markdown_string) // 2
        glyph_w = font.size('M')[0]
        spacing = glyph_w + 6
        lshift = mid * spacing
        x = cx - lshift
        for ch_i, ch in enumerate(markdown_string):
            color = (200, 200, 200)
            if ch_i == mid:
                color = (255, 100, 100)
            surf = font.render(ch, True, color)
            w, h = surf.get_size()
            pos = (x - (w/2), cy - h/2)
            screen.blit(surf, pos)
            x += spacing

def draw_slider():
    slider_y = 20
    slider_x = 50
    slider_width = 200
    slider_height = 8
    pygame.draw.line(screen, (80, 80, 80), (slider_x, slider_y + slider_height // 2), (slider_x + slider_width, slider_y + slider_height // 2), slider_height)
    min_wpm, max_wpm_range = 100, 1200
    progress = (current_wpm - min_wpm) / (max_wpm_range - min_wpm)
    filled_width = slider_width * progress
    pygame.draw.line(screen, (255, 100, 100), (slider_x, slider_y + slider_height // 2), (slider_x + filled_width, slider_y + slider_height // 2), slider_height)
    thumb_pos = slider_x + filled_width
    pygame.draw.circle(screen, (255, 100, 100), (int(thumb_pos), slider_y + slider_height // 2), 8)
    pygame.draw.circle(screen, (255, 150, 150), (int(thumb_pos), slider_y + slider_height // 2), 6)
    small_font = pygame.font.Font(None, 20)
    wpm_label = small_font.render(f"WPM: {current_wpm}", True, (255, 255, 255))
    wpm_label_w, wpm_label_h = wpm_label.get_size()
    label_bg_rect = wpm_label.get_rect(topleft=(slider_x + slider_width + wpm_label_w / 2, slider_y))
    label_bg_rect.inflate_ip(15, 15)
    pygame.draw.rect(screen, (50, 50, 50), label_bg_rect, border_radius=4)
    pygame.draw.rect(screen, (100, 100, 100), label_bg_rect, 1, border_radius=4)
    screen.blit(wpm_label, (slider_x + slider_width + 35, slider_y))

    return slider_x, slider_y, slider_width, slider_height

def handle_slider_click(mouse_x, slider_x, slider_width):
    global current_wpm
    min_wpm, max_wpm_range = 100, 1200
    relative_x = max(0, min(mouse_x - slider_x, slider_width))
    new_wpm = min_wpm + (relative_x / slider_width) * (max_wpm_range - min_wpm)
    current_wpm = int(new_wpm)

def draw_text_box(text_input):
    box_y = screen.get_height() - 60
    box_x = 50
    box_width = screen.get_width() - 100
    box_height = 40
    pygame.draw.rect(screen, (40, 40, 40), (box_x, box_y, box_width, box_height), border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), (box_x, box_y, box_width, box_height), 2, border_radius=6)
    small_font = pygame.font.Font(None, 22)
    text_label = small_font.render(f"Prompt: {text_input}", True, (200, 200, 200))
    screen.blit(text_label, (box_x + 15, box_y + 10))
    if text_box_active:
        cursor_x = box_x + 15 + text_label.get_width() + 3
        pygame.draw.line(screen, (255, 100, 100), (cursor_x, box_y + 8), (cursor_x, box_y + 32), 2)
    return box_x, box_y, box_width, box_height

def draw_full_current_response():
    global full_current_response
    global full_box_rect
    global full_response_lines
    global full_max_lines
    global full_box_minimized
    global full_scroll
    box_width = int(screen.get_width() / 5)
    box_height = int(screen.get_height() / 2)
    box_y = int(screen.get_height() / 2 - box_height / 2)
    box_x = 50
    small_font = pygame.font.Font(None, 18)
    padding = 10
    text_starty = box_y + padding + 20
    line_height = small_font.get_linesize()
    text = (full_current_response or "").strip()

    if full_box_minimized:
        # draw a small header with minimize/expand button
        header_rect = pygame.Rect(box_x, box_y, box_width, 28)
        pygame.draw.rect(screen, (20, 20, 20), header_rect, border_radius=4)
        title = small_font.render("Full Response (minimized)", True, (180, 180, 180))
        screen.blit(title, (box_x + padding, box_y + 6))
        # draw expand button
        btn_rect = pygame.Rect(box_x + box_width - 34, box_y + 4, 24, 20)
        pygame.draw.rect(screen, (60, 60, 60), btn_rect, border_radius=4)
        pygame.draw.rect(screen, (100, 100, 100), btn_rect, 1, border_radius=4)
        plus = small_font.render("+", True, (200, 200, 200))
        screen.blit(plus, (btn_rect.x + 6, btn_rect.y + 1))
        return box_x, box_y, box_width, box_height

    pygame.draw.rect(screen, (10, 10, 10), (box_x, box_y, box_width, box_height), border_radius=6)
    pygame.draw.rect(screen, (30, 30, 30), (box_x, box_y, box_width, box_height), 2, border_radius=6)
    btn_rect = pygame.Rect(box_x + box_width - 34, box_y + 4, 24, 20)
    title = small_font.render("Full Response", True, (180, 180, 180))
    screen.blit(title, (box_x + padding, box_y + 6))
    pygame.draw.rect(screen, (60, 60, 60), btn_rect, border_radius=4)
    pygame.draw.rect(screen, (100, 100, 100), btn_rect, 1, border_radius=4)
    plus = small_font.render("-", True, (200, 200, 200))
    screen.blit(plus, (btn_rect.x + 6, btn_rect.y + 1))

    # store geometry for event handling
    full_box_rect = (box_x, box_y, box_width, box_height)
    if not text:
        placeholder = small_font.render("(no response yet)", True, (50, 50, 50))
        screen.blit(placeholder, (box_x + padding, text_starty))
        full_response_lines = []
        full_max_lines = max(1, (box_height - (padding * 2 + 20)) // line_height)
        return box_x, box_y, box_width, box_height

    words = text.split()
    lines = []
    current = ""
    max_inner_width = box_width - padding * 2
    for w in words:
        test = w if not current else current + " " + w
        if small_font.size(test)[0] <= max_inner_width:
            current = test
        else:
            if current:
                lines.append(current)
            if small_font.size(w)[0] > max_inner_width:
                part = ""
                for ch in w:
                    if small_font.size(part + ch)[0] <= max_inner_width:
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
    full_response_lines = lines
    full_max_lines = max_lines

    visible_lines = lines[full_scroll:full_scroll + max_lines]
    y = text_starty
    for ln in visible_lines:
        surf = small_font.render(ln, True, (60, 60, 60))
        screen.blit(surf, (box_x + padding, y))
        y += line_height

    total_lines = len(lines)
    if total_lines > max_lines:
        track_x = box_x + box_width - 14
        track_y = text_starty
        track_h = box_height - (padding * 2 + 20)
        track_w = 6
        pygame.draw.rect(screen, (30, 30, 30), (track_x, track_y, track_w, track_h), border_radius=4)
        thumb_h = max(20, int(track_h * (max_lines / total_lines)))
        thumb_w = track_w + 2
        max_scroll = total_lines - max_lines
        thumb_y = track_y + int((track_h - thumb_h) * (full_scroll / max_scroll)) if max_scroll > 0 else track_y
        thumb_rect = pygame.Rect(track_x - (thumb_w - track_w) / 2, thumb_y, thumb_w, thumb_h)
        pygame.draw.rect(screen, (80, 80, 80), thumb_rect, border_radius=4)
    return box_x, box_y, box_width, box_height

def draw_vertical_indicator():
    cx, cy = screen.get_rect().center
    pygame.draw.line(screen, (100, 100, 100), (cx, 50), (cx, screen.get_height() / 2 - 50), 3)
    pygame.draw.line(screen, (100, 100, 100), (cx, screen.get_height() / 2 + 50), (cx, screen.get_height() - 100), 3)

def create_new_response(prompt):
    new_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    return new_response

def run_fastread(response):
    global running
    global current_wpm
    global text_input
    global slider_dragging
    global text_surface
    global text_box_active
    global full_current_response
    global full_box_minimized
    global full_scroll
    global full_response_lines
    global full_max_lines
    global full_box_rect
    full_current_response = ""
    last_string = None
    for chunk in response:
        for inner_event in pygame.event.get():
            if inner_event.type == pygame.QUIT:
                running = False
                break
            if inner_event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = False
            if inner_event.type == pygame.MOUSEMOTION and slider_dragging:
                slider_x, slider_y, slider_width, _ = draw_slider()
                handle_slider_click(inner_event.pos[0], slider_x, slider_width)
            if inner_event.type == pygame.MOUSEWHEEL:
                max_scroll = max(0, len(full_response_lines) - full_max_lines)
                full_scroll = max(0, min(full_scroll - inner_event.y, max_scroll))
            if inner_event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = inner_event.pos
                bx, by, bw, bh = full_box_rect
                padding = 12
                min_rect = pygame.Rect(bx + bw - 34, by + 4, 24, 20)
                if min_rect.collidepoint(mx, my):
                    full_box_minimized = not full_box_minimized
                slider_y = 20
                slider_x = 50
                slider_width = 200
                slider_height = 8
                slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height + 5)
                if slider_rect.collidepoint(mx, my):
                    slider_dragging = True
                    track_x = bx + bw - 14
                    track_y = by + padding
                    track_h = bh - padding * 2
                    if track_x <= mx <= track_x + 8 and track_y <= my <= track_y + track_h:
                        max_scroll = max(0, len(full_response_lines) - full_max_lines)
                        if max_scroll > 0:
                            rel = (my - track_y) / track_h
                            full_scroll = int(rel * max_scroll)
            if inner_event.type == pygame.KEYDOWN:
                if inner_event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                elif inner_event.unicode.isprintable():
                    text_input += inner_event.unicode
        if not running:
            break

        pause_time = (1 / (current_wpm)) * (seconds_per_minute)
        time.sleep(pause_time)
        screen.fill((0, 0, 0))

        content = chunk.choices[0].delta.content
        full_current_response += "" if content is None else content
        markdown_string = raw_string_to_markdown_string(content)
        short_pause_sep = [","]
        long_pause_sep = [".", "!", "?"]
        junk_sep = ["\"", "\'", "-", " ", "\t", "\n", "", "—", ":", "###", "(", ")", "[", "]", "{", "}"]
        if markdown_string in short_pause_sep:
            time.sleep(1 * pause_time)
            blit_string(last_string)
        elif markdown_string in long_pause_sep:
            time.sleep(3 * pause_time)
            blit_string(last_string)
        elif markdown_string in junk_sep:
            blit_string(last_string)
        elif markdown_string is None:
            blit_string(last_string)
        elif markdown_string is not None:
            last_string = markdown_string
            blit_string(markdown_string)
        draw_slider()
        draw_text_box(text_input)
        draw_full_current_response()
        draw_vertical_indicator()
        pygame.display.flip()

# export OPENAI_API_KEY=
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
max_wpm = 900
seconds_per_minute = 60
current_wpm = max_wpm
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption("fastread")
font = pygame.font.SysFont('Courier', 70)
bold_font = pygame.font.SysFont('Courier', 70, bold=True)
italic_font = pygame.font.SysFont('Courier', 70, italic=True)

text_surface = None
running = True
slider_dragging = False
text_input = ""
text_box_active = False
full_current_response = ""
full_box_minimized = False
full_scroll = 0
full_response_lines = []
full_max_lines = 0
full_box_rect = (0, 0, 0, 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
        if event.type == pygame.MOUSEMOTION and slider_dragging:
            slider_x, slider_y, slider_width, _ = draw_slider()
            handle_slider_click(event.pos[0], slider_x, slider_width)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and text_input:
                new_prompt = text_input
                text_input = ""
                last_string = None
                response = create_new_response(new_prompt)
                run_fastread(response)
            elif event.key == pygame.K_BACKSPACE:
                text_input = text_input[:-1]
            elif event.unicode.isprintable():
                text_input += event.unicode
        if event.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(full_response_lines) - full_max_lines)
            full_scroll = max(0, min(full_scroll - event.y, max_scroll))
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            bx, by, bw, bh = full_box_rect
            padding = 12
            min_rect = pygame.Rect(bx + bw - 34, by + 4, 24, 20)
            if min_rect.collidepoint(mx, my):
                full_box_minimized = not full_box_minimized
            slider_y = 20
            slider_x = 50
            slider_width = 200
            slider_height = 8
            slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height + 10)
            if slider_rect.collidepoint(mx, my):
                slider_dragging = True
                track_x = bx + bw - 14
                track_y = by + padding
                track_h = bh - padding * 2
                if track_x <= mx <= track_x + 8 and track_y <= my <= track_y + track_h:
                    max_scroll = max(0, len(full_response_lines) - full_max_lines)
                    if max_scroll > 0:
                        rel = (my - track_y) / track_h
                        full_scroll = int(rel * max_scroll)
    screen.fill((0, 0, 0))
    draw_slider()
    draw_text_box(text_input)
    draw_full_current_response()
    draw_vertical_indicator()
    pygame.display.flip()
    time.sleep(0.016)

pygame.quit()
