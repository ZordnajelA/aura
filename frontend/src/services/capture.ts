import api from './api'

export enum CaptureType {
  TEXT = 'text',
  LINK = 'link',
  FILE = 'file'
}

export interface CaptureCreate {
  type: CaptureType
  content?: string
  file_name?: string
}

export interface CaptureResponse {
  id: number
  type: CaptureType
  content?: string
  file_path?: string
  file_name?: string
  file_type?: string
  created_at: string
  updated_at: string
}

/**
 * Capture text or link content
 */
export const captureText = async (content: string): Promise<CaptureResponse> => {
  const isLink = content.match(/^https?:\/\//i)

  const capture: CaptureCreate = {
    type: isLink ? CaptureType.LINK : CaptureType.TEXT,
    content
  }

  const response = await api.post<CaptureResponse>('/capture/text', capture)
  return response.data
}

/**
 * Upload and capture a file
 */
export const captureFile = async (file: File): Promise<CaptureResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<CaptureResponse>('/capture/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

/**
 * Get all captures
 */
export const getCaptures = async (skip: number = 0, limit: number = 100): Promise<CaptureResponse[]> => {
  const response = await api.get<CaptureResponse[]>('/capture/', {
    params: { skip, limit }
  })
  return response.data
}

/**
 * Get a specific capture by ID
 */
export const getCapture = async (captureId: number): Promise<CaptureResponse> => {
  const response = await api.get<CaptureResponse>(`/capture/${captureId}`)
  return response.data
}
