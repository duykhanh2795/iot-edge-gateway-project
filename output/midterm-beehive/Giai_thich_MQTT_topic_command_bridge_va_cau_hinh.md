# Giải thích MQTT topic command bridge và file cấu hình

Tài liệu này giải thích các khái niệm MQTT và phần cấu hình xuất hiện trong báo cáo hệ thống giám sát tổ ong.

## 1. MQTT hoạt động theo mô hình nào

MQTT có ba vai trò chính:

```text
Publisher → MQTT Broker → Subscriber
```

- **Publisher**: chương trình hoặc thiết bị gửi bản tin.
- **Broker**: phần mềm nhận bản tin rồi chuyển cho đúng subscriber. Hệ thống dùng Mosquitto.
- **Subscriber**: chương trình hoặc thiết bị đăng ký nhận một hoặc nhiều topic.

Ví dụ:

```text
ESP32 publish dữ liệu
→ Mosquitto cục bộ
→ Local Rule Engine đã subscribe nhận dữ liệu
```

MQTT Broker không tự hiểu nhiệt độ, cảnh báo hay lệnh. Nó chỉ chuyển bản tin dựa trên tên topic.

## 2. Topic là gì

Topic là địa chỉ logic của bản tin MQTT.

Ví dụ:

```text
hive/hive-023/telemetry/snapshot
```

Topic trên có năm cấp:

| Cấp | Giá trị | Ý nghĩa |
|---|---|---|
| 1 | `hive` | Loại tài sản là thùng ong |
| 2 | `hive-023` | Mã node cụ thể |
| 3 | `telemetry` | Nhóm dữ liệu đo định kỳ |
| 4 | `snapshot` | Tên loại bản tin |

Các cấp được phân tách bằng dấu `/`.

Topic không phải thư mục thật và cũng không phải URL. Nó chỉ là chuỗi ký tự để Broker định tuyến bản tin.

## 3. Topic tại trại và topic tại trung tâm

### Topic cục bộ tại trại C

```text
hive/hive-023/telemetry/snapshot
```

### Topic tương ứng tại trung tâm

```text
bee/site-c/hive/hive-023/telemetry/snapshot
```

MQTT Bridge thêm tiền tố `bee/site-c/` khi gửi dữ liệu từ trại C lên trung tâm.

| Nơi | Topic |
|---|---|
| Broker trại C | `hive/hive-023/telemetry/snapshot` |
| Broker trung tâm | `bee/site-c/hive/hive-023/telemetry/snapshot` |

Tiền tố site giúp trung tâm phân biệt dữ liệu của ba trại:

```text
bee/site-a/#
bee/site-b/#
bee/site-c/#
```

## 4. `+` trong MQTT có nghĩa là gì

`+` là wildcard thay cho **đúng một cấp topic**.

Ví dụ subscriber đăng ký:

```text
hive/+/telemetry/snapshot
```

Nó khớp với:

```text
hive/hive-001/telemetry/snapshot
hive/hive-023/telemetry/snapshot
hive/hive-061/telemetry/snapshot
```

Nhưng không khớp với:

```text
hive/hive-023/event/tilt
hive/hive-023/telemetry/acoustic/detail
```

Trong mẫu trên, `+` chỉ thay cho một cấp là `hive-001`, `hive-023` hoặc mã node khác.

Ví dụ tại trung tâm:

```text
bee/+/hive/+/state/status
```

Hai dấu `+` lần lượt thay cho:

1. Một `siteId`.
2. Một `hiveId`.

Topic này có thể nhận trạng thái của mọi node thùng ong tại mọi trại.

## 5. `#` trong MQTT có nghĩa là gì

`#` là wildcard thay cho **không, một hoặc nhiều cấp topic còn lại**.

Nó phải nằm ở cuối topic filter.

Ví dụ:

```text
hive/hive-023/telemetry/#
```

Nó khớp với:

```text
hive/hive-023/telemetry
hive/hive-023/telemetry/snapshot
hive/hive-023/telemetry/acoustic
hive/hive-023/telemetry/acoustic/detail
```

Ví dụ:

```text
bee/site-c/#
```

Topic filter này nhận toàn bộ nhánh của trại C.

### Phân biệt nhanh

```text
+  = đúng một cấp
#  = toàn bộ phần còn lại
```

