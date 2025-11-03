import { useState, useEffect } from 'react'
import Navigation from '@/components/Navigation'
import paraService, { Area, Project, Resource, Archive } from '@/services/para'
import {
  Plus,
  Folder,
  Rocket,
  BookOpen,
  Archive as ArchiveIcon,
  Pencil,
  Trash2
} from 'lucide-react'

type TabType = 'projects' | 'areas' | 'resources' | 'archives'

export default function PARAPage() {
  const [activeTab, setActiveTab] = useState<TabType>('projects')
  const [areas, setAreas] = useState<Area[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [archives, setArchives] = useState<Archive[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Form states
  const [newItem, setNewItem] = useState({
    name: '',
    title: '',
    description: '',
    content: '',
    area_id: '',
    status: 'active',
    due_date: '',
    resource_type: 'note',
    url: '',
    icon: '',
    display_order: 0
  })

  useEffect(() => {
    loadData()
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'areas':
          const areasData = await paraService.getAreas()
          setAreas(areasData)
          break
        case 'projects':
          const projectsData = await paraService.getProjects()
          setProjects(projectsData)
          break
        case 'resources':
          const resourcesData = await paraService.getResources()
          setResources(resourcesData)
          break
        case 'archives':
          const archivesData = await paraService.getArchives()
          setArchives(archivesData)
          break
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      switch (activeTab) {
        case 'areas':
          await paraService.createArea({
            name: newItem.name,
            description: newItem.description,
            icon: newItem.icon,
            display_order: newItem.display_order
          })
          break
        case 'projects':
          await paraService.createProject({
            name: newItem.name,
            description: newItem.description,
            area_id: newItem.area_id || undefined,
            status: newItem.status,
            due_date: newItem.due_date || undefined
          })
          break
        case 'resources':
          await paraService.createResource({
            title: newItem.title,
            content: newItem.content,
            area_id: newItem.area_id || undefined,
            resource_type: newItem.resource_type,
            url: newItem.url || undefined
          })
          break
      }
      setShowCreateModal(false)
      resetForm()
      loadData()
    } catch (error) {
      console.error('Error creating item:', error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this item?')) return

    try {
      switch (activeTab) {
        case 'areas':
          await paraService.deleteArea(id)
          break
        case 'projects':
          await paraService.deleteProject(id)
          break
        case 'resources':
          await paraService.deleteResource(id)
          break
        case 'archives':
          await paraService.deleteArchive(id)
          break
      }
      loadData()
    } catch (error) {
      console.error('Error deleting item:', error)
    }
  }

  const resetForm = () => {
    setNewItem({
      name: '',
      title: '',
      description: '',
      content: '',
      area_id: '',
      status: 'active',
      due_date: '',
      resource_type: 'note',
      url: '',
      icon: '',
      display_order: 0
    })
  }

  const tabs = [
    { id: 'projects', name: 'Projects', icon: Rocket, color: 'text-blue-600' },
    { id: 'areas', name: 'Areas', icon: Folder, color: 'text-green-600' },
    { id: 'resources', name: 'Resources', icon: BookOpen, color: 'text-purple-600' },
    { id: 'archives', name: 'Archives', icon: ArchiveIcon, color: 'text-gray-600' }
  ]

  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">PARA Organization</h1>
            {activeTab !== 'archives' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="h-5 w-5" />
                Add {activeTab.slice(0, -1).charAt(0).toUpperCase() + activeTab.slice(1, -1)}
              </button>
            )}
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-gray-200">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`h-5 w-5 ${activeTab === tab.id ? tab.color : ''}`} />
                  <span className="font-medium">{tab.name}</span>
                </button>
              )
            })}
          </div>

          {/* Content */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loading ? (
              <div className="col-span-full text-center py-12 text-gray-500">Loading...</div>
            ) : (
              <>
                {activeTab === 'areas' && areas.map((area) => (
                  <AreaCard key={area.id} area={area} onDelete={handleDelete} />
                ))}
                {activeTab === 'projects' && projects.map((project) => (
                  <ProjectCard key={project.id} project={project} onDelete={handleDelete} />
                ))}
                {activeTab === 'resources' && resources.map((resource) => (
                  <ResourceCard key={resource.id} resource={resource} onDelete={handleDelete} />
                ))}
                {activeTab === 'archives' && archives.map((archive) => (
                  <ArchiveCard key={archive.id} archive={archive} onDelete={handleDelete} />
                ))}
                {((activeTab === 'areas' && areas.length === 0) ||
                  (activeTab === 'projects' && projects.length === 0) ||
                  (activeTab === 'resources' && resources.length === 0) ||
                  (activeTab === 'archives' && archives.length === 0)) && (
                  <div className="col-span-full text-center py-12 text-gray-500">
                    No {activeTab} yet. Click the button above to create one!
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">
              Create {activeTab.slice(0, -1).charAt(0).toUpperCase() + activeTab.slice(1, -1)}
            </h2>

            <div className="space-y-4">
              {activeTab === 'areas' && (
                <>
                  <input
                    type="text"
                    placeholder="Name"
                    value={newItem.name}
                    onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                  <textarea
                    placeholder="Description"
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                  />
                  <input
                    type="text"
                    placeholder="Icon (emoji or name)"
                    value={newItem.icon}
                    onChange={(e) => setNewItem({ ...newItem, icon: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </>
              )}

              {activeTab === 'projects' && (
                <>
                  <input
                    type="text"
                    placeholder="Project Name"
                    value={newItem.name}
                    onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                  <textarea
                    placeholder="Description"
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                  />
                  <select
                    value={newItem.area_id}
                    onChange={(e) => setNewItem({ ...newItem, area_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="">No Area</option>
                    {areas.map((area) => (
                      <option key={area.id} value={area.id}>{area.name}</option>
                    ))}
                  </select>
                  <input
                    type="date"
                    value={newItem.due_date}
                    onChange={(e) => setNewItem({ ...newItem, due_date: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </>
              )}

              {activeTab === 'resources' && (
                <>
                  <input
                    type="text"
                    placeholder="Title"
                    value={newItem.title}
                    onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                  <textarea
                    placeholder="Content"
                    value={newItem.content}
                    onChange={(e) => setNewItem({ ...newItem, content: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                  />
                  <select
                    value={newItem.resource_type}
                    onChange={(e) => setNewItem({ ...newItem, resource_type: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="note">Note</option>
                    <option value="bookmark">Bookmark</option>
                    <option value="file">File</option>
                  </select>
                  <input
                    type="url"
                    placeholder="URL (optional)"
                    value={newItem.url}
                    onChange={(e) => setNewItem({ ...newItem, url: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </>
              )}
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={handleCreate}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Create
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  resetForm()
                }}
                className="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Card Components
function AreaCard({ area, onDelete }: { area: Area; onDelete: (id: string) => void }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          {area.icon && <span className="text-2xl">{area.icon}</span>}
          <h3 className="font-semibold text-lg">{area.name}</h3>
        </div>
        <button
          onClick={() => onDelete(area.id)}
          className="text-red-500 hover:text-red-700"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>
      {area.description && <p className="text-gray-600 text-sm">{area.description}</p>}
    </div>
  )
}

function ProjectCard({ project, onDelete }: { project: Project; onDelete: (id: string) => void }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg">{project.name}</h3>
        <button
          onClick={() => onDelete(project.id)}
          className="text-red-500 hover:text-red-700"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>
      {project.description && <p className="text-gray-600 text-sm mb-2">{project.description}</p>}
      <div className="flex items-center gap-2">
        <span className={`px-2 py-1 text-xs rounded ${
          project.status === 'active' ? 'bg-green-100 text-green-700' :
          project.status === 'completed' ? 'bg-blue-100 text-blue-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {project.status}
        </span>
        {project.due_date && (
          <span className="text-xs text-gray-500">Due: {new Date(project.due_date).toLocaleDateString()}</span>
        )}
      </div>
    </div>
  )
}

function ResourceCard({ resource, onDelete }: { resource: Resource; onDelete: (id: string) => void }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg">{resource.title}</h3>
        <button
          onClick={() => onDelete(resource.id)}
          className="text-red-500 hover:text-red-700"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>
      {resource.content && <p className="text-gray-600 text-sm mb-2">{resource.content}</p>}
      <div className="flex items-center gap-2">
        <span className="px-2 py-1 text-xs rounded bg-purple-100 text-purple-700">
          {resource.resource_type}
        </span>
        {resource.url && (
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-500 hover:underline truncate"
          >
            Link
          </a>
        )}
      </div>
    </div>
  )
}

function ArchiveCard({ archive, onDelete }: { archive: Archive; onDelete: (id: string) => void }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg">Archived {archive.parent_type}</h3>
        <button
          onClick={() => onDelete(archive.id)}
          className="text-red-500 hover:text-red-700"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>
      <p className="text-gray-600 text-sm">
        ID: {archive.parent_id.slice(0, 8)}...
      </p>
      <p className="text-xs text-gray-500 mt-2">
        Archived: {new Date(archive.archived_at).toLocaleDateString()}
      </p>
    </div>
  )
}
