import api from './api'

export interface MediaFile {
  id: string
  note_id: string
  file_path: string
  file_type: string
  file_size: number | null
  mime_type: string | null
  is_processed: boolean
  created_at: string
}

export interface MediaUploadResponse extends MediaFile {
  url: string
}

class MediaService {
  /**
   * Upload a media file and create an associated note
   */
  async uploadFile(
    file: File,
    title?: string,
    content?: string
  ): Promise<MediaUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    if (title) {
      formData.append('title', title)
    }

    if (content) {
      formData.append('content', content)
    }

    const response = await api.post<MediaUploadResponse>('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  }

  /**
   * Get all media files for a specific note
   */
  async getNoteMedia(noteId: string): Promise<MediaFile[]> {
    const response = await api.get<MediaFile[]>(`/media/note/${noteId}`)
    return response.data
  }

  /**
   * Get a specific media file by ID
   */
  async getMedia(mediaId: string): Promise<MediaFile> {
    const response = await api.get<MediaFile>(`/media/${mediaId}`)
    return response.data
  }

  /**
   * Delete a media file
   */
  async deleteMedia(mediaId: string): Promise<void> {
    await api.delete(`/media/${mediaId}`)
  }

  /**
   * Get the full URL for a media file
   */
  getMediaUrl(relativePath: string): string {
    // Remove leading slash if present
    const path = relativePath.startsWith('/') ? relativePath : `/${relativePath}`
    return `${api.defaults.baseURL}${path}`
  }
}

export const mediaService = new MediaService()
export default mediaService
