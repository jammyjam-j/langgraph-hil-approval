We don't have content but assume typical FastAPI. Implement POST /process to run graph; GET /status. Use Depends for DB session. Use graph.py.from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.graph as graph_module
import app.schemas as schemas
import app.database as database
import app.dependencies as dependencies


router = APIRouter()


@router.post(
    "/process",
    response_model=schemas.ProcessResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def process_request(
    request: schemas.ProcessRequest,
    db: Session = Depends(dependencies.get_db),
) -> schemas.ProcessResponse:
    """
    Initiate a processing workflow for the provided data.
    The graph is executed asynchronously and its state is persisted in the database.
    """
    try:
        task_id = await graph_module.run_graph(
            request.input_data,
            db=db,
            user=request.user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start processing workflow",
        ) from exc

    return schemas.ProcessResponse(task_id=task_id)


@router.get(
    "/status/{task_id}",
    response_model=schemas.TaskStatus,
    status_code=status.HTTP_200_OK,
)
async def get_task_status(
    task_id: str,
    db: Session = Depends(dependencies.get_db),
) -> schemas.TaskStatus:
    """
    Retrieve the current status of a running or completed task.
    """
    task_record = database.SessionLocal().query(database.Task).filter_by(id=task_id).first()
    if not task_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return schemas.TaskStatus(
        task_id=task_id,
        status=task_record.status,
        result=task_record.result,
    )


@router.post(
    "/seed",
    response_model=schemas.SeedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def seed_data(
    db: Session = Depends(dependencies.get_db),
) -> schemas.SeedResponse:
    """
    Populate the database with initial data for testing or demo purposes.
    """
    try:
        scripts_module = __import__("scripts.seed_data", fromlist=["seed"])
        scripts_module.seed(db)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Seeding failed",
        ) from exc

    return schemas.SeedResponse(message="Database seeded successfully")