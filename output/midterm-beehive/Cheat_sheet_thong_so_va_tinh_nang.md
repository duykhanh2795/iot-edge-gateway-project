# Cheat sheet thông số và tính năng hệ thống giám sát tổ ong

Tài liệu này dùng để tra nhanh khi trình bày. Các giá trị bên dưới bám theo báo cáo hiện tại.

## 1. Quy mô hệ thống

| Hạng mục | Giá trị |
|---|---:|
| Trại A | 52 thùng ong |
| Trại B | 47 thùng ong |
| Trại C | 61 thùng ong |
| Tổng node thùng ong | 160 node |
| Weather node | 3 node, mỗi trại 1 node |
| Edge Gateway | 3 gateway, mỗi trại 1 gateway |
| Tổng thiết bị được quản lý | 166 thiết bị |
| Uplink trại A | 10 Mbps |
| Uplink trại B | 5 Mbps |
| Uplink trại C | 3 Mbps |

Mỗi node thùng ong gồm ESP32, cảm biến nhiệt độ - độ ẩm, load cell và HX711, IMU, microphone, mạch đo pin và nguồn điện.

## 2. Thành phần chạy ở đâu

### Tại mỗi trại

- ESP32 và các cảm biến.
- Wi-Fi AP ngoài trời.
- Còi cảnh báo.
- Edge Gateway.
- Mosquitto cục bộ.
- Local Rule Engine.
- SQLite và file cache.
- Upload/OTA Agent.

### Trên VPS hoặc Cloud

- Mosquitto trung tâm.
- Ingest Consumer.
- Central Rule Engine.
- Device Status Service.
- Notification Service.
- Command Service.
- REST/WebSocket API.
- TimescaleDB, PostgreSQL, Redis và Object Storage.
- Dashboard Web.

## 3. Chu kỳ gửi dữ liệu

| Dữ liệu | Chu kỳ | Ghi chú |
|---|---:|---|
| Snapshot của node thùng ong | 60 giây | Nhiệt độ, độ ẩm, khối lượng, góc nghiêng và pin |
| Đặc trưng âm thanh | 120 giây | Chỉ gửi đặc trưng nhỏ, không gửi audio thô |
| Heartbeat | 300 giây | Kèm pin, firmware, RSSI và trạng thái sống |
| Weather snapshot | 60 giây | Điều kiện môi trường ngoài trời |
| Event nghiêng hoặc giảm khối lượng | Gửi ngay | Không chờ chu kỳ định kỳ |
| Audio thô | Không gửi định kỳ | Chỉ thu 10 giây khi có lệnh `audio-capture` |

Cách nhớ: **60 - 120 - 300** tương ứng snapshot - acoustic feature - heartbeat.

## 4. Thời gian phản ứng và cảnh báo

| Tình huống | Mục tiêu thời gian |
|---|---:|
| Cảnh báo và bật còi tại trại | Dưới 2 giây |
| Cảnh báo tại trung tâm khi WAN tốt | Dưới 15 giây |
| Cập nhật dữ liệu môi trường | Dưới 60 giây |
| Cảnh báo pin yếu hoặc offline thông thường | Dưới 5 phút |
| Node bị coi là offline | Sau 3 chu kỳ snapshot, khoảng 180 giây |
| Gateway bị coi là offline | Khoảng 90 giây |
| MQTT keepalive | 60 giây |
| Cảnh báo chưa được ACK | Sau 2 phút thì chuyển cấp hoặc gửi thêm kênh |

Local Rule Engine xử lý nghiêng và giảm khối lượng ngay tại trại, nên mất 4G vẫn có thể bật còi.

## 5. MQTT và topic

### Quy tắc chung

- QoS sử dụng: QoS 1.
- MQTT trong LAN: mTLS giữa MQTT client và broker cục bộ.
- MQTT Bridge: TLS qua 4G.
- Chỉ `state/status` được retained.
- `telemetry`, `event` và `cmd` không retained.
- Backend khử bản tin trùng bằng `deviceId + seq`.
- Command khử lặp bằng `commandId` và có `expiresAt`.

### Cấu trúc topic trung tâm

```text
bee/{siteId}/{assetType}/{assetId}/{group}/{name}
```

Ví dụ:

```text
bee/site-a/hive/hive-017/telemetry/snapshot
bee/site-c/hive/hive-023/event/tilt
bee/site-b/hive/hive-031/cmd/audio-capture
```

### Các nhóm topic

| Nhóm | Hướng chính | Retained |
|---|---|---|
| `telemetry/#` | Trại lên trung tâm | Không |
| `event/#` | Trại lên trung tâm | Không |
| `state/status` | Trại lên trung tâm | Có |
| `cmd/#` | Trung tâm xuống trại | Không |

Không retained command vì node reconnect có thể thực hiện lại một lệnh cũ.

## 6. Các lệnh điều khiển

Backend có thể gửi các lệnh sau:

