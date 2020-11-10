from pydantic import BaseModel


class discordConfigModel(BaseModel):
    token: str
    prefix: str
    debug: bool


class fastapiConfigModel(BaseModel):
    host: str
    port: int
    title: str
    description: str
    debug: bool


class MusicExtensionConfigModel(BaseModel):
    X_Naver_Client_Id: str
    X_Naver_Client_Secret: str


class MongoDBConfigModel(BaseModel):
    db_url: str
    db_port: int
