# Hướng dẫn nắm toàn bộ hệ thống giám sát tổ ong để báo cáo

## 1. Hệ thống giải quyết bài toán gì

Hợp tác xã có ba trại với tổng cộng 160 thùng ong. Việc kiểm tra thủ công khiến người quản lý khó biết kịp thời khi:

- Nhiệt độ hoặc độ ẩm trong tổ bất thường.
- Khối lượng thùng thay đổi.
- Thùng bị nghiêng, nhấc lên hoặc di chuyển.
- Thiết bị yếu pin hoặc mất kết nối.

Hệ thống gắn một node IoT cho mỗi thùng, xử lý cảnh báo khẩn cấp ngay tại trại và gửi dữ liệu lên Cloud để lưu trữ, theo dõi và điều khiển từ xa.

Một câu mô tả ngắn gọn:

> ESP32 thu dữ liệu tại từng thùng; Edge Gateway xử lý và lưu tạm tại trại; MQTT Bridge chuyển dữ liệu lên Backend trên Cloud; Dashboard giúp người dùng theo dõi, nhận cảnh báo và gửi lệnh.

## 2. Quy mô cần nhớ

| Trại | Số thùng ong |
|---|---:|
| A | 52 |
| B | 47 |
| C | 61 |
| Tổng | 160 |

Ngoài 160 node thùng ong, mỗi trại có một weather node và một Edge Gateway. Tổng số thiết bị được quản lý là:

```text
160 node thùng + 3 weather node + 3 gateway = 166 thiết bị
```

## 3. Các phần cứng tại trại

### 3.1. Node thùng ong

Node thùng ong là một cụm thiết bị IoT gắn cho một thùng, không phải một cảm biến riêng.

```text
Node thùng ong
├── ESP32: bộ điều khiển
├── Cảm biến nhiệt độ và độ ẩm
├── Load cell + HX711: cân thùng ong
├── IMU: phát hiện nghiêng, rung và di chuyển
├── Microphone: thu tín hiệu âm thanh
├── Mạch đo pin
└── Pin hoặc nguồn điện
```

ESP32 đọc các cảm biến, xử lý sơ bộ, đóng gói dữ liệu và gửi MQTT về Gateway.

### 3.2. Weather node

Mỗi trại có một weather node:

```text
1 ESP32 + cảm biến môi trường ngoài trời
```

Bản đơn giản dùng DHT22 để đo nhiệt độ và độ ẩm ngoài trời. Dữ liệu này được dùng để so sánh môi trường ngoài trời với điều kiện bên trong các tổ ong.

### 3.3. Wi-Fi AP ngoài trời

Wi-Fi AP tạo mạng LAN không dây để các ESP32 kết nối với Edge Gateway.

AP chỉ chuyển tiếp dữ liệu, không phân tích cảm biến và không chạy luật cảnh báo. Một thiết bị thực tế có thể tích hợp cả chức năng AP và router, nhưng trên sơ đồ ta nhấn mạnh vai trò phủ Wi-Fi tại trại.

### 3.4. Edge Gateway

Gateway là một máy tính nhỏ đặt tại trại, ví dụ Raspberry Pi, mini PC hoặc industrial gateway chạy Linux.

Gateway không phải cảm biến. Nó là máy chủ cục bộ chạy các phần mềm:

```text
Edge Gateway
├── Mosquitto cục bộ
├── Local Rule Engine
├── SQLite và file cache
└── Upload/OTA Agent
```

### 3.5. Còi

Còi là cơ cấu chấp hành tại trại. Nó subscribe topic command và bật khi Local Rule Engine phát hiện nguy cơ dịch chuyển hoặc trộm thùng.

## 4. Phần mềm chạy tại trại

### Mosquitto cục bộ

Mosquitto là phần mềm MQTT Broker, giống như bưu điện nhận và chuyển bản tin:

```text
ESP32 publish → Mosquitto → Rule Engine hoặc subscriber khác nhận
```

### Local Rule Engine

