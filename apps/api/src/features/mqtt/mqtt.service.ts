import { Injectable, Logger, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import mqtt, { MqttClient } from 'mqtt';
import { RelayStatus } from '../../common/enums/relay-status.enum';
import { buildControlTopic, extractDeviceIdFromTelemetryTopic } from '../../common/utils/topic.util';
import { DevicesService } from '../devices/devices.service';
import { TelemetryService } from '../telemetry/telemetry.service';
import { parseTelemetryPayload } from './mqtt-payload.parser';

@Injectable()
export class MqttService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(MqttService.name);
  private client: MqttClient | null = null;

  constructor(
    private readonly config: ConfigService,
    private readonly telemetryService: TelemetryService,
    private readonly devicesService: DevicesService,
  ) {}

  onModuleInit(): void {
    const mqttUrl = this.config.get<string>('MQTT_URL', 'mqtt://localhost:1883');
    const telemetryTopic = this.config.get<string>('MQTT_TELEMETRY_TOPIC', 'iot/devices/+/telemetry');

    this.client = mqtt.connect(mqttUrl, {
      clientId: `iot-api-${process.pid}`,
      reconnectPeriod: 3000,
    });

    this.client.on('connect', () => {
      this.logger.log(`Connected to MQTT broker at ${mqttUrl}`);
      this.client?.subscribe(telemetryTopic);
    });

    this.client.on('message', (topic, payload) => {
      void this.handleTelemetryMessage(topic, payload);
    });

    this.client.on('error', (error) => {
      this.logger.error(`MQTT error: ${error.message}`);
    });
  }

  onModuleDestroy(): void {
    this.client?.end();
  }

  async publishRelayCommand(deviceId: string, relayStatus: RelayStatus): Promise<void> {
    const topic = buildControlTopic(deviceId);
    await this.publish(topic, relayStatus);
    await this.devicesService.updateRelayStatus(deviceId, relayStatus);
  }

  private async handleTelemetryMessage(topic: string, payloadBuffer: Buffer): Promise<void> {
    const payload = parseTelemetryPayload(payloadBuffer);
    if (!payload) {
      this.logger.warn(`Ignored invalid telemetry payload on topic ${topic}`);
      return;
    }

    const deviceId = extractDeviceIdFromTelemetryTopic(topic);
    await this.telemetryService.recordTelemetry(deviceId, payload);
  }

  private publish(topic: string, message: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.client?.connected) {
        reject(new Error('MQTT client is not connected'));
        return;
      }

      this.client.publish(topic, message, { qos: 1 }, (error) => {
        if (error) {
          reject(error);
          return;
        }
        resolve();
      });
    });
  }
}

