# Danh mục topic MQTT đầy đủ của hệ thống giám sát tổ ong

Đây là danh mục topic chuẩn dùng để học và đối chiếu khi trình bày. Bảng “Ví dụ topic thật trong hệ thống” ở file Word chỉ đưa ra ví dụ, không phải toàn bộ danh mục.

## 1. Quy ước cấu trúc topic

### Tại Broker cục bộ của mỗi trại

```text
{assetType}/{assetId}/{group}/{name}
```

Ví dụ:

```text
hive/hive-023/telemetry/snapshot
```

### Tại Mosquitto trung tâm

```text
bee/{siteId}/{assetType}/{assetId}/{group}/{name}
```

Ví dụ:

```text
bee/site-c/hive/hive-023/telemetry/snapshot
```

MQTT Bridge tự thêm prefix `bee/site-c/` khi gửi từ trại C lên trung tâm và loại prefix này khi nhận command từ trung tâm xuống trại C.

## 2. Ý nghĩa từng cấp

| Cấp | Ví dụ | Ý nghĩa |
|---|---|---|
| Tenant | `bee` | Hệ thống giám sát ong mật |
| Site | `site-a`, `site-b`, `site-c` | Trại ong |
| Asset type | `hive`, `weather`, `gateway`, `alarm` | Loại thiết bị hoặc tài sản |
| Asset ID | `hive-023`, `weather-01`, `edge-01`, `siren-01` | Thiết bị cụ thể |
| Group | `telemetry`, `event`, `state`, `cmd` | Nhóm bản tin |
| Name | `snapshot`, `tilt`, `status`, `ota` | Loại bản tin cụ thể |

## 3. Tám nhóm topic cấp cao

```text
# Từ trại lên trung tâm
bee/+/hive/+/telemetry/#
bee/+/hive/+/event/#
bee/+/hive/+/state/#
bee/+/weather/+/telemetry/#
bee/+/gateway/+/state/#
bee/+/gateway/+/event/#

# Từ trung tâm xuống trại
bee/+/hive/+/cmd/#
bee/+/alarm/+/cmd/#
```

Trong đó:

- `+` thay cho đúng một cấp topic.
- `#` thay cho toàn bộ các cấp còn lại và phải nằm cuối filter.

## 4. Danh mục topic node thùng ong gửi định kỳ

### 4.1. Snapshot cảm biến

```text
Local:   hive/{hiveId}/telemetry/snapshot
Central: bee/{siteId}/hive/{hiveId}/telemetry/snapshot
```

Ví dụ:

```text
bee/site-a/hive/hive-017/telemetry/snapshot
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | ESP32 node thùng ong |
| Subscriber local | Local Rule Engine, dịch vụ lưu SQLite |
| Subscriber Cloud | Ingest Consumer |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không |
| Chu kỳ | 60 giây |

Payload minh họa:

```json
{
  "deviceId": "hive-017",
  "seq": 1054,
  "temperature": 34.2,
  "humidity": 68.0,
  "weight": 42.6,
  "tilt": 2.1,
  "battery": 81,
  "timestamp": "2026-09-21T10:30:00Z"
}
```

### 4.2. Đặc trưng âm thanh

```text
Local:   hive/{hiveId}/telemetry/acoustic
Central: bee/{siteId}/hive/{hiveId}/telemetry/acoustic
```

Ví dụ:

```text
bee/site-b/hive/hive-031/telemetry/acoustic
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | ESP32 node thùng ong |
| Subscriber | Ingest Consumer và dịch vụ phân tích |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không |
| Chu kỳ | 120 giây |

Topic này chỉ mang đặc trưng âm thanh nhỏ, không chứa file audio thô.

## 5. Danh mục event của node thùng ong

### 5.1. Thùng bị nghiêng hoặc di chuyển

```text
Local:   hive/{hiveId}/event/tilt
Central: bee/{siteId}/hive/{hiveId}/event/tilt
```

Ví dụ:

```text
bee/site-c/hive/hive-023/event/tilt
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | ESP32 hoặc Local Rule Engine |
| Subscriber local | Local Rule Engine |
| Subscriber Cloud | Ingest Consumer và Central Rule Engine |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không |
| Chu kỳ | Gửi ngay khi xảy ra |

### 5.2. Khối lượng giảm bất thường

```text
Local:   hive/{hiveId}/event/weight-drop
Central: bee/{siteId}/hive/{hiveId}/event/weight-drop
```

Ví dụ:

```text
bee/site-c/hive/hive-023/event/weight-drop
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | ESP32 hoặc Local Rule Engine |
| Subscriber local | Local Rule Engine |
| Subscriber Cloud | Ingest Consumer và Central Rule Engine |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không |
| Chu kỳ | Gửi ngay khi xảy ra |