Đây là chương trình chứa luật `nếu - thì`:

```text
NẾU IMU và load cell cho thấy thùng bị di chuyển
THÌ tạo event và bật còi
```

Nó không phải AI và không phải phần cứng. Nó là code chạy trên Gateway.

### SQLite và file cache

- SQLite lưu telemetry cục bộ.
- File cache lưu audio hoặc firmware tạm thời.
- Dữ liệu tại Gateway được giữ 21 ngày.

### Upload/OTA Agent

Đây là chương trình chạy trên Gateway:

- Chiều upload: nhận file audio từ ESP32 và tải lên Object Storage.
- Chiều OTA: tải firmware từ Cloud một lần rồi phân phối cho các ESP32 qua LAN.

## 5. Phần trung tâm trên VPS hoặc Cloud

### Mosquitto trung tâm

Mosquitto trung tâm là phần mềm MQTT Broker chạy trên VPS/Cloud có public IP hoặc domain.

Ví dụ:

```text
mqtt.example.com:8883
```

Kết nối được bảo vệ bằng TLS/mTLS, chứng chỉ, firewall và ACL; không phải ai trên Internet cũng được truy cập.

### Backend

Backend cũng chạy trên VPS/Cloud và gồm các module phần mềm:

| Module | Bản chất và nhiệm vụ |
|---|---|
| Ingest Consumer | Nhận dữ liệu MQTT, kiểm tra và khử trùng lặp |
| Central Rule Engine | Kiểm tra luật tổng hợp và tạo cảnh báo |
| Device Status Service | Xác định online, offline hoặc isolated |
| Notification Service | Gửi Push, SMS, Email và quản lý ACK |
| Command Service | Kiểm tra quyền và gửi lệnh xuống thiết bị |
| REST/WebSocket API | Cung cấp dữ liệu cho Dashboard và Mobile App |

Các module trên có thể nằm trong cùng một ứng dụng Backend, không bắt buộc là nhiều server riêng.

### Các kho dữ liệu

| Kho | Dữ liệu chính |
|---|---|
| TimescaleDB | Telemetry theo thời gian |
| PostgreSQL | Event, alert, command, audit và hồ sơ thiết bị |
| Redis | Trạng thái hiện tại và cache Dashboard |
| Object Storage | Audio và firmware |

### Dashboard và Mobile App

Dashboard được host trên Cloud nhưng người dùng mở bằng trình duyệt. Dashboard không truy cập trực tiếp MQTT hay database; mọi yêu cầu đều đi qua API.

## 6. Use case 1: gửi dữ liệu định kỳ

Chu kỳ đã chốt:

```text
Snapshot cảm biến:   60 giây
Đặc trưng âm thanh: 120 giây
Heartbeat:          300 giây
Weather snapshot:    60 giây
Event bất thường:    gửi ngay
```

Luồng một snapshot bình thường:

```text
1. Cảm biến đo dữ liệu.
2. ESP32 đọc nhiệt độ, độ ẩm, khối lượng, góc nghiêng và pin.
3. ESP32 publish MQTT qua Wi-Fi.
4. Wi-Fi AP chuyển gói tin đến Mosquitto trên Gateway.
5. MQTT Bridge chuyển bản tin qua 4G/TLS lên Mosquitto trung tâm.
6. Ingest Consumer nhận, kiểm tra và khử trùng lặp.
7. Ingest chia dữ liệu đồng thời cho database, Rule Engine và Device Status.
8. API cung cấp dữ liệu cho Dashboard.
```

Đường đi rút gọn:

```text
ESP32 → AP → Gateway → MQTT Bridge → Mosquitto trung tâm
→ Ingest → Database/Rule/Status → API → Dashboard
```

## 7. Ingest Consumer xử lý gì

Ingest Consumer là phần mềm Backend subscribe Mosquitto trung tâm.

Khi nhận một bản tin, nó:

1. Kiểm tra JSON và schema.
2. Xác định site và thiết bị gửi.
3. Khử trùng lặp bằng `deviceId + seq`.
4. Chia dữ liệu sang nhiều nhánh song song.

