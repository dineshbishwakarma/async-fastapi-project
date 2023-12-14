from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# First create Base class that inherits from DeclarativeBase
# Now All models will inherit from Base class
# SQLAlchemy uses Base class to keep all information about your database schema together
# It should be created only once in whole project
class Base(DeclarativeBase):
    pass

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    publication_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # relationship tells how models are related  to each other
    #To show relationship of Post model with Comment model created post property
    # here post property doesn't create new column in comments table
    post: Mapped["Post"] = relationship("Post", back_populates = "comments")

class Post(Base):
    __tablename__ = "posts"
    # Define columns
    # mapped_column function define the type of column and its related properties
    id: Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    publication_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    comments: Mapped[list[Comment]] = relationship("Comment", cascade="all, delete")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    email: Mapped[str] = mapped_column(String(1024), index=True, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    


