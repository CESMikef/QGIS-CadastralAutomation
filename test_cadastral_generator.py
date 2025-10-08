"""
Unit tests for cadastral_generator.py
Run with: python -m pytest test_cadastral_generator.py
"""

import pytest
from qgis.core import QgsVectorLayer
from qgis.testing import start_app
from cadastral_generator import Config

# Initialize QGIS application for testing
QGIS_APP = start_app()


class TestConfig:
    """Test configuration validation"""
    
    def test_valid_config(self):
        """Test valid configuration"""
        config = Config()
        assert config.validate() is True
    
    def test_invalid_buffer_distance(self):
        """Test invalid buffer distance"""
        config = Config()
        config.ROAD_BUFFER_METERS = -5
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_min_area(self):
        """Test invalid minimum area"""
        config = Config()
        config.MIN_AREA_SQM = -100
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_max_area(self):
        """Test invalid maximum area"""
        config = Config()
        config.MAX_AREA_SQM = -100
        with pytest.raises(ValueError):
            config.validate()
    
    def test_min_greater_than_max(self):
        """Test minimum area greater than maximum"""
        config = Config()
        config.MIN_AREA_SQM = 1000
        config.MAX_AREA_SQM = 500
        with pytest.raises(ValueError):
            config.validate()


class TestLayerOperations:
    """Test layer operations (requires QGIS)"""
    
    def test_config_types(self):
        """Test configuration parameter types"""
        config = Config()
        assert isinstance(config.ROAD_BUFFER_METERS, (int, float))
        assert isinstance(config.MIN_AREA_SQM, (int, float))
        assert isinstance(config.MAX_AREA_SQM, (int, float))
        assert isinstance(config.TARGET_CRS, str)


if __name__ == '__main__':
    pytest.main([__file__])
