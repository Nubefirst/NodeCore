import api from './api'
import type { SystemInfo } from '../types/system'

export async function getSystemInfo(): Promise<SystemInfo> {
    const response = await api.get<SystemInfo>('/system/info')

    return response.data
}
