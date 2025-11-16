# app/schemas/calculation.py
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator
)
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class CalculationType(str, Enum):
    """Enumeration of valid calculation types."""
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    """Base schema for calculation data."""
    type: CalculationType = Field(
        ...,
        description="Type of calculation to perform",
        examples=["addition"]
    )
    inputs: List[float] = Field(
        ...,
        description="List of numeric inputs for the calculation",
        examples=[[10.5, 3, 2]],
        min_length=2
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v):
        """Validate and normalize the calculation type."""
        if not isinstance(v, str):
            raise ValueError("Type must be a string")
        
        allowed = {e.value for e in CalculationType}
        if v.lower() not in allowed:
            raise ValueError(
                f"Type must be one of: {', '.join(sorted(allowed))}"
            )
        return v.lower()

    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, v):
        """Validate that inputs is a list."""
        if not isinstance(v, list):
            raise ValueError("Input should be a valid list")
        return v

    @model_validator(mode='after')
    def validate_inputs(self) -> "CalculationBase":
        """Validate inputs based on calculation type."""
        if len(self.inputs) < 2:
            raise ValueError(
                "At least two numbers are required for calculation"
            )
        if self.type == CalculationType.DIVISION:
            # Prevent division by zero (skip first value as numerator)
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"type": "addition", "inputs": [10.5, 3, 2]},
                {"type": "division", "inputs": [100, 2]}
            ]
        }
    )


class CalculationCreate(CalculationBase):
    """
    Schema for creating a new Calculation.
    NOTE: In a real app, user_id would come from auth, not the request body.
    For this module, we include it to test the foreign key.
    """
    user_id: UUID = Field(
        ...,
        description="UUID of the user who owns this calculation",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class CalculationRead(CalculationBase):
    """
    Schema for reading a Calculation.
    This defines the shape of the data returned from the API.
    """
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    result: float # The result is required in the read model

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174999",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "addition",
                "inputs": [10.5, 3, 2],
                "result": 15.5,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    )