```text
                         ┌→ TimescaleDB/PostgreSQL
Ingest Consumer ─────────┼→ Central Rule Engine
                         └→ Device Status Service
```

Không phải luôn lưu xong mới chạy Rule Engine; các nhánh có thể được xử lý đồng thời.

## 8. Use case 2: phát hiện thùng bị di chuyển

Đây là use case quan trọng nhất của xử lý Edge:

```text
1. IMU phát hiện nghiêng hoặc chuyển động.
2. Load cell phát hiện khối lượng tác động thay đổi nhanh.
3. ESP32 gửi event ngay, không đợi chu kỳ 60 giây.
4. Mosquitto cục bộ chuyển event cho Local Rule Engine.
5. Rule Engine kiểm tra điều kiện đã cấu hình.
6. Nếu nguy hiểm, Rule Engine publish lệnh bật còi.
7. Mosquitto chuyển lệnh cho còi.
8. Còi phản ứng mục tiêu dưới 2 giây.
9. Event đồng thời được gửi lên trung tâm khi WAN hoạt động.
```

Đường cảnh báo tại chỗ:

```text
ESP32 → AP → Mosquitto cục bộ → Local Rule Engine
→ Mosquitto cục bộ → Còi
```

Luồng này không cần Cloud nên vẫn hoạt động khi mất 4G.

## 9. Use case 3: tạo cảnh báo trung tâm và ACK

Sau khi event lên Cloud:

```text
1. Ingest Consumer nhận event.
2. Central Rule Engine kiểm tra, tổng hợp và chống tạo alert trùng.
3. Alert được lưu trong PostgreSQL.
4. Notification Service gửi Push, SMS hoặc Email.
5. Người dùng bấm xác nhận đã biết, gọi là ACK.
6. ACK đi từ Mobile App qua API đến Notification Service.
7. PostgreSQL lưu trạng thái acknowledged.
```

Trạng thái điển hình:

```text
pending → sent → acknowledged
```

Nếu sau 2 phút chưa có ACK, Notification Service có thể escalate: gửi thêm kênh hoặc chuyển cảnh báo cho người có trách nhiệm cao hơn.

## 10. Use case 4: gửi command từ Cloud xuống thiết bị

Ví dụ người dùng thay đổi chu kỳ gửi hoặc yêu cầu node ghi âm:

```text
1. Người dùng thao tác trên Dashboard.
2. Dashboard gọi API.
3. API xác thực người dùng.
4. Command Service kiểm tra RBAC.
5. Command Service tạo commandId và expiresAt.
6. Command và audit được lưu vào PostgreSQL.
7. Command Service publish lệnh lên Mosquitto trung tâm.
8. MQTT Bridge chuyển lệnh xuống đúng trại.
9. Mosquitto cục bộ chuyển lệnh cho đúng ESP32.
10. ESP32 kiểm tra commandId, hạn lệnh rồi mới thực hiện.
```

Đường đi rút gọn:

```text
Dashboard → API → Command Service → Mosquitto trung tâm
→ MQTT Bridge → Mosquitto cục bộ → ESP32
```

Các lệnh có thể gồm:

- Đổi chu kỳ gửi hoặc ngưỡng.
- Hiệu chuẩn cân.
- `audio-capture`.
- Restart.
- OTA.
- Bật hoặc tắt còi.

Command dùng QoS 1 nhưng không retained để tránh node reconnect rồi chạy lại lệnh cũ.

## 11. Use case 5: thu và tải audio

Audio thô không được gửi định kỳ qua MQTT.

```text
1. Người dùng chọn Thu âm trên Dashboard.
2. Backend gửi command audio-capture đến đúng node.
3. ESP32 ghi âm 10 giây.
4. ESP32 chuyển file qua LAN cho Upload Agent trên Gateway.
5. Agent lưu file vào cache.
6. Nếu WAN hoạt động, Agent upload file bằng HTTPS lên Object Storage.
7. Backend tạo signed URL.
8. Dashboard dùng signed URL để phát hoặc tải file.
```

