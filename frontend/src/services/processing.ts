import apiClient from './api'
import type {
  ProcessingJob,
  ProcessedContent,
  TextClassification
} from '../types'

/**
 * Processing service for AI classification and media processing
 */
const processingService = {
  /**
   * Start processing for a media file
   */
  async startProcessing(mediaId: string): Promise<{ success: boolean; job_id: string; status: string; message: string }> {
    const response = await apiClient.post(`/processing/start/${mediaId}`)
    return response.data
  },

  /**
   * Get status of a processing job
   */
  async getJobStatus(jobId: string): Promise<ProcessingJob> {
    const response = await apiClient.get(`/processing/status/${jobId}`)
    return response.data
  },

  /**
   * Get all processing results for a note
   */
  async getProcessingResults(noteId: string): Promise<ProcessedContent[]> {
    const response = await apiClient.get(`/processing/results/${noteId}`)
    return response.data
  },

  /**
   * Trigger text classification for a note
   */
  async classifyNote(noteId: string): Promise<{ success: boolean; task_id: string; message: string }> {
    const response = await apiClient.post(`/processing/classify/${noteId}`)
    return response.data
  },

  /**
   * Get classification results for a note
   */
  async getClassification(noteId: string): Promise<TextClassification | null> {
    const response = await apiClient.get(`/processing/classification/${noteId}`)
    return response.data
  },

  /**
   * Cancel a processing job (if still pending)
   */
  async cancelJob(jobId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/processing/${jobId}`)
    return response.data
  }
}

export default processingService
