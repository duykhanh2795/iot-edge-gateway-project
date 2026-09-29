import { IsEnum } from 'class-validator';
import { RelayStatus } from '../../../common/enums/relay-status.enum';

export class ControlRelayDto {
  @IsEnum(RelayStatus)
  relayStatus: RelayStatus;
}

