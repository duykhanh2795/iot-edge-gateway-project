from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math


OUT = Path(r"F:\iot-edge-gateway-project\output\midterm-beehive\kien_truc_he_thong_to_ong_dong_bo.png")
W, H = 1800, 1600
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


def box(x1, y1, x2, y2, text, fill, outline="#475569", fs=24, bold=False, radius=12):
    d.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=3)
    max_chars = max(8, int((x2 - x1) / (fs * 0.56)))
    label = wrapped(text, max_chars)
    bbox = d.multiline_textbbox((0, 0), label, font=font(fs, bold), spacing=4, align="center")
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.multiline_text(((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2), label,
                     font=font(fs, bold), fill="#111827", spacing=4, align="center")


def line(points, dashed=False, color="#334155", width=4):
    for a, b in zip(points, points[1:]):
        if dashed:
            length = math.dist(a, b)
            parts = max(1, int(length / 18))
            for i in range(parts):
                if i % 2 == 0:
                    p1 = (a[0] + (b[0] - a[0]) * i / parts, a[1] + (b[1] - a[1]) * i / parts)
                    p2 = (a[0] + (b[0] - a[0]) * (i + 1) / parts, a[1] + (b[1] - a[1]) * (i + 1) / parts)
                    d.line((*p1, *p2), fill=color, width=width)
        else:
            d.line((*a, *b), fill=color, width=width)


def poly_arrow(points, label="", dashed=False, color="#334155", fs=20, label_at=None):
    line(points, dashed=dashed, color=color)
    (x1, y1), (x2, y2) = points[-2], points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 14
    d.polygon([
        (x2, y2),
        (x2 - size * math.cos(angle - 0.55), y2 - size * math.sin(angle - 0.55)),
        (x2 - size * math.cos(angle + 0.55), y2 - size * math.sin(angle + 0.55)),
    ], fill=color)
    if label:
        if label_at is None:
            a, b = points[0], points[1]
            lx, ly = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        else:
            lx, ly = label_at
        bbox = d.textbbox((0, 0), label, font=font(fs))
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.rectangle((lx - tw / 2 - 5, ly - th / 2 - 3, lx + tw / 2 + 5, ly + th / 2 + 3), fill="white")
        d.text((lx, ly), label, font=font(fs), fill="#111827", anchor="mm")


d.text((W / 2, 35), "SƠ ĐỒ KIẾN TRÚC HỆ THỐNG GIÁM SÁT TỔ ONG",
       font=font(35, True), fill="#111827", anchor="mm")

sites = [("TRẠI A - 52 THÙNG", 30), ("TRẠI B - 47 THÙNG", 620), ("TRẠI C - 61 THÙNG", 1210)]
for title, x in sites:
    d.rounded_rectangle((x, 75, x + 560, 390), radius=16, fill="#FFF9EC", outline="#D98E04", width=4)
    d.text((x + 280, 100), title, font=font(25, True), fill="#3A2E00", anchor="mm")
    box(x + 25, 135, x + 185, 235, "Node ESP32 × N\nDHT / load cell\nIMU / mic / pin", "#FFE8B3", "#D98E04", 19, True)
    box(x + 25, 260, x + 185, 335, "Weather node × 1", "#FFE8B3", "#D98E04", 19)
    box(x + 220, 185, x + 330, 285, "Wi-Fi AP\nngoài trời", "#B3D9FF", "#1B6FC9", 20, True)
    box(x + 360, 135, x + 525, 285, "EDGE GATEWAY\nMosquitto local\nRule Engine local\nSQLite/file cache\nUpload/OTA Agent", "#C9F2C0", "#2E9E2E", 17, True)
    box(x + 400, 310, x + 490, 365, "Còi", "#FFB3B3", "#D62828", 20, True)
    poly_arrow([(x + 185, 185), (x + 220, 220)], "MQTT", fs=15, label_at=(x + 202, 185))
    poly_arrow([(x + 185, 298), (x + 220, 260)], "MQTT", fs=15, label_at=(x + 202, 300))
    poly_arrow([(x + 330, 235), (x + 360, 235)])
    poly_arrow([(x + 445, 285), (x + 445, 310)], "cmd", fs=14, label_at=(x + 475, 298))

out_y, cmd_y = 430, 485
for _, x in sites:
    cx = x + 445
    poly_arrow([(cx, 285), (cx, out_y)])
    poly_arrow([(cx + 38, cmd_y), (cx + 38, 285)], dashed=True, color="#64748B")
line([(475, out_y), (1325, out_y)], color="#334155", width=5)
line([(475, cmd_y), (1325, cmd_y)], dashed=True, color="#64748B", width=4)
d.text((900, out_y - 16), "Bridge MQTT/TLS qua 4G: telemetry / event / state", font=font(20), fill="#334155", anchor="mm")
d.text((900, cmd_y + 18), "Lệnh cmd từ trung tâm về đúng site", font=font(20), fill="#475569", anchor="mm")

box(705, 525, 1095, 655, "MOSQUITTO TRUNG TÂM\nVPS/Cloud có public IP\nBroker nhận dữ liệu và chuyển lệnh", "#C9F2C0", "#2E9E2E", 23, True)
poly_arrow([(900, out_y), (900, 525)], "publish", fs=18, label_at=(950, 505))
poly_arrow([(955, 525), (955, cmd_y)], "cmd", dashed=True, color="#64748B", fs=17, label_at=(990, 505))

d.rounded_rectangle((30, 700, 1770, 1510), radius=18, fill="#F5F0FF", outline="#7B3FE4", width=4)
d.text((900, 730), "BACKEND VÀ KHO LƯU TRỮ - VPS/CLOUD", font=font(29, True), fill="#2E1354", anchor="mm")

box(70, 790, 310, 900, "Ingest Consumer\nvalidate + khử lặp", "#E6D9FF", "#7B3FE4", 21, True)
box(410, 775, 635, 885, "TimescaleDB\nTelemetry", "#FFD1DC", "#D63A6A", 21, True)
box(690, 775, 915, 885, "PostgreSQL\nEvent / audit / status", "#FFD1DC", "#D63A6A", 20, True)
box(970, 775, 1195, 885, "Central Rule Engine\nLuật toàn hệ thống", "#E6D9FF", "#7B3FE4", 20, True)
box(1250, 775, 1475, 885, "Device Status\nService", "#E6D9FF", "#7B3FE4", 21, True)
box(1530, 775, 1730, 885, "Redis\nTrạng thái nhanh", "#FFD1DC", "#D63A6A", 20, True)

box(970, 1030, 1195, 1140, "Notification Service\nPush / SMS / ACK", "#E6D9FF", "#7B3FE4", 20, True)
box(1250, 1030, 1475, 1140, "REST / WebSocket API", "#E6D9FF", "#7B3FE4", 21, True)
box(410, 1270, 635, 1380, "Command Service\nRBAC + audit", "#E6D9FF", "#7B3FE4", 20, True)
box(70, 1270, 310, 1380, "Object Storage\nAudio + firmware OTA\nHTTPS trực tiếp gateway", "#FFD1DC", "#D63A6A", 18, True)
box(1250, 1270, 1475, 1380, "Dashboard Web", "#FFF3B0", "#C9A400", 22, True)
box(1530, 1270, 1730, 1380, "Mobile App", "#FFF3B0", "#C9A400", 22, True)

poly_arrow([(705, 590), (190, 590), (190, 790)], "subscribe", fs=18, label_at=(360, 590))

poly_arrow([(310, 845), (350, 845)])
line([(350, 845), (350, 945), (1362, 945)], color="#334155", width=5)
for cx in (522, 802, 1082, 1362):
    poly_arrow([(cx, 945), (cx, 885)])
d.text((760, 968), "luồng đã kiểm tra: lưu đồng thời + chuyển sang xử lý", font=font(18), fill="#334155", anchor="mm")

poly_arrow([(1475, 830), (1530, 830)], "cache", fs=16, label_at=(1503, 805))
poly_arrow([(1362, 885), (1362, 980), (802, 980), (802, 885)], "lưu lịch sử", fs=16, label_at=(1080, 980))
poly_arrow([(1082, 885), (1082, 1030)])
poly_arrow([(802, 885), (802, 1185), (1320, 1185), (1320, 1140)], "query", fs=17, label_at=(1045, 1185))
poly_arrow([(1630, 885), (1630, 1200), (1405, 1200), (1405, 1140)], "trạng thái hiện tại", fs=16, label_at=(1515, 1200))
poly_arrow([(1362, 1140), (1362, 1270)], "REST/WS", fs=17, label_at=(1415, 1205))
poly_arrow([(1195, 1060), (1220, 1060), (1220, 1000), (1630, 1000), (1630, 1270)],
           "Push/SMS", fs=17, label_at=(1420, 1000))

poly_arrow([(1530, 1325), (1475, 1325)], "ACK/cmd", dashed=True, color="#64748B", fs=16, label_at=(1502, 1295))
poly_arrow([(1290, 1140), (1290, 1220), (745, 1220), (745, 1325), (635, 1325)],
           "yêu cầu điều khiển", dashed=True, color="#64748B", fs=16, label_at=(990, 1220))
poly_arrow([(410, 1325), (350, 1325), (350, 620), (705, 620)], "publish cmd", dashed=True, color="#64748B", fs=17, label_at=(500, 620))

d.text((900, 1555),
       "Đường liền: dữ liệu / truy vấn   |   Đường đứt: command hoặc truyền file   |   Bus chỉ là cách gom dây để sơ đồ dễ đọc",
       font=font(20), fill="#334155", anchor="mm")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, quality=95)
print(OUT)
