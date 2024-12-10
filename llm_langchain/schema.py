from ninja import Schema, Field
from .pydantic import DashboardSchema

class InstrucionSchema(Schema):
    metadata : str | None = Field(default=None, description="The metadata of the dataset provided in few sentences.")
    column_metadata : str | None = Field(default=None, description="The metadata of the columns present in the data.")


class ResponseSchema(Schema):
    instructions : DashboardSchema
    plot_code : list[str]
    plot_json : list[str]


class PostResponseSchema(InstrucionSchema, ResponseSchema):
    pass