from sqlalchemy.exc import IntegrityError
from app.db.projectStatus import model
from app.exceptions import handle_database_error, handle_not_found


def create_projectStatus(db, project_id, status):
    try:
        db_projectStatus = model.ProjectStatus(pid=project_id, sid=status.id)
        db.add(db_projectStatus)
        db.commit()
        db.refresh(db_projectStatus)
        return db_projectStatus
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "Duplicate entry" in error_msg:
            handle_database_error(e, "Create projectStatus", detail="Status already added to this project")
        else:
            handle_database_error(e, "Create projectStatus")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create projectStatus")

def get_projectStatus(db, project_id):
    try:
        return db.query(model.ProjectStatus).filter(model.ProjectStatus.pid == project_id).all()
    except Exception as e:
        handle_database_error(e, "Get projectStatus")

def delete_projectStatus(db, project_id, status_id):
    try:
        db_projectStatus = db.query(model.ProjectStatus).filter(
            model.ProjectStatus.pid == project_id
        ).filter(
            model.ProjectStatus.sid == status_id
        ).first()
        if not db_projectStatus:
            handle_not_found("ProjectStatus", f"project_id={project_id}, status_id={status_id}")
        db.delete(db_projectStatus)
        db.commit()
        return db_projectStatus
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete projectStatus")