Nếu mất 4G, file nằm trong cache và được upload khi mạng phục hồi.

MQTT chỉ truyền command và metadata; file audio thật đi bằng HTTPS.

## 12. Use case 6: cập nhật firmware OTA

```text
1. Firmware và manifest được đưa lên Object Storage.
2. Manifest chứa version, URL, SHA-256, chữ ký Ed25519 và expiresAt.
3. Backend gửi lệnh OTA đến Gateway hoặc node mục tiêu.
4. Upload/OTA Agent tải firmware một lần qua 4G.
5. Agent kiểm tra file rồi lưu cache.
6. Agent phân phối firmware cho ESP32 qua LAN theo từng batch.
7. ESP32 tự kiểm SHA-256 và chữ ký.
8. ESP32 ghi firmware vào phân vùng B rồi reboot.
9. Nếu health check thất bại, thiết bị quay lại phân vùng A.
```

Điều kiện cập nhật:

- Pin trên 50%.
- Không có event an ninh đang hoạt động.
- Đủ flash và RSSI đạt ngưỡng.

Các đợt triển khai:

```text
5 node canary → 10% → 30% → phần còn lại
```

Chờ ít nhất 30 phút giữa các đợt. Dừng nếu lỗi cập nhật vượt 2% hoặc tỷ lệ offline tăng trên 3%.

## 13. Use case 7: trại C mất 4G trong 18 giờ

Khi WAN mất:

```text
1. ESP32 và Wi-Fi LAN vẫn hoạt động.
2. Mosquitto và Local Rule Engine trên Gateway vẫn chạy.
3. Còi vẫn được điều khiển tại chỗ.
4. Telemetry tiếp tục được lưu vào SQLite và queue của Broker.
5. Audio nằm trong file cache.
6. Trung tâm tạm thời không nhận được dữ liệu mới.
7. Site được đánh dấu isolated, không gán nhầm tất cả node thành offline.
```

Khi WAN phục hồi:

```text
1. MQTT Bridge reconnect.
2. Gateway ưu tiên gửi event và state.
3. Telemetry tồn đọng được gửi bù với giới hạn 512 kbps/site.
4. Backend khử bản tin trùng.
5. Dashboard đánh dấu khoảng dữ liệu từng bị gián đoạn.
```

Hàng đợi được thiết kế 64 MiB, lớn hơn nhu cầu khoảng 32,89 MiB của kịch bản 18 giờ.

## 14. Online offline và isolated

- **Online:** thiết bị vẫn gửi telemetry hoặc heartbeat.
- **Offline:** thiết bị không còn gửi dữ liệu trong thời gian quy định.
- **Isolated:** Gateway tại trại còn hoạt động nhưng mất kết nối WAN với trung tâm.

Node:

- Publish retained birth `online` khi kết nối.
- Đặt Last Will retained `offline`.
- Gửi heartbeat mỗi 300 giây.
- Bị coi là offline sau khoảng 180 giây không có snapshot.

Trạng thái hiện tại nằm trong Redis; lịch sử trạng thái nằm trong PostgreSQL.

## 15. MQTT topic cần hiểu

Topic trung tâm có dạng:

```text
bee/{siteId}/{assetType}/{assetId}/{group}/{name}
```

Ví dụ:

```text
bee/site-c/hive/hive-023/cmd/audio-capture
```

Đọc từ trái sang phải:

```text
bee             hệ thống ong mật
site-c          trại C
hive            loại thiết bị là node thùng ong
hive-023        node của thùng số 23
cmd             nhóm command
audio-capture   yêu cầu ghi âm
```

Wildcard:

```text
+ = thay đúng một cấp
# = thay toàn bộ phần còn lại và phải nằm cuối filter
```

Ví dụ:

```text
hive/+/cmd/#
```

nghĩa là mọi command của mọi node hive trong một trại.

## 16. MQTT Bridge và prefix site

