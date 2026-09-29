import { RelayStatus } from '../../../common/enums/relay-status.enum';

export interface AiPredictionRequestDto {
  device_id: string;
  temperature: number;
  humidity: number;
  relay_status: RelayStatus;
  observed_at: string;
}

