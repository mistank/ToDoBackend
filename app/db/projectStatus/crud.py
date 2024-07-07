from app.db.projectStatus import model


def create_projectStatus(db, project_id, status):
    db_projectStatus = model.ProjectStatus(pid=project_id,sid=status.id)
    db.add(db_projectStatus)
    db.commit()
    db.refresh(db_projectStatus)
    return db_projectStatus

def get_projectStatus(db, project_id):
    return db.query(model.ProjectStatus).filter(model.ProjectStatus.pid == project_id).all()

def delete_projectStatus(db, project_id, status_id):
    db_projectStatus = db.query(model.ProjectStatus).filter(model.ProjectStatus.pid == project_id).filter(model.ProjectStatus.sid == status_id).first()
    db.delete(db_projectStatus)
    db.commit()
    return db_projectStatus


