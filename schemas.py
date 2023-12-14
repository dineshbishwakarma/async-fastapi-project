from datetime import datetime
from pydantic import BaseModel, Field

class CommentBase(BaseModel):
    publication_date: datetime = Field(default_factory=datetime.now())
    content: str

    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    post_id: int

class PostBase(BaseModel):
    title: str
    content: str
    publication_date: datetime = Field(default_factory=datetime.now())
    class Config:
        # pydantic parse data from dictionary like d['title']
        # orm access properties like an object like o.title
        # orm_mode = True enables pydantic to use orm style like o.title
        orm_mode = True

class PostPartialUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostCreate(PostBase):
    # pass here means inherit all porperties from PostBase class
    pass

class PostRead(PostBase):
    id: int
    comments: list[CommentRead]

class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    hashed_password: str

class UserRead(UserBase):
    id: int