| Topic filter | Khớp với gì |
|---|---|
| `hive/+/state/status` | Trạng thái của mọi hive, đúng cấu trúc bốn cấp |
| `hive/+/state/#` | Mọi loại state của mọi hive |
| `hive/#` | Mọi topic nằm dưới nhánh `hive` |
| `#` | Gần như tất cả topic trên Broker |

## 6. `cmd` là gì

`cmd` là viết tắt của **command**, tức nhóm topic dùng để gửi lệnh.

`cmd` không phải từ khóa đặc biệt của MQTT. Đây chỉ là tên do người thiết kế hệ thống quy ước.

Ví dụ:

```text
hive/hive-023/cmd/config
hive/hive-023/cmd/audio-capture
hive/hive-023/cmd/restart
hive/hive-023/cmd/ota
alarm/siren-01/cmd/set
```

ESP32 `hive-023` subscribe:

```text
hive/hive-023/cmd/#
```

Do đó nó nhận tất cả lệnh dành cho chính nó, nhưng không nhận lệnh của `hive-024`.

### MQTT có tự thực hiện command không

Không. MQTT chỉ chuyển payload đến ESP32.

Code trên ESP32 phải đọc topic và tự thực hiện hành động:

```text
Nhận .../cmd/audio-capture → ghi âm 10 giây
Nhận .../cmd/config        → thay đổi chu kỳ hoặc ngưỡng
Nhận .../cmd/restart       → khởi động lại
Nhận .../cmd/ota           → bắt đầu cập nhật firmware
```

## 7. Payload của command

Topic cho biết lệnh đi đâu và thuộc loại gì. Payload chứa tham số chi tiết.

Ví dụ topic:

```text
bee/site-c/hive/hive-023/cmd/audio-capture
```

Payload:

```json
{
  "commandId": "cmd-20260921-001",
  "durationSeconds": 10,
  "expiresAt": "2026-09-21T10:05:00Z"
}
```

- `commandId`: nhận diện lệnh và chống thực hiện lặp.
- `durationSeconds`: thời gian ghi âm.
- `expiresAt`: lệnh quá hạn thì node không thực hiện.

Command dùng QoS 1 nhưng không retained.

## 8. Telemetry event state và cmd khác nhau thế nào

| Nhóm | Nội dung | Hướng chính | Retained |
|---|---|---|---|
| `telemetry` | Dữ liệu đo định kỳ | Node lên trung tâm | Không |
| `event` | Sự kiện bất thường cần xử lý | Node lên trung tâm | Không |
| `state` | Trạng thái hiện tại | Node lên trung tâm | Có với `state/status` |
| `cmd` | Lệnh điều khiển | Trung tâm xuống node | Không |

Ví dụ:

```text
telemetry/snapshot  → nhiệt độ, độ ẩm, cân nặng
event/tilt          → thùng bị nghiêng
state/status        → online, firmware, pin
cmd/audio-capture   → yêu cầu node ghi âm
```

## 9. QoS 1 có nghĩa là gì

QoS 1 bảo đảm bản tin được giao **ít nhất một lần**.

```text
Publisher gửi bản tin
→ Broker nhận
→ Broker trả PUBACK
```

Nếu Publisher chưa nhận PUBACK, nó có thể gửi lại. Vì vậy cùng một bản tin có thể xuất hiện hai lần.

Hệ thống xử lý trùng bằng:

- Telemetry: `deviceId + seq`.
- Event: `eventId`.
- Command: `commandId`.

## 10. Retained có nghĩa là gì

Khi một bản tin được publish với retained, Broker giữ lại bản tin cuối cùng của topic.

Subscriber mới kết nối sẽ nhận ngay giá trị cuối đó.

Phù hợp với:

```text
state/status
```

Ví dụ Dashboard vừa mở có thể biết node đang online hay offline mà không cần đợi bản tin kế tiếp.

Không được retained:

```text
event/#
cmd/#
```

Nếu retained `cmd/ota`, một node vừa reconnect có thể chạy lại chiến dịch OTA cũ. Nếu retained `event/tilt`, Dashboard mới kết nối có thể báo lại một sự kiện cũ.

## 11. MQTT Bridge là gì

MQTT Bridge là chức năng của Mosquitto dùng để nối hai Broker.

```text
Mosquitto trại C
       ⇅ MQTT Bridge qua 4G/TLS
Mosquitto trung tâm
```

Bridge thực hiện hai hướng:

```text
OUT: telemetry, event, state từ trại lên trung tâm
IN:  cmd từ trung tâm xuống trại
```

Mỗi trại có một kết nối bridge riêng.

## 12. Vì sao không dùng `# both`

