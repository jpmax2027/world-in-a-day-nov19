#!/usr/bin/env python3
"""THE WORLD IN A DAY -- Thursday 19 November 2026.

Draws a newspaper front page summing up the day's world news, from code
only: a small rasterizer, an embedded 5x7 bitmap font, and a zlib PNG
encoder. Python 3 standard library only; no network, no image files.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default /output), 1024x1024 PNG,
deterministic (two runs produce byte-identical files).
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (158, 28, 28)
BLUE = (28, 58, 120)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)

# ---------------------------------------------------------------- font -----
# 5x7 bitmap glyphs, one row per string, '#' = ink.
GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    per_char = 6 * scale
    max_chars = max(1, (max_w + scale) // per_char)
    words = text.split(' ')
    lines, cur = [], ''
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += ' ' + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- rasterizer --
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            row = bytes(color) * (x1 - x0)
            self.px[base:base + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = GLYPHS.get(ch, GLYPHS[' '])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = text_width(s, scale)
        return self.text((x0 + x1 - w) // 2, y, s, scale, color)

    def para(self, x, y, text, scale, color, max_w, leading=None):
        if leading is None:
            leading = 7 * scale + 4
        for line in wrap(text, scale, max_w):
            self.text(x, y, line, scale, color)
            y += leading
        return y


# ------------------------------------------------------------------ scene --
def draw_flags(cv, x, y):
    """Three small abstract flags on poles: US, China, Russia."""
    # poles
    for i in range(3):
        cv.vline(x + 14 + i * 62, y - 6, 74, INK, 2)
    # US flag: stripes + blue canton
    fx = x
    for i in range(7):
        cv.rect(fx, y + i * 6, 52, 6, (178, 34, 52) if i % 2 == 0 else PAPER)
    cv.rect(fx, y, 24, 24, BLUE)
    for sx in (6, 15):
        for sy in (6, 15):
            cv.rect(fx + sx, y + sy, 3, 3, PAPER)
    # China flag: red field, one big + four small yellow stars (squares)
    fx = x + 62
    cv.rect(fx, y, 52, 42, RED)
    cv.rect(fx + 6, y + 6, 10, 10, (255, 222, 0))
    for sx, sy in ((28, 6), (36, 12), (36, 22), (28, 26)):
        cv.rect(fx + sx, y + sy, 5, 5, (255, 222, 0))
    # Russia flag: white / blue / red horizontal tricolour, thin dark border
    fx = x + 124
    cv.rect(fx, y, 52, 42, INK)
    cv.rect(fx + 1, y + 1, 50, 12, PAPER)
    cv.rect(fx + 1, y + 15, 50, 12, BLUE)
    cv.rect(fx + 1, y + 29, 50, 12, RED)


def draw_summit_scene(cv, x, y, w, h):
    """Abstract summit scene: sky, three flags, three figures at a table."""
    cv.rect(x, y, w, h, (214, 228, 240))            # sky
    cv.rect(x, y + h - 48, w, 48, (120, 96, 66))    # floor
    cv.rect(x, y + h - 82, w, 6, (90, 70, 44))      # horizon band
    # sun / emblem disc
    cv.disc(x + w // 2, y + 26, 16, (232, 190, 60))
    # flags
    draw_flags(cv, x + (w - 176) // 2, y + 52)
    # three figures seated behind a table
    suits = ((28, 58, 120), (158, 28, 28), (52, 52, 52))
    step = (w - 130) // 2
    for i, suit in enumerate(suits):
        fx = x + 44 + i * step
        cv.disc(fx + 22, y + 100, 15, (226, 196, 164))   # head
        cv.rect(fx, y + 117, 44, 30, suit)               # shoulders
        cv.rect(fx + 19, y + 117, 6, 22, PAPER)          # shirt
        cv.rect(fx + 17, y + 121, 10, 8, RED if i != 1 else BLUE)  # tie
    # table
    cv.rect(x + 20, y + 146, w - 40, 11, (96, 66, 38))
    cv.rect(x + 30, y + 157, 9, h - 157, (96, 66, 38))
    cv.rect(x + w - 39, y + 157, 9, h - 157, (96, 66, 38))
    # papers on the table
    for i in range(3):
        cv.rect(x + 52 + i * step, y + 139, 32, 7, PAPER)
    cv.rect(x, y, w, 3, INK)
    cv.rect(x, y + h - 3, w, 3, INK)
    cv.rect(x, y, 3, h, INK)
    cv.rect(x + w - 3, y, 3, h, INK)


# ------------------------------------------------------------------- png ---
def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------ page ---
def build():
    cv = Canvas(W, H, PAPER)
    M = 24                      # margin
    CW = W - 2 * M              # content width = 976
    y = 16

    # --- masthead ---
    cv.hline(M, y, CW, INK, 4)
    y += 12
    cv.text_center(y, "THE WORLD IN A DAY", 6, INK, M, M + CW)
    y += 6 * 7 + 8
    cv.text_center(y, "ONE DAY'S WORLD NEWS, IN ONE PICTURE.", 2, GREY, M, M + CW)
    y += 7 * 2 + 12

    # --- date band (must be unmissable) ---
    cv.rect(M, y, CW, 58, INK)
    cv.text_center(y + 13, "THURSDAY 19 NOVEMBER 2026", 4, PAPER, M, M + CW)
    y += 58 + 12
    cv.hline(M, y, CW, INK, 4)
    y += 14

    # --- lead story ---
    lead_x, lead_w = M, 600
    scene_x, scene_w = M + 620, CW - 620
    cv.text(lead_x, y, "SHENZHEN  |  APEC SUMMIT", 2, RED)
    y += 7 * 2 + 6
    head_y = y
    y = cv.para(lead_x, y, "THREE LEADERS, ONE TABLE", 4, INK, lead_w,
                leading=7 * 4 + 4)
    y += 4
    y = cv.para(lead_x, y,
                "TRUMP, XI AND PUTIN MEET IN SHENZHEN - FIRST THREE-WAY SUMMIT",
                2, INK, lead_w, leading=7 * 2 + 2)
    y += 5
    y = cv.para(lead_x, y,
                "DONALD TRUMP, XI JINPING AND VLADIMIR PUTIN HELD A 90-MINUTE "
                "THREE-WAY MEETING IN SHENZHEN ON THE SIDELINES OF THE APEC "
                "SUMMIT - THEIR FIRST THREE-WAY SUMMIT.",
                2, INK, lead_w, leading=7 * 2 + 1)
    y += 3
    y = cv.para(lead_x, y,
                "AFTERWARDS THEY ISSUED A JOINT \"PEACE DECLARATION\": DIALOGUE "
                "ON REDUCING NUCLEAR RISKS, UN REFORM, AND MORE REFINED "
                "PETROLEUM SUPPLIES FOR ALL COUNTRIES. IT NAMES NEITHER "
                "UKRAINE NOR IRAN.",
                2, INK, lead_w, leading=7 * 2 + 1)
    y += 3
    y = cv.para(lead_x, y,
                "TRUMP LEFT CHINA AFTER THE MEETING; PUTIN DID NOT COMMIT TO "
                "ATTENDING NEXT MONTH'S G20 IN MIAMI. THE TALKS CAME AS THE "
                "NEW START TREATY NEARS EXPIRY.",
                2, INK, lead_w, leading=7 * 2 + 1)
    lead_bottom = y
    scene_h = 180
    draw_summit_scene(cv, scene_x, head_y - 6, scene_w, scene_h)
    cv.text(scene_x, head_y + scene_h, "THE THREE LEADERS AT THE TABLE IN SHENZHEN.",
            1, GREY, )
    y = max(lead_bottom, head_y + scene_h + 7 + 8) + 6
    cv.hline(M, y, CW, INK, 3)
    y += 12

    # --- four panels, 2x2 ---
    panels = [
        ("IRAN WAR", "TRUMP: \"SEE WHAT HAPPENS\" AFTER JAN. 1",
         "TRUMP SAID THE US WOULD \"SEE WHAT HAPPENS\" IN THE IRAN WAR AFTER "
         "JAN. 1, 2027. HE IS WEIGHING A STRIKE AFTER A REPORT OF A POSSIBLE "
         "DIRTY BOMB; A HOUTHI MISSILE DAMAGED THE PIF TOWER IN RIYADH."),
        ("WORLD COURT", "MYANMAR GUILTY OF GENOCIDE, TOP COURT RULES",
         "THE UN'S TOP COURT RULED MYANMAR COMMITTED STATE-SPONSORED "
         "GENOCIDE AGAINST THE ROHINGYA IN NORTHERN RAKHINE STATE - THE "
         "FIRST RULING OF ITS KIND."),
        ("UKRAINE", "CRIMEA BRIDGE HIT A THIRD TIME",
         "RUSSIA SAID UKRAINE ATTACKED THE CRIMEAN BRIDGE FOR THE THIRD TIME "
         "THIS WEEK. RAIL TRAFFIC WAS TEMPORARILY SUSPENDED AFTER THE STRIKE."),
        ("MARKETS", "ANTHROPIC DEBUTS IN BIGGEST IPO EVER",
         "ANTHROPIC BEGAN TRADING ON NASDAQ UNDER \"ANT\" AFTER A $83-A-SHARE "
         "IPO. THE SALE OF 980 MILLION SHARES RAISED $81.3 BILLION - THE "
         "LARGEST IPO EVER."),
    ]
    pw = (CW - 20) // 2
    row_y = y
    for row in range(2):
        col_y = row_y
        max_bottom = row_y
        for col in range(2):
            px = M + col * (pw + 20)
            kicker, head, body = panels[row * 2 + col]
            yy = col_y
            cv.rect(px, yy, pw, 4, RED)
            yy += 8
            cv.text(px, yy, kicker, 2, RED)
            yy += 7 * 2 + 4
            yy = cv.para(px, yy, head, 3, INK, pw, leading=7 * 3 + 3)
            yy += 3
            yy = cv.para(px, yy, body, 2, INK, pw, leading=7 * 2 + 1)
            max_bottom = max(max_bottom, yy)
        row_y = max_bottom + 12
        if row == 0:
            cv.hline(M, row_y - 6, CW, GREY, 1)
    y = row_y + 2
    cv.hline(M, y, CW, INK, 3)
    y += 12

    # --- strip band: three short items ---
    cv.text(M, y, "ALSO MAKING NEWS", 2, RED)
    y += 7 * 2 + 8
    strip = [
        ("GAZA: ", "ISRAELI TANKS PUSH INTO CENTRAL GAZA BEYOND THE YELLOW "
         "LINE, NEAR NUSEIRAT; THE IDF SAID IT ENDED THE SAME DAY."),
        ("GREENLAND: ", "DENMARK APPROVES (109-0) A SECURITY DEAL WITH "
         "GREENLAND AND THE US, PAVING THE WAY FOR MORE US BASES."),
        ("WASHINGTON: ", "HOUSE DEMOCRATS NOMINATE HAKEEM JEFFRIES FOR "
         "SPEAKER, 251-11; THE FULL HOUSE VOTES JAN. 3."),
    ]
    sw = (CW - 40) // 3
    strip_bottom = y
    for i, (label, text) in enumerate(strip):
        sx = M + i * (sw + 20)
        yy = y
        yy = cv.para(sx, yy, label + text, 2, INK, sw, leading=7 * 2 + 1)
        strip_bottom = max(strip_bottom, yy)
    y = strip_bottom + 8
    cv.hline(M, y, CW, INK, 3)
    y += 8

    # --- ticker at the very bottom ---
    ticker = ("ALSO THURSDAY: CYCLONE AKVAN DUE FRIDAY OFF ANDHRA "
            "PRADESH-ODISHA | TRUMP ASKS SUPREME COURT TO BLOCK RESTORED "
            "PROTECTIONS FOR VENEZUELAN MIGRANTS | IAEA: NORTH KOREA "
            "EXPANDING URANIUM ENRICHMENT AT YONGBYON | TAKAICHI AND PUTIN "
            "AGREE TO KEEP TALKING | GTA VI RELEASES TODAY")
    th = H - y - 12
    cv.rect(M, y, CW, th, INK)
    lines = wrap(ticker, 2, CW - 32)
    ty = y + max(4, (th - len(lines) * (7 * 2 + 2)) // 2)
    for line in lines:
        cv.text(M + 16, ty, line, 2, PAPER)
        ty += 7 * 2 + 2
    print(f"layout: ticker at y={y}, band={th}px, {len(lines)} lines")
    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, 'entry.png')
    size = write_png(cv, path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == '__main__':
    main()