Mỗi trại có một Bridge riêng nối Mosquitto cục bộ với Mosquitto trung tâm.

```text
OUT: telemetry, event, state
IN:  cmd
```

Ví dụ khi gửi từ trại C:

```text
Local:   hive/hive-023/telemetry/snapshot
Central: bee/site-c/hive/hive-023/telemetry/snapshot
```

Bridge thêm prefix `bee/site-c/`. Chiều command thực hiện ngược lại và loại prefix khi đưa topic vào Broker cục bộ.

Không dùng `topic # both` vì có thể tạo vòng lặp và đưa command quay trở lại trung tâm.

Các điểm tròn gom dây trên sơ đồ chỉ để hình vẽ gọn hơn; chúng không phải thiết bị hoặc phần mềm thật.

## 17. QoS retained ACK và escalate

### QoS 1

Bản tin được giao ít nhất một lần nên có thể bị trùng. Hệ thống phải khử lặp bằng `seq`, `eventId` hoặc `commandId`.

### Retained

Broker giữ bản tin cuối của một topic. Chỉ `state/status` được retained để subscriber mới biết trạng thái cuối ngay lập tức.

Không retained `event` hoặc `cmd` vì cảnh báo và lệnh cũ không được tự phát lại.

### ACK

ACK là xác nhận người dùng đã nhận hoặc xử lý cảnh báo.

### Escalate

Nếu cảnh báo chưa được ACK đúng hạn, hệ thống gửi thêm kênh hoặc chuyển lên người có trách nhiệm cao hơn.

## 18. Bảo mật

- Node và Broker cục bộ xác thực bằng mTLS.
- Mỗi Bridge có chứng chỉ riêng theo site.
- TLS mã hóa dữ liệu qua mạng.
- ACL giới hạn topic được đọc hoặc ghi.
- Người dùng đăng nhập Backend và được phân quyền RBAC.
- Command Service ghi audit: ai gửi, gửi khi nào và đến thiết bị nào.
- Ứng dụng người dùng không được kết nối trực tiếp vào MQTT Broker.

Phân biệt:

```text
TLS/mTLS = xác thực và mã hóa kết nối
ACL      = giới hạn quyền đọc/ghi topic
RBAC     = giới hạn quyền của người dùng trên Backend
```

## 19. Vì sao kiến trúc cần Edge Gateway

Nếu mọi ESP32 kết nối trực tiếp Cloud:

- Mất 4G thì không bật còi được qua Cloud.
- Không có nơi lưu bền tại trại.
- 160 node phải duy trì kết nối Internet trực tiếp.
- OTA và audio tiêu tốn nhiều dữ liệu 4G.

Edge Gateway giải quyết bằng cách:

- Xử lý cảnh báo tại chỗ.
- Lưu dữ liệu khi mất WAN.
- Gom kết nối của các node.
- Tải firmware một lần rồi phân phối qua LAN.
- Cache audio trước khi upload.

## 20. Những con số nên nhớ

```text
52 - 47 - 61       số thùng tại A, B, C
160                tổng node thùng ong
166                tổng thiết bị quản lý
60 - 120 - 300     snapshot, acoustic feature, heartbeat
<2 giây            cảnh báo cục bộ
<15 giây           cảnh báo trung tâm khi WAN tốt
180 giây           node offline hoặc OTA rollback
18 giờ             kịch bản mất WAN
21 ngày            cache tại Gateway
64 MiB              hàng đợi bridge
512 kbps/site       tốc độ gửi bù
10 giây             audio capture
180 ngày            telemetry thô tại trung tâm
30 ngày             lưu audio
```

## 21. Cách trình bày sơ đồ trong khoảng ba phút

Bạn có thể trình bày theo thứ tự sau:

> Hệ thống có ba trại với tổng cộng 160 thùng ong. Mỗi thùng được gắn một node ESP32 gồm cảm biến nhiệt độ, độ ẩm, load cell, IMU, microphone và mạch đo pin. Các node gửi dữ liệu qua Wi-Fi AP đến Mosquitto chạy trên Edge Gateway của từng trại.