Cấu hình sau rất nguy hiểm:

```text
topic # both
```

Nó cho phép gần như mọi topic đi cả hai chiều. Một bản tin có thể:

1. Đi từ trại lên trung tâm.
2. Bị trung tâm gửi lại xuống trại.
3. Trại lại gửi nó lên lần nữa.
4. Quá trình lặp tiếp tục.

Hậu quả:

- Topic bị lặp tiền tố.
- Message rate tăng nhanh.
- Broker tốn CPU và RAM.
- Database nhận nhiều bản sao.
- Command có nguy cơ bị thực hiện nhiều lần.

Thiết kế hiện tại dùng allowlist một chiều:

```text
telemetry/event/state → out
cmd                   → in
```

## 13. Phân biệt các file cấu hình

Phần phụ lục của báo cáo trình bày cấu hình trong cùng một khung để dễ đọc, nhưng khi triển khai thật nên tách thành:

```text
/etc/mosquitto/mosquitto.conf
/etc/mosquitto/conf.d/bridge-site-c.conf
/etc/mosquitto/acl
```

- `mosquitto.conf`: cấu hình chung của Broker.
- `bridge-site-c.conf`: cấu hình kết nối Broker trại C với Broker trung tâm.
- `acl`: quy định tài khoản nào được đọc hoặc ghi topic nào.

## 14. Giải thích cấu hình lưu trữ của Mosquitto

```conf
persistence true
```

Cho phép Mosquitto lưu session, retained message và hàng đợi xuống đĩa. Broker restart không làm mất toàn bộ trạng thái cần khôi phục.

```conf
persistence_location /var/lib/mosquitto/
```

Thư mục lưu file persistence.

```conf
autosave_interval 60
```

Mosquitto định kỳ ghi trạng thái persistence xuống đĩa mỗi 60 giây.

```conf
max_queued_messages 160000
```

Giới hạn số bản tin nằm trong hàng đợi là 160.000 message.

```conf
max_queued_bytes 67108864
```

Giới hạn dung lượng hàng đợi là 67.108.864 byte, tương đương 64 MiB.

```conf
queue_qos0_messages false
```

Không xếp hàng bản tin QoS 0 khi kết nối bridge bị mất. Dung lượng được ưu tiên cho bản tin QoS 1 quan trọng hơn.

## 15. Giải thích cấu hình MQTT Bridge

```conf
connection central-site-c
```

Tạo một cấu hình bridge có tên `central-site-c`.

```conf
address mqtt-center.example:8883
```

Địa chỉ Mosquitto trung tâm. Cổng 8883 thường được dùng cho MQTT qua TLS.

Trong triển khai thật, `mqtt-center.example` được thay bằng domain thật của VPS hoặc Cloud.

```conf
remote_clientid bridge-site-c
```

Client ID mà Bridge của trại C dùng khi kết nối đến Mosquitto trung tâm.

```conf
bridge_protocol_version mqttv50
```

Bridge sử dụng MQTT 5.0.

```conf
cleansession false
```

Yêu cầu giữ session để kết nối lại có thể tiếp tục nhận các bản tin QoS đã được xếp hàng.

```conf
start_type automatic
```

Mosquitto tự khởi động kết nối bridge khi Broker chạy.

```conf
restart_timeout 5 120
```

Khi mất kết nối, Bridge reconnect theo backoff từ 5 đến tối đa 120 giây, tránh kết nối lại liên tục khi 4G chập chờn.

```conf
try_private true
```

Bridge cố gắng thông báo cho Broker bên kia rằng đây là kết nối bridge. Tùy chọn này hỗ trợ quản lý kết nối nhưng không thay thế việc giới hạn topic bằng allowlist.

## 16. Giải thích chứng chỉ TLS của Bridge

```conf
bridge_cafile /etc/mosquitto/ca.crt
bridge_certfile /etc/mosquitto/site-c.crt
bridge_keyfile /etc/mosquitto/site-c.key
```

- `bridge_cafile`: chứng chỉ CA dùng để kiểm tra chứng chỉ của Mosquitto trung tâm.
- `bridge_certfile`: chứng chỉ riêng của Bridge trại C.
- `bridge_keyfile`: khóa riêng tương ứng với chứng chỉ trại C.

Mosquitto trung tâm kiểm tra chứng chỉ để xác định đây đúng là Bridge của site C.

Khóa riêng `.key` phải được bảo vệ và không được gửi ra ngoài.