- Thay đổi chu kỳ gửi dữ liệu.
- Thay đổi ngưỡng cảnh báo.
- Hiệu chuẩn cân.
- Thu audio 10 giây.
- Restart node.
- Cập nhật OTA.
- Bật hoặc tắt còi.

Luồng command:

```text
Dashboard/Mobile
→ API
→ Command Service
→ Mosquitto trung tâm
→ MQTT Bridge
→ Mosquitto cục bộ
→ ESP32 hoặc còi
```

## 7. Mất WAN và lưu tạm

### Kịch bản thiết kế

- Trại C mất 4G trong 18 giờ, tương đương 64.800 giây.
- LAN, Gateway, broker cục bộ và còi vẫn hoạt động.
- Dữ liệu được lưu tại Gateway và gửi bù khi WAN phục hồi.

### Dung lượng và hàng đợi

| Thông số | Giá trị |
|---|---:|
| Bản tin tồn đọng trong 18 giờ | Khoảng 113.076 message |
| Payload ứng dụng | Khoảng 20,24 MiB |
| Nhu cầu sau overhead và dự phòng | Khoảng 32,89 MiB |
| `max_queued_messages` | 160.000 message |
| `max_queued_bytes` | 64 MiB |
| `autosave_interval` | 60 giây |
| Tốc độ gửi bù | 512 kbps/site |
| Thời gian gửi bù dự kiến | Dưới 10 phút |
| Cache tại Gateway | 21 ngày |
| Vòng đệm tại node nếu Gateway mất | 6 giờ |

### Tham số bridge quan trọng

```text
persistence true
cleansession false
queue_qos0_messages false
restart_timeout 5 120
```

- `persistence true`: giữ queue và session sau khi broker restart.
- `cleansession false`: không bỏ session khi bridge mất kết nối.
- `queue_qos0_messages false`: không để QoS 0 chiếm hàng đợi quan trọng.
- `restart_timeout 5 120`: reconnect theo backoff từ 5 đến 120 giây.

## 8. Chính sách giảm dữ liệu khi hàng đợi gần đầy

| Mức đầy | Phản ứng |
|---|---|
| Trên 80% | Giảm acoustic feature từ 120 giây xuống 1 mẫu mỗi 10 phút |
| Trên 90% | Gộp snapshot thành trung bình 5 phút |
| Cần bỏ dữ liệu | Bỏ audio thô cũ trước, sau đó mới giảm telemetry |
| Luôn ưu tiên giữ | Event tilt, weight-drop, ACK command và audit |

Gateway phát event `data-degraded` để Backend biết khoảng dữ liệu đã bị giảm mẫu.

## 9. Audio capture và upload

### Thông số audio

- Độ dài bản ghi: 10 giây.
- Mẫu tham chiếu: 8 kHz, 16 bit, mono.
- Kích thước trước nén: khoảng 160.000 byte.
- Audio không được truyền trực tiếp qua MQTT.
- Audio trên Object Storage được giữ 30 ngày.

### Luồng hoạt động

```text
Người dùng nhấn Thu âm
→ Backend gửi command audio-capture
→ ESP32 ghi âm 10 giây
→ ESP32 gửi file cho Upload Agent trong LAN
→ Agent lưu cache
→ Agent upload Object Storage bằng HTTPS
→ Dashboard nhận signed URL
```

Nếu mất 4G, Agent giữ file trong cache và upload lại khi WAN phục hồi.

## 10. OTA firmware

### Điều kiện node được cập nhật

- Pin trên 50%.
- Không có event an ninh đang hoạt động.
- Đủ dung lượng flash.
- RSSI đạt ngưỡng.

### Manifest OTA

- Phiên bản firmware.
- URL HTTPS.
- SHA-256.
- Chữ ký Ed25519.
- `expiresAt`.

### Các đợt triển khai

```text
5 node canary → 10% → 30% → phần còn lại
```

- Chờ ít nhất 30 phút giữa các đợt.
- Dừng nếu tỷ lệ lỗi cập nhật vượt 2%.
- Dừng nếu tỷ lệ offline tăng trên 3%.
- Dừng nếu xuất hiện sai lệch cảm biến sau reboot.
- Rollback nếu node không heartbeat trong 180 giây hoặc health check thất bại.

### Luồng firmware

```text
Object Storage
→ Upload/OTA Agent trên Gateway
→ ESP32 qua LAN
```

Gateway tải firmware một lần qua 4G rồi phân phối nội bộ theo batch. ESP32 dùng hai phân vùng A/B để quay lại firmware cũ khi cập nhật thất bại.

## 11. Theo dõi online, offline và isolated

- Node publish retained birth `online` khi kết nối.
- Node đặt Last Will retained `offline`.
- Heartbeat ứng dụng gửi mỗi 300 giây.
- Node offline khi mất ba snapshot liên tiếp, khoảng 180 giây.
- Gateway offline sau khoảng 90 giây.
- Nếu Gateway còn chạy nhưng mất WAN, site có trạng thái `isolated`, không gán nhầm toàn bộ node thành offline.
- Trạng thái hiện tại nằm trong Redis; lịch sử trạng thái nằm trong PostgreSQL.