Event không retained vì subscriber mới không được hiểu nhầm một sự kiện cũ là sự cố đang diễn ra.

## 6. Danh mục state của node thùng ong

### 6.1. Trạng thái hoạt động

```text
Local:   hive/{hiveId}/state/status
Central: bee/{siteId}/hive/{hiveId}/state/status
```

Ví dụ:

```text
bee/site-a/hive/hive-017/state/status
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | ESP32; Broker publish LWT khi mất kết nối đột ngột |
| Subscriber | Device Status Service |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Có |

Payload có thể chứa:

```json
{
  "deviceId": "hive-017",
  "status": "online",
  "firmwareVersion": "1.2.0",
  "battery": 81,
  "rssi": -62,
  "timestamp": "2026-09-21T10:30:00Z"
}
```

Birth message publish `online`; Last Will publish `offline`. Retained giúp subscriber vừa kết nối nhận ngay trạng thái MQTT cuối cùng.

### 6.2. Kết quả và phiên bản firmware

```text
Local:   hive/{hiveId}/state/firmware
Central: bee/{siteId}/hive/{hiveId}/state/firmware
```

Ví dụ:

```text
bee/site-a/hive/hive-017/state/firmware
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | ESP32 sau quá trình OTA |
| Subscriber | Ingest Consumer, Device Status Service và OTA Backend |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không trong thiết kế hiện tại |

Payload có thể gồm `version`, `result`, `bootCount`, `commandId` và `timestamp`.

Chỉ `state/status` được retained; không mặc định retained toàn bộ nhánh `state/#`.

## 7. Danh mục command gửi đến node thùng ong

Tất cả command có đặc điểm chung:

| Thuộc tính | Giá trị |
|---|---|
| Publisher | Command Service trên Cloud |
| Subscriber | ESP32 được chỉ định |
| Hướng Bridge | `in` |
| QoS | 1 |
| Retained | Không |
| Trường bắt buộc | `commandId`, `expiresAt` |

### 7.1. Thay đổi cấu hình

```text
Local:   hive/{hiveId}/cmd/config
Central: bee/{siteId}/hive/{hiveId}/cmd/config
```

Ví dụ:

```text
bee/site-b/hive/hive-031/cmd/config
```

Dùng để đổi chu kỳ gửi, ngưỡng cảnh báo hoặc cấu hình được cho phép.

### 7.2. Hiệu chuẩn cân

```text
Local:   hive/{hiveId}/cmd/calibrate
Central: bee/{siteId}/hive/{hiveId}/cmd/calibrate
```

Dùng để yêu cầu node thực hiện quy trình hiệu chuẩn load cell/HX711.

### 7.3. Thu audio theo yêu cầu

```text
Local:   hive/{hiveId}/cmd/audio-capture
Central: bee/{siteId}/hive/{hiveId}/cmd/audio-capture
```

Ví dụ:

```text
bee/site-b/hive/hive-031/cmd/audio-capture
```

Payload minh họa:

```json
{
  "commandId": "cmd-20260921-001",
  "durationSeconds": 10,
  "expiresAt": "2026-09-21T10:05:00Z"
}
```

MQTT chỉ chuyển lệnh. File audio được truyền qua LAN và HTTPS, không nằm trong payload MQTT.

### 7.4. Restart node

```text
Local:   hive/{hiveId}/cmd/restart
Central: bee/{siteId}/hive/{hiveId}/cmd/restart
```

Node chỉ restart nếu command còn hạn và `commandId` chưa được xử lý.

### 7.5. Cập nhật OTA

```text
Local:   hive/{hiveId}/cmd/ota
Central: bee/{siteId}/hive/{hiveId}/cmd/ota
```

Payload hoặc manifest tham chiếu chứa `version`, URL HTTPS, SHA-256, chữ ký Ed25519 và `expiresAt`.

## 8. Topic của weather node

### Weather snapshot

```text
Local:   weather/{weatherId}/telemetry/snapshot
Central: bee/{siteId}/weather/{weatherId}/telemetry/snapshot
```

