# app/models/calculation.py
from datetime import datetime
import uuid
from typing import List
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from app.database import Base # Make sure this imports from your updated database.py

class AbstractCalculation:
    """
    Abstract base class defining common attributes for all calculations.
    Uses @declared_attr decorator for shared columns.
    """

    @declared_attr
    def __tablename__(cls):
        return 'calculations'

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )

    @declared_attr
    def user_id(cls):
        """Foreign key to the user who owns this calculation."""
        return Column(
            UUID(as_uuid=True),
            ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
            index=True
        )

    @declared_attr
    def type(cls):
        """Discriminator column for polymorphic inheritance."""
        return Column(
            String(50),
            nullable=False,
            index=True
        )

    @declared_attr
    def inputs(cls):
        """JSON column storing the list of numbers for the calculation."""
        return Column(
            JSON,
            nullable=False
        )

    @declared_attr
    def result(cls):
        """The computed result of the calculation."""
        return Column(
            Float,
            nullable=True
        )

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def user(cls):
        """Relationship to the User model."""
        return relationship("User", back_populates="calculations")

    @classmethod
    def create(cls, calculation_type: str, user_id: uuid.UUID,
                inputs: List[float]) -> "Calculation":
        """
        Factory method to create the appropriate calculation subclass.
        This implements the (optional) Factory Pattern.
        """
        calculation_classes = {
            'addition': Addition,
            'subtraction': Subtraction,
            'multiplication': Multiplication,
            'division': Division,
        }
        calculation_class = calculation_classes.get(calculation_type.lower())
        if not calculation_class:
            raise ValueError(
                f"Unsupported calculation type: {calculation_type}"
            )
        
        # Create instance and pre-calculate result
        instance = calculation_class(user_id=user_id, inputs=inputs)
        instance.result = instance.get_result() # Store result in DB
        return instance

    def get_result(self) -> float:
        """Abstract method to compute the calculation result."""
        raise NotImplementedError(
            "Subclasses must implement get_result() method"
        )

    def __repr__(self):
        return f"<Calculation(type={self.type}, inputs={self.inputs})>"


class Calculation(Base, AbstractCalculation):
    """Base calculation model with polymorphic configuration."""
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation",
    }


class Addition(Calculation):
    """Addition calculation subclass."""
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list) or len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        return sum(self.inputs)


class Subtraction(Calculation):
    """Subtraction calculation subclass."""
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list) or len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        result = self.inputs[0]
        for value in self.inputs[1:]:
            result -= value
        return result


class Multiplication(Calculation):
    """Multiplication calculation subclass."""
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list) or len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        result = 1
        for value in self.inputs:
            result *= value
        return result


class Division(Calculation):
    """Division calculation subclass."""
    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list) or len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        result = self.inputs[0]
        for value in self.inputs[1:]:
            if value == 0:
                raise ValueError("Cannot divide by zero.")
            result /= value
        return result