## 17. Cú pháp một dòng `topic` của Bridge

Cú pháp tổng quát:

```conf
topic <pattern> <direction> <qos> <local-prefix> <remote-prefix>
```

Trong đó:

| Phần | Ý nghĩa |
|---|---|
| `pattern` | Topic filter cần chuyển |
| `direction` | `out`, `in` hoặc `both` |
| `qos` | QoS dùng trên bridge |
| `local-prefix` | Tiền tố phía Broker cục bộ |
| `remote-prefix` | Tiền tố phía Broker trung tâm |

## 18. Đọc một dòng outbound

```conf
topic hive/+/telemetry/# out 1 "" bee/site-c/
```

Đọc từ trái sang phải:

1. Chọn mọi telemetry của mọi hive.
2. `out`: gửi từ Broker trại C lên Broker trung tâm.
3. `1`: sử dụng QoS 1.
4. `""`: không thêm tiền tố tại phía local.
5. `bee/site-c/`: thêm tiền tố này tại phía trung tâm.

Kết quả ánh xạ:

```text
Local:
hive/hive-023/telemetry/snapshot

Central:
bee/site-c/hive/hive-023/telemetry/snapshot
```

Các dòng outbound trong báo cáo:

```conf
topic hive/+/telemetry/# out 1 "" bee/site-c/
topic hive/+/event/# out 1 "" bee/site-c/
topic hive/+/state/# out 1 "" bee/site-c/
topic weather/+/telemetry/# out 1 "" bee/site-c/
topic gateway/+/state/# out 1 "" bee/site-c/
```

## 19. Đọc một dòng inbound

```conf
topic hive/+/cmd/# in 1 "" bee/site-c/
```

Đọc từ trái sang phải:

1. Chọn nhánh command của mọi hive.
2. `in`: nhận từ Mosquitto trung tâm xuống Broker trại C.
3. Dùng QoS 1.
4. Không thêm local prefix.
5. Ở trung tâm, lệnh phải nằm dưới `bee/site-c/`.

Kết quả ánh xạ:

```text
Central:
bee/site-c/hive/hive-023/cmd/audio-capture

Local:
hive/hive-023/cmd/audio-capture
```

Các dòng inbound:

```conf
topic hive/+/cmd/# in 1 "" bee/site-c/
topic alarm/+/cmd/# in 1 "" bee/site-c/
```

## 20. File bridge hoàn chỉnh dùng trong báo cáo

```conf
# /etc/mosquitto/conf.d/bridge-site-c.conf

persistence true
persistence_location /var/lib/mosquitto/
autosave_interval 60
max_queued_messages 160000
max_queued_bytes 67108864
queue_qos0_messages false

connection central-site-c
address mqtt-center.example:8883
remote_clientid bridge-site-c
bridge_protocol_version mqttv50
cleansession false
start_type automatic
restart_timeout 5 120
try_private true

bridge_cafile /etc/mosquitto/ca.crt
bridge_certfile /etc/mosquitto/site-c.crt
bridge_keyfile /etc/mosquitto/site-c.key

topic hive/+/telemetry/# out 1 "" bee/site-c/
topic hive/+/event/# out 1 "" bee/site-c/
topic hive/+/state/# out 1 "" bee/site-c/
topic weather/+/telemetry/# out 1 "" bee/site-c/
topic gateway/+/state/# out 1 "" bee/site-c/

topic hive/+/cmd/# in 1 "" bee/site-c/
topic alarm/+/cmd/# in 1 "" bee/site-c/
```

Trại A và B dùng cấu hình tương tự, chỉ thay:

```text
site-c → site-a hoặc site-b
bridge-site-c → bridge-site-a hoặc bridge-site-b
```

## 21. ACL là gì

ACL là Access Control List, tức danh sách quyền truy cập topic.

ACL quy định:

- Tài khoản nào được publish.
- Tài khoản nào được subscribe.
- Được truy cập chính xác những nhánh topic nào.

ACL không phải code ESP32 và cũng không phải cấu hình Bridge. Nó là file quyền được Mosquitto đọc.

Trong `mosquitto.conf` cần trỏ đến file ACL:

```conf
acl_file /etc/mosquitto/acl
```

## 22. Giải thích ACL của một node

```conf
user hive-023
topic write hive/hive-023/telemetry/#
topic write hive/hive-023/event/#
topic write hive/hive-023/state/#
topic read  hive/hive-023/cmd/#
```

Ý nghĩa:

