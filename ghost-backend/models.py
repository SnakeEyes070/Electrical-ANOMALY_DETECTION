from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pydantic.functional_validators import field_validator
from pydantic_core import core_schema

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class SensorData(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    sensor_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    voltage: float = Field(..., ge=0, le=500)  # 0-500V range
    current: float = Field(..., ge=0, le=100)   # 0-100A range
    power: float = Field(...)
    temperature: float = Field(...)
    frequency: Optional[float] = None
    power_factor: Optional[float] = None
    location: Optional[dict] = None
    node_id: str = Field(...)
    transformer_id: Optional[str] = None
    
    # Pydantic V2 model config
    model_config = ConfigDict(
        populate_by_name=True,  # formerly allow_population_by_field_name
        arbitrary_types_allowed=True,
        json_schema_extra={  # formerly schema_extra
            "example": {
                "sensor_id": "ESP32_001",
                "voltage": 230.5,
                "current": 15.2,
                "power": 3502.6,
                "temperature": 42.3,
                "node_id": "node_001",
                "transformer_id": "transformer_A"
            }
        }
    )
    
    @field_validator('power', mode='before')
    @classmethod
    def calculate_power_if_missing(cls, v, info):
        """Calculate power if not provided"""
        if v is None and 'voltage' in info.data and 'current' in info.data:
            return info.data['voltage'] * info.data['current']
        return v

class AnomalyAlert(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    alert_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sensor_id: str = Field(...)
    alert_type: str = Field(..., description="theft|overload|temperature|voltage_drop")
    severity: str = Field(..., description="low|medium|high|critical")
    message: str = Field(...)
    value: float = Field(...)
    threshold: float = Field(...)
    location: dict = Field(...)
    status: str = Field(default="active", description="active|acknowledged|resolved")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class HealthScore(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    node_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    score: float = Field(..., ge=0, le=100)
    components: dict = Field(...)
    recommendations: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )