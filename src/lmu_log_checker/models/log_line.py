from pydantic import BaseModel

class LogLine(BaseModel):
    time_s: str
    file: str
    line: int # line of the log's message
    message: str
