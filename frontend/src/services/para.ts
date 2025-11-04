import api from './api'

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface Area {
  id: string
  user_id: string
  name: string
  description: string | null
  icon: string | null
  display_order: number
  created_at: string
  updated_at: string
}

export interface AreaCreate {
  name: string
  description?: string
  icon?: string
  display_order?: number
}

export interface AreaUpdate {
  name?: string
  description?: string
  icon?: string
  display_order?: number
}

export interface Project {
  id: string
  user_id: string
  area_id: string | null
  name: string
  description: string | null
  status: 'active' | 'completed' | 'archived'
  due_date: string | null
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  description?: string
  area_id?: string
  status?: string
  due_date?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  area_id?: string
  status?: string
  due_date?: string
}

export interface Resource {
  id: string
  user_id: string
  area_id: string | null
  title: string
  content: string | null
  resource_type: 'note' | 'bookmark' | 'file'
  url: string | null
  created_at: string
  updated_at: string
}

export interface ResourceCreate {
  title: string
  content?: string
  area_id?: string
  resource_type?: string
  url?: string
}

export interface ResourceUpdate {
  title?: string
  content?: string
  area_id?: string
  resource_type?: string
  url?: string
}

export interface Archive {
  id: string
  user_id: string
  parent_type: 'project' | 'area' | 'resource' | 'note'
  parent_id: string
  archived_at: string
  archive_metadata: string | null
}

export interface ArchiveCreate {
  parent_type: string
  parent_id: string
  archive_metadata?: string
}

// ============================================================================
// PARA SERVICE
// ============================================================================

class PARAService {
  // ==========================================================================
  // AREAS
  // ==========================================================================

  /**
   * Create a new area
   */
  async createArea(data: AreaCreate): Promise<Area> {
    const response = await api.post<Area>('/para/areas', data)
    return response.data
  }

  /**
   * Get all areas
   */
  async getAreas(): Promise<Area[]> {
    const response = await api.get<Area[]>('/para/areas')
    return response.data
  }

  /**
   * Get a specific area by ID
   */
  async getArea(areaId: string): Promise<Area> {
    const response = await api.get<Area>(`/para/areas/${areaId}`)
    return response.data
  }

  /**
   * Update an area
   */
  async updateArea(areaId: string, data: AreaUpdate): Promise<Area> {
    const response = await api.put<Area>(`/para/areas/${areaId}`, data)
    return response.data
  }

  /**
   * Delete an area
   */
  async deleteArea(areaId: string): Promise<void> {
    await api.delete(`/para/areas/${areaId}`)
  }

  // ==========================================================================
  // PROJECTS
  // ==========================================================================

  /**
   * Create a new project
   */
  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await api.post<Project>('/para/projects', data)
    return response.data
  }

  /**
   * Get all projects with optional filters
   */
  async getProjects(status?: string, areaId?: string): Promise<Project[]> {
    const response = await api.get<Project[]>('/para/projects', {
      params: { status, area_id: areaId }
    })
    return response.data
  }

  /**
   * Get a specific project by ID
   */
  async getProject(projectId: string): Promise<Project> {
    const response = await api.get<Project>(`/para/projects/${projectId}`)
    return response.data
  }

  /**
   * Update a project
   */
  async updateProject(projectId: string, data: ProjectUpdate): Promise<Project> {
    const response = await api.put<Project>(`/para/projects/${projectId}`, data)
    return response.data
  }

  /**
   * Delete a project
   */
  async deleteProject(projectId: string): Promise<void> {
    await api.delete(`/para/projects/${projectId}`)
  }

  // ==========================================================================
  // RESOURCES
  // ==========================================================================

  /**
   * Create a new resource
   */
  async createResource(data: ResourceCreate): Promise<Resource> {
    const response = await api.post<Resource>('/para/resources', data)
    return response.data
  }

  /**
   * Get all resources with optional filters
   */
  async getResources(resourceType?: string, areaId?: string): Promise<Resource[]> {
    const response = await api.get<Resource[]>('/para/resources', {
      params: { resource_type: resourceType, area_id: areaId }
    })
    return response.data
  }

  /**
   * Get a specific resource by ID
   */
  async getResource(resourceId: string): Promise<Resource> {
    const response = await api.get<Resource>(`/para/resources/${resourceId}`)
    return response.data
  }

  /**
   * Update a resource
   */
  async updateResource(resourceId: string, data: ResourceUpdate): Promise<Resource> {
    const response = await api.put<Resource>(`/para/resources/${resourceId}`, data)
    return response.data
  }

  /**
   * Delete a resource
   */
  async deleteResource(resourceId: string): Promise<void> {
    await api.delete(`/para/resources/${resourceId}`)
  }

  // ==========================================================================
  // ARCHIVES
  // ==========================================================================

  /**
   * Archive an item
   */
  async createArchive(data: ArchiveCreate): Promise<Archive> {
    const response = await api.post<Archive>('/para/archives', data)
    return response.data
  }

  /**
   * Get all archived items with optional filter
   */
  async getArchives(parentType?: string): Promise<Archive[]> {
    const response = await api.get<Archive[]>('/para/archives', {
      params: { parent_type: parentType }
    })
    return response.data
  }

  /**
   * Get a specific archive entry by ID
   */
  async getArchive(archiveId: string): Promise<Archive> {
    const response = await api.get<Archive>(`/para/archives/${archiveId}`)
    return response.data
  }

  /**
   * Delete an archive entry
   */
  async deleteArchive(archiveId: string): Promise<void> {
    await api.delete(`/para/archives/${archiveId}`)
  }

  // ==========================================================================
  // NOTE LINKING
  // ==========================================================================

  /**
   * Link a note to an area
   */
  async linkNoteToArea(areaId: string, noteId: string): Promise<void> {
    await api.post(`/para/areas/${areaId}/notes/${noteId}`)
  }

  /**
   * Unlink a note from an area
   */
  async unlinkNoteFromArea(areaId: string, noteId: string): Promise<void> {
    await api.delete(`/para/areas/${areaId}/notes/${noteId}`)
  }

  /**
   * Get all notes linked to an area
   */
  async getAreaNotes(areaId: string): Promise<any[]> {
    const response = await api.get(`/para/areas/${areaId}/notes`)
    return response.data
  }

  /**
   * Link a note to a project
   */
  async linkNoteToProject(projectId: string, noteId: string): Promise<void> {
    await api.post(`/para/projects/${projectId}/notes/${noteId}`)
  }

  /**
   * Unlink a note from a project
   */
  async unlinkNoteFromProject(projectId: string, noteId: string): Promise<void> {
    await api.delete(`/para/projects/${projectId}/notes/${noteId}`)
  }

  /**
   * Get all notes linked to a project
   */
  async getProjectNotes(projectId: string): Promise<any[]> {
    const response = await api.get(`/para/projects/${projectId}/notes`)
    return response.data
  }

  /**
   * Link a note to a resource
   */
  async linkNoteToResource(resourceId: string, noteId: string): Promise<void> {
    await api.post(`/para/resources/${resourceId}/notes/${noteId}`)
  }

  /**
   * Unlink a note from a resource
   */
  async unlinkNoteFromResource(resourceId: string, noteId: string): Promise<void> {
    await api.delete(`/para/resources/${resourceId}/notes/${noteId}`)
  }

  /**
   * Get all notes linked to a resource
   */
  async getResourceNotes(resourceId: string): Promise<any[]> {
    const response = await api.get(`/para/resources/${resourceId}/notes`)
    return response.data
  }
}

export const paraService = new PARAService()
export default paraService
