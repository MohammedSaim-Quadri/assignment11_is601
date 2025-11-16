# tests/integration/test_calculation.py
import pytest
import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)

# We use the 'db_session' fixture from your M10 conftest.py
# We also use the 'test_user' fixture to get a valid user_id

def test_calculation_factory_addition(db_session: Session, test_user: User):
    """Test the Calculation.create factory for addition."""
    inputs = [1, 2, 3]
    calc = Calculation.create(
        calculation_type='addition',
        user_id=test_user.id,
        inputs=inputs,
    )
    db_session.add(calc)
    db_session.commit()

    assert isinstance(calc, Addition)
    assert calc.get_result() == 6
    assert calc.result == 6 # Verify result was stored

def test_calculation_factory_subtraction(db_session: Session, test_user: User):
    """Test the Calculation.create factory for subtraction."""
    inputs = [10, 4]
    calc = Calculation.create(
        calculation_type='subtraction',
        user_id=test_user.id,
        inputs=inputs,
    )
    db_session.add(calc)
    db_session.commit()

    assert isinstance(calc, Subtraction)
    assert calc.get_result() == 6
    assert calc.result == 6

def test_calculation_factory_multiplication(db_session: Session, test_user: User):
    """Test the Calculation.create factory for multiplication."""
    inputs = [3, 4, 2]
    calc = Calculation.create(
        calculation_type='multiplication',
        user_id=test_user.id,
        inputs=inputs,
    )
    db_session.add(calc)
    db_session.commit()
    
    assert isinstance(calc, Multiplication)
    assert calc.get_result() == 24
    assert calc.result == 24

def test_calculation_factory_division(db_session: Session, test_user: User):
    """Test the Calculation.create factory for division."""
    inputs = [100, 2, 5]
    calc = Calculation.create(
        calculation_type='division',
        user_id=test_user.id,
        inputs=inputs,
    )
    db_session.add(calc)
    db_session.commit()

    assert isinstance(calc, Division)
    assert calc.get_result() == 10
    assert calc.result == 10

def test_calculation_factory_invalid_type(test_user: User):
    """Test the factory raises an error for an unsupported type."""
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(
            calculation_type='modulus',
            user_id=test_user.id,
            inputs=[10, 3],
        )

def test_polymorphic_query(db_session: Session, test_user: User):
    """Test that a query on the base Calculation returns all types."""
    db_session.add_all([
        Calculation.create('addition', test_user.id, [1, 2, 3]),
        Calculation.create('division', test_user.id, [100, 10]),
    ])
    db_session.commit()

    # Query the base class
    calcs = db_session.query(Calculation).all()
    assert len(calcs) == 2

    # Verify SQLAlchemy returned the correct subclasses
    assert isinstance(calcs[0], Addition)
    assert isinstance(calcs[1], Division)
    assert calcs[0].get_result() == 6
    assert calcs[1].get_result() == 10

def test_division_by_zero_model(test_user: User):
    """Test the model's internal division by zero check."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Calculation.create(
            calculation_type='division',
            user_id=test_user.id,
            inputs=[100, 0],
        )