Ví dụ:

```text
bee/site-c/weather/weather-01/telemetry/snapshot
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | Weather node ESP32 |
| Subscriber | Ingest Consumer |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không |
| Chu kỳ | 60 giây |

Payload tối thiểu gồm nhiệt độ và độ ẩm ngoài trời; có thể mở rộng ánh sáng hoặc mưa nếu phần cứng được bổ sung.

## 9. Topic của Edge Gateway

### 9.1. Trạng thái Gateway

```text
Local:   gateway/{gatewayId}/state/status
Central: bee/{siteId}/gateway/{gatewayId}/state/status
```

Ví dụ:

```text
bee/site-c/gateway/edge-01/state/status
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | Dịch vụ trạng thái trên Edge Gateway |
| Subscriber | Ingest Consumer và Device Status Service |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Có thể retained cho trạng thái cuối |

Payload có thể chứa trạng thái Gateway, dung lượng đĩa, tình trạng queue, phiên bản phần mềm và thời gian hoạt động.

### 9.2. Dữ liệu bị giảm mẫu

```text
Local:   gateway/{gatewayId}/event/data-degraded
Central: bee/{siteId}/gateway/{gatewayId}/event/data-degraded
```

Ví dụ:

```text
bee/site-c/gateway/edge-01/event/data-degraded
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher | Edge Gateway |
| Subscriber | Ingest Consumer, Central Rule Engine và Dashboard Backend |
| Hướng Bridge | `out` |
| QoS | 1 |
| Retained | Không |

Payload ghi thời gian bắt đầu, kết thúc, loại dữ liệu đã giảm mẫu và số message đã bỏ.

Topic này được mô tả trong nội dung báo cáo nhưng đang thiếu trong bảng đăng ký và cấu hình Bridge của file Word.

## 10. Topic điều khiển còi

```text
Local:   alarm/{sirenId}/cmd/set
Central: bee/{siteId}/alarm/{sirenId}/cmd/set
```

Ví dụ:

```text
bee/site-c/alarm/siren-01/cmd/set
```

| Thuộc tính | Giá trị |
|---|---|
| Publisher local | Local Rule Engine |
| Publisher Cloud | Command Service nếu người có quyền điều khiển từ xa |
| Subscriber | Bộ điều khiển còi |
| Hướng Bridge | `in` khi lệnh đến từ Cloud |
| QoS | 1 |
| Retained | Không |

Payload minh họa:

```json
{
  "commandId": "alarm-20260921-001",
  "value": "on",
  "expiresAt": "2026-09-21T10:05:00Z"
}
```

Không retained vì còi không được tự bật lại bởi một command cũ sau khi reconnect.

## 11. Bảng đăng ký topic hoàn chỉnh

| Mẫu topic local | Nhóm | Hướng | QoS | Retained |
|---|---|---|---:|---|
| `hive/+/telemetry/snapshot` | telemetry | out | 1 | Không |
| `hive/+/telemetry/acoustic` | telemetry | out | 1 | Không |
| `hive/+/event/tilt` | event | out | 1 | Không |
| `hive/+/event/weight-drop` | event | out | 1 | Không |
| `hive/+/state/status` | state | out | 1 | Có |
| `hive/+/state/firmware` | state | out | 1 | Không |
| `weather/+/telemetry/snapshot` | telemetry | out | 1 | Không |
| `gateway/+/state/status` | state | out | 1 | Có thể retained |
| `gateway/+/event/data-degraded` | event | out | 1 | Không |
| `hive/+/cmd/config` | cmd | in | 1 | Không |
| `hive/+/cmd/calibrate` | cmd | in | 1 | Không |
| `hive/+/cmd/audio-capture` | cmd | in | 1 | Không |
| `hive/+/cmd/restart` | cmd | in | 1 | Không |
| `hive/+/cmd/ota` | cmd | in | 1 | Không |
| `alarm/+/cmd/set` | cmd | in | 1 | Không |

## 12. Cấu hình Bridge cần dùng

### Outbound từ trại C lên trung tâm

```conf
topic hive/+/telemetry/# out 1 "" bee/site-c/
topic hive/+/event/# out 1 "" bee/site-c/
topic hive/+/state/# out 1 "" bee/site-c/
topic weather/+/telemetry/# out 1 "" bee/site-c/
topic gateway/+/state/# out 1 "" bee/site-c/
topic gateway/+/event/# out 1 "" bee/site-c/
```

### Inbound từ trung tâm xuống trại C

```conf
topic hive/+/cmd/# in 1 "" bee/site-c/
topic alarm/+/cmd/# in 1 "" bee/site-c/
```

Dòng cần bổ sung so với file Word hiện tại:

```conf
topic gateway/+/event/# out 1 "" bee/site-c/
```

## 13. Subscription và ACL của Backend Ingest

Ingest Consumer cần subscribe:

```text
bee/+/hive/+/telemetry/#
bee/+/hive/+/event/#
bee/+/hive/+/state/#
bee/+/weather/+/telemetry/#
bee/+/gateway/+/state/#
bee/+/gateway/+/event/#
```

ACL đọc tương ứng:

```conf
user backend-ingest
topic read bee/+/hive/+/telemetry/#
topic read bee/+/hive/+/event/#
topic read bee/+/hive/+/state/#
topic read bee/+/weather/+/telemetry/#
topic read bee/+/gateway/+/state/#
topic read bee/+/gateway/+/event/#
```

ACL ghi của Command Service:

```conf
user backend-command
topic write bee/+/hive/+/cmd/#
topic write bee/+/alarm/+/cmd/#
```

## 14. ACL của một node thùng ong

Ví dụ node `hive-023` tại Broker cục bộ:

```conf
user hive-023
topic write hive/hive-023/telemetry/#
topic write hive/hive-023/event/#
topic write hive/hive-023/state/#
topic read  hive/hive-023/cmd/#
```

Node này không được đọc command hoặc ghi dữ liệu dưới ID của node khác.

## 15. Topic nào retained và topic nào không

```text
Retained:
- hive/+/state/status
- gateway/+/state/status nếu cần khôi phục trạng thái cuối ngay