> Trên Gateway có Local Rule Engine để phát hiện nghiêng hoặc giảm khối lượng và bật còi trong dưới hai giây. Vì toàn bộ luồng này nằm tại trại nên mất 4G vẫn cảnh báo được. Gateway còn lưu dữ liệu trong 21 ngày và gửi bù khi mạng phục hồi.

> Ba Gateway kết nối đến Mosquitto trung tâm trên VPS bằng MQTT Bridge qua 4G và TLS. Bridge chỉ gửi telemetry, event, state lên và chỉ nhận command xuống; prefix site giúp tách dữ liệu và phân quyền ba trại.

> Ingest Consumer của Backend nhận dữ liệu, kiểm tra và khử trùng lặp rồi chia song song sang database, Central Rule Engine và Device Status Service. TimescaleDB lưu telemetry, PostgreSQL lưu sự kiện và audit, Redis giữ trạng thái tức thời, Object Storage lưu audio và firmware.

> Người dùng xem dữ liệu qua Dashboard và gửi lệnh qua API cùng Command Service. File audio và firmware đi bằng HTTPS thay vì MQTT. Notification Service gửi Push, SMS hoặc Email và theo dõi ACK của cảnh báo.

## 22. Các câu thầy có thể hỏi

### ESP32 có phải cảm biến không

Không. ESP32 là vi điều khiển đọc nhiều cảm biến và gửi dữ liệu.

### Gateway là gì

Là máy tính nhỏ tại trại, chạy Mosquitto, luật cục bộ, cache và Upload/OTA Agent.

### Tại sao mất 4G vẫn bật còi

Vì ESP32, Wi-Fi, Mosquitto, Rule Engine và còi đều nằm trong mạng LAN tại trại.

### Mosquitto trung tâm có phải server không

Mosquitto là phần mềm Broker chạy trên VPS/Cloud có public IP hoặc domain.

### Ingest Consumer là gì

Là chương trình Backend subscribe Mosquitto, kiểm tra, khử trùng lặp và phân phối dữ liệu.

### Rule Engine là gì

Là phần mềm kiểm tra luật `nếu - thì`; không nhất thiết là AI.

### Tại sao có Local Rule và Central Rule

Local Rule phản ứng nhanh và không phụ thuộc WAN; Central Rule dùng dữ liệu tổng hợp và lịch sử.

### Tại sao không gửi audio qua MQTT

Vì file lớn có thể chiếm hàng đợi và ảnh hưởng telemetry, event và command. Audio đi bằng HTTPS.

### Tại sao cần MQTT Bridge

Để nối Broker cục bộ và Broker trung tâm, chuyển đúng nhóm topic và giữ mỗi trại hoạt động độc lập khi WAN mất.

### Tại sao command không retained

Để node reconnect không thực hiện lại lệnh cũ.

### Điểm đặc biệt nhất của đề tài

Hệ thống kết hợp giám sát điều kiện tổ ong với phát hiện dịch chuyển, xử lý Edge khi mất WAN, lưu và gửi bù dữ liệu, audio theo yêu cầu và OTA an toàn.

## 23. Mô hình tư duy cuối cùng

Nếu quên chi tiết, hãy nhớ năm tầng:

```text
CẢM BIẾN
Node ESP32 đo dữ liệu
    ↓
MẠNG TẠI TRẠI
Wi-Fi AP chuyển dữ liệu
    ↓
EDGE
Gateway xử lý nhanh, bật còi và lưu tạm
    ↓
CLOUD
Mosquitto trung tâm, Backend và database
    ↓
NGƯỜI DÙNG
Dashboard, thông báo, ACK và command
```

Ba luồng quan trọng nhất:

```text
Dữ liệu: ESP32 → Gateway → Cloud → Dashboard
Cảnh báo: ESP32 → Local Rule → Còi + Cloud notification
Lệnh: Dashboard → Backend → Gateway → ESP32
```
