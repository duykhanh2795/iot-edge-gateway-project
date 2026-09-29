from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math


OUT = Path(r"F:\iot-edge-gateway-project\output\midterm-beehive\kien_truc_he_thong_to_ong_dong_bo.png")
W, H = 2400, 1450
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

REG = r"C:\Windows\Fonts\arial.ttf"
BOLD = r"C:\Windows\Fonts\arialbd.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def wrapped(text, max_chars):
    lines = []
    for block in text.split("\n"):
        words = block.split()
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return "\n".join(lines)


def box(x1, y1, x2, y2, text, fill, outline="#475569", fs=29, bold=False, radius=12):
    d.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=3)
    max_chars = max(9, int((x2 - x1) / (fs * 0.56)))
    label = wrapped(text, max_chars)
    bbox = d.multiline_textbbox((0, 0), label, font=font(fs, bold), spacing=5, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.multiline_text(((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2), label,
                     font=font(fs, bold), fill="#111827", spacing=5, align="center")


def arrow(x1, y1, x2, y2, label="", dashed=False, color="#334155", fs=24):
    if dashed:
        parts = 14
        for i in range(parts):
            if i % 2 == 0:
                xa = x1 + (x2 - x1) * i / parts
                ya = y1 + (y2 - y1) * i / parts
                xb = x1 + (x2 - x1) * (i + 1) / parts
                yb = y1 + (y2 - y1) * (i + 1) / parts
                d.line((xa, ya, xb, yb), fill=color, width=4)
    else:
        d.line((x1, y1, x2, y2), fill=color, width=4)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 15
    points = [
        (x2, y2),
        (x2 - size * math.cos(angle - 0.55), y2 - size * math.sin(angle - 0.55)),
        (x2 - size * math.cos(angle + 0.55), y2 - size * math.sin(angle + 0.55)),
    ]
    d.polygon(points, fill=color)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        bbox = d.textbbox((0, 0), label, font=font(fs))
        pad = 4
        d.rectangle((mx - (bbox[2] - bbox[0]) / 2 - pad, my - 22,
                     mx + (bbox[2] - bbox[0]) / 2 + pad, my + 10), fill="white")
        d.text((mx, my - 6), label, font=font(fs), fill="#111827", anchor="mm")


d.text((W / 2, 42), "SƠ ĐỒ KIẾN TRÚC HỆ THỐNG GIÁM SÁT TỔ ONG",
       font=font(42, True), fill="#111827", anchor="mm")

site_specs = [("TRẠI A - 52 THÙNG", 100), ("TRẠI B - 47 THÙNG", 470), ("TRẠI C - 61 THÙNG", 840)]

for title, y in site_specs:
    d.rounded_rectangle((35, y, 960, y + 315), radius=18, fill="#FFF9EC", outline="#D98E04", width=4)
    d.text((60, y + 20), title, font=font(30, True), fill="#3A2E00")
    box(65, y + 75, 300, y + 205, "Node ESP32\nCảm biến tổ ong", "#FFE8B3", "#D98E04", 27, True)
    box(65, y + 225, 300, y + 285, "Weather node x1", "#FFE8B3", "#D98E04", 25)
    box(350, y + 110, 520, y + 240, "Wi-Fi AP\nngoài trời", "#B3D9FF", "#1B6FC9", 27, True)
    box(555, y + 70, 795, y + 270,
        "EDGE GATEWAY\nMosquitto cục bộ\nLocal Rule Engine\nSQLite + file cache\nUpload/OTA Agent",
        "#C9F2C0", "#2E9E2E", 23, True)
    box(825, y + 115, 930, y + 220, "Còi", "#FFB3B3", "#D62828", 28, True)
    arrow(300, y + 140, 350, y + 155, "MQTT/mTLS", fs=19)
    arrow(300, y + 255, 350, y + 205, "MQTT/mTLS", fs=19)
    arrow(520, y + 175, 555, y + 175, "LAN", fs=18)
    arrow(795, y + 168, 825, y + 168, "cmd", fs=17)

# Two logical buses keep the three site links readable.
d.line((995, 205, 995, 945), fill="#334155", width=5)
d.line((1045, 290, 1045, 1030), fill="#64748B", width=4)
for _, y in site_specs:
    arrow(795, y + 105, 995, y + 105, "OUT", fs=17)
    arrow(1045, y + 250, 795, y + 250, "CMD", dashed=True, fs=17)
d.ellipse((978, 560, 1012, 594), fill="white", outline="#334155", width=4)
d.ellipse((1028, 690, 1062, 724), fill="white", outline="#64748B", width=4)

# Central broker
box(1090, 480, 1350, 790, "MOSQUITTO\nTRUNG TÂM\nVPS/Cloud\n4G + TLS",
    "#C9F2C0", "#2E9E2E", 31, True)
arrow(995, 577, 1090, 577, "Bridge OUT", fs=19)
arrow(1090, 707, 1045, 707, "Bridge CMD", dashed=True, fs=17)

# Backend container
d.rounded_rectangle((1410, 100, 2110, 1245), radius=20, fill="#F5F0FF", outline="#7B3FE4", width=4)
d.text((1760, 135), "BACKEND VÀ LƯU TRỮ - CLOUD", font=font(32, True), fill="#2E1354", anchor="mm")

box(1605, 190, 1915, 300, "Ingest Consumer\nkiểm tra + khử lặp", "#E6D9FF", "#7B3FE4", 27, True)
box(1440, 390, 1645, 515, "TimescaleDB\nTelemetry", "#FFD1DC", "#D63A6A", 24, True)
box(1660, 390, 1865, 515, "PostgreSQL\nEvent + audit", "#FFD1DC", "#D63A6A", 24, True)
box(1880, 390, 2080, 515, "Central Rule\nEngine", "#E6D9FF", "#7B3FE4", 25, True)
box(1440, 630, 1645, 750, "Redis\nTrạng thái", "#FFD1DC", "#D63A6A", 25, True)
box(1660, 630, 1865, 750, "Device Status\nService", "#E6D9FF", "#7B3FE4", 25, True)
box(1880, 630, 2080, 750, "Notification\nService", "#E6D9FF", "#7B3FE4", 24, True)
box(1440, 875, 1645, 995, "Command\nService", "#E6D9FF", "#7B3FE4", 25, True)
box(1740, 875, 2035, 995, "REST/WebSocket API", "#E6D9FF", "#7B3FE4", 26, True)

box(2160, 190, 2370, 350, "Object Storage\nAudio + OTA", "#FFD1DC", "#D63A6A", 25, True)
box(2160, 790, 2370, 905, "Dashboard Web", "#FFF3B0", "#C9A400", 25, True)
box(2160, 990, 2370, 1105, "Mobile App", "#FFF3B0", "#C9A400", 26, True)

# Cleaner internal flow: labels are carried by nodes and legend, not every line.
arrow(1350, 610, 1605, 245, "subscribe", fs=19)
arrow(1660, 300, 1540, 390)
arrow(1760, 300, 1760, 390)
arrow(1915, 265, 1980, 390)
arrow(1820, 300, 1760, 630)
arrow(1760, 630, 1645, 690)
arrow(1760, 630, 1760, 515)
arrow(1980, 515, 1980, 630)
arrow(1540, 515, 1840, 875)
arrow(1760, 515, 1870, 875)
arrow(1540, 750, 1780, 875)
arrow(1880, 935, 1645, 935, "command", dashed=True, fs=18)
arrow(1440, 935, 1350, 720, "publish cmd", dashed=True, fs=18)

# File and user paths.
arrow(960, 330, 2160, 270, "HTTPS audio / firmware", dashed=True, fs=19)
arrow(2035, 920, 2160, 845, "REST/WS", fs=19)
arrow(2080, 690, 2160, 1045, "Push/SMS", fs=19)
arrow(2160, 1045, 2035, 950, "ACK / cmd", dashed=True, fs=18)

d.text((1200, 1370),
       "Đường liền: dữ liệu/truy vấn   |   Đường đứt: command hoặc truyền file   |   Các điểm gom trên sơ đồ chỉ là tuyến logic",
       font=font(27), fill="#334155", anchor="mm")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, quality=95)
print(OUT)
