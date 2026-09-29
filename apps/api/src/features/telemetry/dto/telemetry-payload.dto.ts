import { IsEnum, IsNumber, IsOptional, IsString, Max, Min } from 'class-validator';
import { RelayStatus } from '../../../common/enums/relay-status.enum';

export class TelemetryPayloadDto {
  @IsNumber()
  @Min(-40)
  @Max(80)
  temperature: number;

  @IsNumber()
  @Min(0)
  @Max(100)
  humidity: number;

  @IsEnum(RelayStatus)
  relayStatus: RelayStatus;

  @IsOptional()
  @IsString()
  timestamp?: string;
}

