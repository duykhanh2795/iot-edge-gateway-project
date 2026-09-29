'use server';

import { revalidatePath } from 'next/cache';
import { controlRelay } from '../services/dashboard-api';
import type { RelayStatus } from '../types';

export async function controlRelayAction(deviceId: string, relayStatus: RelayStatus) {
  await controlRelay(deviceId, relayStatus);
  revalidatePath('/');
}

