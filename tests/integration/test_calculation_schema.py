# tests/integration/test_calculation_schema.py
import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.calculation import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationRead
)

def test_calculation_base_valid():
    """Test CalculationBase with valid data."""
    data = {"type": "addition", "inputs": [10.5, 3]}
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.ADDITION
    assert calc.inputs == [10.5, 3]

def test_calculation_base_case_insensitive_type():
    """Test that calculation type validation is case-insensitive."""
    data = {"type": "ADDITION", "inputs": [1, 2]}
    calc = CalculationBase(**data)
    assert calc.type == CalculationType.ADDITION

def test_calculation_base_invalid_type():
    """Test that an invalid calculation type raises ValidationError."""
    data = {"type": "modulus", "inputs": [10, 3]}
    with pytest.raises(ValidationError, match="Type must be one of"):
        CalculationBase(**data)

def test_calculation_base_insufficient_inputs():
    """Test that fewer than 2 inputs raises ValidationError."""
    data = {"type": "addition", "inputs": [5]}
    with pytest.raises(ValidationError, match="List should have at least 2 items"):
        CalculationBase(**data)

def test_calculation_base_division_by_zero():
    """Test that the schema validator catches division by zero."""
    data = {"type": "division", "inputs": [100, 0]}
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationBase(**data)

def test_calculation_base_division_by_zero_in_middle():
    """Test that the schema validator catches zero in any denominator."""
    data = {"type": "division", "inputs": [100, 5, 0, 2]}
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationBase(**data)

def test_calculation_base_division_zero_numerator_ok():
    """Test that zero in the numerator is valid."""
    data = {"type": "division", "inputs": [0, 5, 2]}
    calc = CalculationBase(**data)
    assert calc.inputs == [0, 5, 2]

def test_calculation_create_valid():
    """Test CalculationCreate with a valid user_id."""
    user_id = uuid4()
    data = {
        "type": "multiplication",
        "inputs": [2, 3, 4],
        "user_id": str(user_id)
    }
    calc = CalculationCreate(**data)
    assert calc.user_id == user_id
    assert calc.type == CalculationType.MULTIPLICATION

def test_calculation_create_invalid_user_id():
    """Test that an invalid UUID for user_id fails validation."""
    data = {
        "type": "subtraction",
        "inputs": [10, 5],
        "user_id": "not-a-uuid"
    }
    with pytest.raises(ValidationError):
        CalculationCreate(**data)