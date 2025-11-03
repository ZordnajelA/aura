"""
API endpoints for PARA (Projects, Areas, Resources, Archives) functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Area, Project, Resource, Archive, User
from ..schemas.para import (
    AreaCreate, AreaUpdate, AreaResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ResourceCreate, ResourceUpdate, ResourceResponse,
    ArchiveCreate, ArchiveResponse
)
from .dependencies import get_current_user

router = APIRouter()


# ============================================================================
# AREAS ENDPOINTS
# ============================================================================

@router.post("/areas", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
async def create_area(
    area: AreaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new area for the authenticated user"""
    db_area = Area(
        user_id=current_user.id,
        name=area.name,
        description=area.description,
        icon=area.icon,
        display_order=area.display_order
    )

    db.add(db_area)
    db.commit()
    db.refresh(db_area)

    return db_area


@router.get("/areas", response_model=List[AreaResponse])
async def get_areas(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all areas for the authenticated user"""
    areas = (
        db.query(Area)
        .filter(Area.user_id == current_user.id)
        .order_by(Area.display_order.asc(), Area.created_at.desc())
        .all()
    )
    return areas


@router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area(
    area_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific area by ID"""
    area = (
        db.query(Area)
        .filter(Area.id == area_id, Area.user_id == current_user.id)
        .first()
    )

    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found"
        )

    return area


@router.put("/areas/{area_id}", response_model=AreaResponse)
async def update_area(
    area_id: UUID,
    area_update: AreaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an area"""
    area = (
        db.query(Area)
        .filter(Area.id == area_id, Area.user_id == current_user.id)
        .first()
    )

    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found"
        )

    # Update fields if provided
    if area_update.name is not None:
        area.name = area_update.name
    if area_update.description is not None:
        area.description = area_update.description
    if area_update.icon is not None:
        area.icon = area_update.icon
    if area_update.display_order is not None:
        area.display_order = area_update.display_order

    db.commit()
    db.refresh(area)

    return area


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_area(
    area_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an area"""
    area = (
        db.query(Area)
        .filter(Area.id == area_id, Area.user_id == current_user.id)
        .first()
    )

    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found"
        )

    db.delete(area)
    db.commit()

    return None


# ============================================================================
# PROJECTS ENDPOINTS
# ============================================================================

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project for the authenticated user"""
    db_project = Project(
        user_id=current_user.id,
        area_id=project.area_id,
        name=project.name,
        description=project.description,
        status=project.status,
        due_date=project.due_date
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    status: str = None,
    area_id: UUID = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects for the authenticated user with optional filters"""
    query = db.query(Project).filter(Project.user_id == current_user.id)

    if status:
        query = query.filter(Project.status == status)
    if area_id:
        query = query.filter(Project.area_id == area_id)

    projects = query.order_by(Project.created_at.desc()).all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project by ID"""
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update fields if provided
    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.area_id is not None:
        project.area_id = project_update.area_id
    if project_update.status is not None:
        project.status = project_update.status
    if project_update.due_date is not None:
        project.due_date = project_update.due_date

    db.commit()
    db.refresh(project)

    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return None


# ============================================================================
# RESOURCES ENDPOINTS
# ============================================================================

@router.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource for the authenticated user"""
    db_resource = Resource(
        user_id=current_user.id,
        area_id=resource.area_id,
        title=resource.title,
        content=resource.content,
        resource_type=resource.resource_type,
        url=resource.url
    )

    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)

    return db_resource


@router.get("/resources", response_model=List[ResourceResponse])
async def get_resources(
    resource_type: str = None,
    area_id: UUID = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all resources for the authenticated user with optional filters"""
    query = db.query(Resource).filter(Resource.user_id == current_user.id)

    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if area_id:
        query = query.filter(Resource.area_id == area_id)

    resources = query.order_by(Resource.created_at.desc()).all()
    return resources


@router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resource by ID"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.user_id == current_user.id)
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    return resource


@router.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: UUID,
    resource_update: ResourceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a resource"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.user_id == current_user.id)
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Update fields if provided
    if resource_update.title is not None:
        resource.title = resource_update.title
    if resource_update.content is not None:
        resource.content = resource_update.content
    if resource_update.area_id is not None:
        resource.area_id = resource_update.area_id
    if resource_update.resource_type is not None:
        resource.resource_type = resource_update.resource_type
    if resource_update.url is not None:
        resource.url = resource_update.url

    db.commit()
    db.refresh(resource)

    return resource


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resource"""
    resource = (
        db.query(Resource)
        .filter(Resource.id == resource_id, Resource.user_id == current_user.id)
        .first()
    )

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    db.delete(resource)
    db.commit()

    return None


# ============================================================================
# ARCHIVES ENDPOINTS
# ============================================================================

@router.post("/archives", response_model=ArchiveResponse, status_code=status.HTTP_201_CREATED)
async def create_archive(
    archive: ArchiveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive an item (project, area, resource, or note)"""
    db_archive = Archive(
        user_id=current_user.id,
        parent_type=archive.parent_type,
        parent_id=archive.parent_id,
        archive_metadata=archive.archive_metadata
    )

    db.add(db_archive)
    db.commit()
    db.refresh(db_archive)

    return db_archive


@router.get("/archives", response_model=List[ArchiveResponse])
async def get_archives(
    parent_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all archived items for the authenticated user with optional filter"""
    query = db.query(Archive).filter(Archive.user_id == current_user.id)

    if parent_type:
        query = query.filter(Archive.parent_type == parent_type)

    archives = query.order_by(Archive.archived_at.desc()).all()
    return archives


@router.get("/archives/{archive_id}", response_model=ArchiveResponse)
async def get_archive(
    archive_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific archive entry by ID"""
    archive = (
        db.query(Archive)
        .filter(Archive.id == archive_id, Archive.user_id == current_user.id)
        .first()
    )

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archive entry not found"
        )

    return archive


@router.delete("/archives/{archive_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_archive(
    archive_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete an archive entry"""
    archive = (
        db.query(Archive)
        .filter(Archive.id == archive_id, Archive.user_id == current_user.id)
        .first()
    )

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archive entry not found"
        )

    db.delete(archive)
    db.commit()

    return None
