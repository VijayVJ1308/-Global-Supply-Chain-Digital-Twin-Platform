"""
Logging & Observability Utility for Global Supply Chain Digital Twin Platform.
Provides structured logging and optional Prometheus metrics reporting.
"""

import logging
import sys
import json
from datetime import datetime

class StructuredLogger:
    """Custom logger emitting JSON formatted structured logs."""
    
    def __init__(self, name: str = "SupplyChainDigitalTwin"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def info(self, msg: str, **kwargs):
        payload = {"message": msg, "level": "INFO", "timestamp": datetime.utcnow().isoformat(), **kwargs}
        self.logger.info(json.dumps(payload) if kwargs else msg)
        
    def error(self, msg: str, **kwargs):
        payload = {"message": msg, "level": "ERROR", "timestamp": datetime.utcnow().isoformat(), **kwargs}
        self.logger.error(json.dumps(payload) if kwargs else msg)
        
    def warning(self, msg: str, **kwargs):
        payload = {"message": msg, "level": "WARNING", "timestamp": datetime.utcnow().isoformat(), **kwargs}
        self.logger.warning(json.dumps(payload) if kwargs else msg)

def get_logger(name: str = "SupplyChainLogger") -> StructuredLogger:
    return StructuredLogger(name)
