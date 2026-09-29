import { apiGet, apiPost } from '@/lib/api-client';
import type { DashboardOverview, RelayStatus } from '../types';

export function getDashboardOverview(): Promise<DashboardOverview> {
  return apiGet<DashboardOverview>('/dashboard/overview');
}

export function controlRelay(deviceId: string, relayStatus: RelayStatus) {
  return apiPost(`/devices/${deviceId}/control/relay`, { relayStatus });
}