- Tài khoản `hive-023` được ghi telemetry của chính nó.
- Được ghi event của chính nó.
- Được ghi state của chính nó.
- Chỉ được đọc command dành cho chính nó.

Nó không có quyền:

```text
Đọc command của hive-024
Ghi dữ liệu giả dưới tên hive-024
Đọc toàn bộ dữ liệu của trại
```

## 23. Publish và subscribe cụ thể

### ESP32 publish snapshot

```text
Topic: hive/hive-023/telemetry/snapshot
Payload: { temperature, humidity, weight, tilt, battery, seq }
```

### Local Rule Engine subscribe event

```text
hive/+/event/#
```

Rule Engine nhận event của mọi node trong trại.

### ESP32 subscribe command

```text
hive/hive-023/cmd/#
```

Node chỉ nhận command của chính nó.

### Ingest Consumer trung tâm subscribe dữ liệu

```text
bee/+/hive/+/telemetry/#
bee/+/hive/+/event/#
bee/+/hive/+/state/#
bee/+/weather/+/telemetry/#
bee/+/gateway/+/state/#
```

## 24. Một hành trình đầy đủ của telemetry

```text
1. ESP32 hive-023 publish:
   hive/hive-023/telemetry/snapshot

2. Mosquitto cục bộ nhận bản tin.

3. Bridge khớp dòng:
   topic hive/+/telemetry/# out 1 "" bee/site-c/

4. Bridge thêm prefix và gửi lên:
   bee/site-c/hive/hive-023/telemetry/snapshot

5. Mosquitto trung tâm chuyển bản tin cho Ingest Consumer.

6. Ingest Consumer kiểm tra, khử trùng lặp và chia dữ liệu cho:
   TimescaleDB, Central Rule Engine và Device Status Service.
```

## 25. Một hành trình đầy đủ của command

```text
1. Người dùng chọn Thu âm node hive-023.

2. Command Service publish:
   bee/site-c/hive/hive-023/cmd/audio-capture

3. Bridge site C khớp dòng:
   topic hive/+/cmd/# in 1 "" bee/site-c/

4. Bridge bỏ prefix site và tạo topic local:
   hive/hive-023/cmd/audio-capture

5. Mosquitto cục bộ chuyển lệnh cho hive-023.

6. ESP32 đọc payload, kiểm tra commandId và expiresAt.

7. ESP32 ghi âm 10 giây nếu lệnh hợp lệ.
```

## 26. Những câu dễ bị giảng viên hỏi

### Tại sao dùng `+` thay vì `#`

`+` giới hạn đúng một cấp nên kiểm soát cấu trúc topic chặt hơn. `#` nhận toàn bộ phần còn lại và dễ cấp quyền quá rộng nếu dùng sai.

### Tại sao command không retained

Vì node reconnect có thể nhận và thực hiện lại một lệnh cũ đã hết hạn.

### Tại sao dùng QoS 1

Vì chấp nhận khả năng nhận trùng để giảm nguy cơ mất telemetry, event hoặc command. Backend và node khử lặp bằng ID.

### Tại sao cần prefix site

Để tránh trùng tên, phân quyền từng trại và biết chính xác dữ liệu đến từ đâu.

### Tại sao không bridge `# both`

Vì có thể gây vòng lặp, gửi lệnh ngược trở lại và làm tăng bản tin ngoài kiểm soát.

### ACL khác TLS thế nào

- TLS/mTLS xác định ai đang kết nối và mã hóa đường truyền.
- ACL xác định tài khoản đó được đọc hoặc ghi topic nào.

Hai cơ chế phải được sử dụng cùng nhau.

## 27. Bảng nhớ nhanh

| Ký hiệu hoặc từ | Nghĩa |
|---|---|
| `/` | Phân tách các cấp topic |
| `+` | Khớp đúng một cấp |
| `#` | Khớp toàn bộ các cấp còn lại |
| `cmd` | Nhóm lệnh do hệ thống quy ước |
| `out` | Bridge gửi từ local lên central |
| `in` | Bridge nhận từ central xuống local |
| `both` | Hai chiều, không dùng trong thiết kế này |
| QoS 1 | Giao ít nhất một lần, có thể trùng |
| retained | Broker giữ bản tin cuối của topic |
| ACL | Quyền đọc và ghi topic |
| TLS | Mã hóa kết nối |
| mTLS | Hai phía xác thực nhau bằng chứng chỉ |
| Bridge | Kết nối và chuyển topic giữa hai Broker |