## 12. Lưu trữ và thời hạn giữ

| Dữ liệu | Nơi lưu | Thời hạn |
|---|---|---:|
| Telemetry thô tại Gateway | SQLite | 21 ngày |
| Telemetry thô trung tâm | TimescaleDB | 180 ngày |
| Tổng hợp 15 phút | TimescaleDB | 2 năm |
| Tổng hợp 1 giờ | TimescaleDB | 5 năm |
| Tổng hợp 1 ngày | TimescaleDB | 10 năm |
| Event và alert | PostgreSQL | 5 năm |
| Hồ sơ thiết bị/người dùng | PostgreSQL | Vòng đời + 5 năm |
| Trạng thái tức thời | Redis | 24 giờ |
| Audio | Object Storage | 30 ngày |
| Firmware | Object Storage | Trong thời gian phiên bản còn được hỗ trợ |

## 13. Băng thông và tải

| Trại | Message/s | WAN sau overhead | Tỷ lệ uplink |
|---|---:|---:|---:|
| A | 1,490 | 2,908 kbps | 0,029% |
| B | 1,348 | 2,632 kbps | 0,053% |
| C | 1,745 | 3,406 kbps | 0,114% |
| Tổng | 4,583 | 8,946 kbps | Rất nhỏ so với uplink |

Khi toàn bộ thiết bị reconnect cùng lúc:

- Khoảng 51,5 KB payload.
- Khoảng 67 KB sau overhead.
- Có thể đạt khoảng 536 kbps nếu dồn trong 1 giây.
- Node dùng jitter ngẫu nhiên từ 0 đến 180 giây để tránh kết nối đồng loạt.

## 14. Bảo mật và danh tính

- Mỗi node có `deviceId`, MQTT `clientId` và chứng chỉ riêng.
- Node xác thực với broker cục bộ bằng mTLS.
- Mỗi MQTT Bridge có chứng chỉ riêng theo site.
- Người dùng đăng nhập Backend bằng OIDC và được phân quyền RBAC.
- Node chỉ được ghi dữ liệu của chính nó và đọc command của chính nó.
- Ứng dụng người dùng không truy cập MQTT trực tiếp.
- Chứng chỉ được gia hạn hằng năm.
- Bắt đầu gia hạn trước 30 ngày.
- Hai chứng chỉ cũ và mới được chồng lấn tối đa 14 ngày.

## 15. Các phần mềm dễ nhầm

| Thành phần | Bản chất | Việc chính |
|---|---|---|
| Mosquitto | Phần mềm MQTT Broker | Nhận và chuyển bản tin |
| Ingest Consumer | Phần mềm Backend | Nhận, kiểm tra, khử trùng lặp và chia dữ liệu |
| Local Rule Engine | Phần mềm trên Gateway | Phát hiện nguy hiểm và bật còi tại trại |
| Central Rule Engine | Phần mềm Backend | Kiểm tra luật tổng hợp và tạo alert |
| Upload/OTA Agent | Phần mềm trên Gateway | Chuyển audio lên và firmware xuống |
| Command Service | Phần mềm Backend | Kiểm tra quyền, tạo và audit command |
| Device Status Service | Phần mềm Backend | Xác định online, offline và isolated |
| Notification Service | Phần mềm Backend | Gửi Push, SMS, Email và quản lý ACK |

## 16. Ba luồng cần nhớ khi thuyết trình

### Dữ liệu đi lên

```text
ESP32 → Wi-Fi AP → Edge Gateway → MQTT Bridge
→ Mosquitto trung tâm → Ingest Consumer
→ Database / Rule Engine / Device Status
→ API → Dashboard
```

### Lệnh đi xuống

```text
Dashboard → API → Command Service → Mosquitto trung tâm
→ MQTT Bridge → Mosquitto cục bộ → ESP32 hoặc còi
```

### Mất 4G

```text
ESP32 → Gateway → Local Rule Engine → Còi vẫn hoạt động
                    ↓
              Lưu dữ liệu cục bộ
                    ↓
           Có mạng lại thì gửi bù
```

## 17. Các con số nên học thuộc

```text
52 - 47 - 61       Số thùng tại A, B, C
160                Tổng node thùng ong
166                Tổng thiết bị quản lý
60 - 120 - 300     Snapshot, acoustic feature, heartbeat
<2 giây            Cảnh báo cục bộ
<15 giây           Cảnh báo trung tâm khi WAN tốt
180 giây           Node offline hoặc OTA rollback
18 giờ             Kịch bản mất WAN
21 ngày            Cache tại Gateway
64 MiB              Queue bridge
512 kbps/site       Tốc độ gửi bù
10 giây             Audio capture
180 ngày            Telemetry thô trung tâm
30 ngày             Lưu audio
5 → 10% → 30%      Các đợt OTA trước phần còn lại
```
