import contextlib
from collections.abc import Sequence


from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from sqlalchemy.orm import selectinload

from database import create_all_tables
import schemas
from models import Post, Comment

# To make sure our schema is created when our application start
# we must call a function called lifespan handler

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def hello_world():
    return {"hello": "world"}

# Define pagination
async def pagination(
        # number of item to skip
        skip: int = Query(0, ge=0),
        # number of item to retieve per page
        limit: int = Query(10, ge=0)
) -> tuple[int, int]:
    # Make sure that limit is not above 100
    # max 100 items are shown per page
    capped_limit= min(100, limit)
    return (skip, capped_limit)

async def get_post_or_404(
        id: int, session: AsyncSession = Depends(get_async_session)
) -> Post:
    # select_query = select(Post).where(Post.id == id)
    # result = await session.execute(select_query)

    # # return single object if exists elese return none
    # post = result.scalar_one_or_none()

    # Retrive a post and its comments 
    select_query = (select(Post).options(selectinload(Post.comments)).where(Post.id == id))
    result = await session.execute(select_query)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return post



# Creating a Post
@app.post("/posts", response_model = schemas.PostRead, status_code=status.HTTP_201_CREATED)

async def create_post(post_create: schemas.PostCreate, session: AsyncSession = Depends(get_async_session)) -> Post:

    # convert pydantic input into SQLAlchemy model
    post = Post(**post_create.dict())

    # add post in the session memory
    session.add(post)

    # commit will tell the session to generate appropriate SQL queries and execute them on the data base
    await session.commit()

    return post

# Getting and Filtering Posts
@app.get("/posts",response_model=list[schemas.PostRead])
async def list_posts(
    pagination: tuple[int,int] = Depends(pagination),
    session: AsyncSession = Depends(get_async_session)
) -> Sequence[Post]:
    skip, limit = pagination

    # Here it will automatically know which table to make query
    select_query = select(Post).offset(skip).limit(limit=limit)

    result = await session.execute(select_query)
    # give the resul in sequence
    return result.scalars().all()
    
# Getting single post by ID
@app.get("/posts/{id}", response_model=schemas.PostRead)
async def get_post(post: Post =  Depends(get_post_or_404)) -> Post:
    return post

# Updating a Post
# Use PATCH : updates only specific parts without affecting entire resourc

@app.patch("/posts/{id}", response_model=schemas.PostRead)
async def update_post(
    post_update: schemas.PostPartialUpdate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session)
) -> Post:
    
    # exclude_unset = True : only get the fields that were set in payload
    post_update_dict = post_update.dict(exclude_unset=True)
    for key, value in post_update_dict.items():
        # update matching key to value in post
        setattr(post, key, value)

    
    session.add(post)
    await session.commit()

    return post

# Deleting a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post: Post = Depends(get_post_or_404),
        session: AsyncSession = Depends(get_async_session)
):
    await session.delete(post)
    await session.commit()

    return None

# Create a new comment

@app.post("/posts/{id}/comments",
          response_model = schemas.CommentRead,
          status_code=status.HTTP_201_CREATED,)
async def create_comment(
    comment_create: schemas.CommentCreate,
    post: Post = Depends(get_post_or_404),
    session: AsyncSession = Depends(get_async_session),
) -> Comment:
    comment = Comment(**comment_create.dict(), post = post)
    session.add(comment)
    await session.commit()

    return comment