Không retained:
- telemetry/#
- event/#
- cmd/#
- hive/+/state/firmware trong thiết kế hiện tại
```

Quy tắc nhớ:

```text
Trạng thái hiện tại → có thể retained
Dữ liệu lịch sử     → lưu database, không retained
Sự kiện một lần     → không retained
Command một lần     → không retained
```

## 16. Command ACK và kết quả thực thi

QoS 1 chỉ xác nhận Broker đã nhận bản tin; nó không chứng minh ESP32 đã thực hiện command thành công.

Trong thiết kế hiện tại:

- OTA báo kết quả qua `hive/{hiveId}/state/firmware`.
- Command được Backend theo dõi bằng `commandId`, `expiresAt` và audit trong PostgreSQL.

Nếu triển khai thực tế cần một ACK ứng dụng chung cho mọi command, có thể bổ sung:

```text
Local:   hive/{hiveId}/event/command-result
Central: bee/{siteId}/hive/{hiveId}/event/command-result
```

Topic này là phần mở rộng khuyến nghị, chưa phải topic bắt buộc trong báo cáo hiện tại. Nó vẫn được bao phủ bởi mẫu `hive/+/event/#`.

## 17. Những điểm chưa hoàn chỉnh trong file Word hiện tại

1. Bảng 3.2 chỉ là bảng ví dụ nên không liệt kê mọi topic; điều này không sai nếu giữ đúng tiêu đề “Ví dụ topic thật”.
2. Bảng đăng ký topic chưa nêu riêng `gateway/+/state/#` và `gateway/+/event/#`.
3. Cấu hình Bridge đã có `gateway/+/state/#` nhưng thiếu `gateway/+/event/#`.
4. ACL của Backend Ingest thiếu quyền đọc `bee/+/gateway/+/event/#`.
5. Các command `calibrate` và `restart` được nhắc trong yêu cầu nhưng chưa có dòng ví dụ riêng trong bảng topic.

Danh mục trong file này là phiên bản đầy đủ và nhất quán hơn để dùng khi học hoặc cập nhật báo cáo.

## 18. Cách trả lời ngắn khi thầy hỏi

> Hệ thống có tám nhóm topic cấp cao. Sáu nhóm đưa telemetry, event và state của hive, weather và gateway từ trại lên trung tâm; hai nhóm đưa command cho hive và còi từ trung tâm xuống trại. Bridge tự thêm prefix `bee/site-x/`, QoS dùng mức 1, chỉ topic trạng thái hiện tại được retained, còn telemetry, event và command không retained.
