from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

class Module:
    def __init__(self, app, engine):
        self.app = app
        self.engine = engine
        self.SessionDep = self.create_session_dep()

    def create_session_dep(self):
        def get_session():
            with Session(self.engine) as session:
                yield session

        return Annotated[Session, Depends(get_session)]