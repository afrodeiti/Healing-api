#!/usr/bin/env python3
"""
Sacred Computing Platform - Comprehensive Implementation

A complete Python implementation of the Sacred Computing Platform including:
- Sacred geometry visualization and calculations
- Intention broadcasting via network packets
- Healing code database
- Soul archive storage
- WebSocket server for real-time energetic feedback
- Web API endpoints

This single file contains all functionality of the web application
consolidated for local use and study.

Usage:
  python sacred_computing_platform.py --mode server  # Run server mode
  python sacred_computing_platform.py --mode broadcast --intention "Healing and peace"  # Broadcast intention
  python sacred_computing_platform.py --mode calculate --intention "Healing" --field-type torus  # Calculate sacred geometry
"""

import argparse
import asyncio
import base64
import hashlib
import http.server
import io
import json
import logging
import math
import os
import random
import secrets
import socketserver
import sqlite3
import sys
import threading
import time
import uuid
import webbrowser
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, Set, Callable

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sacred-computing')

# Web server port
SERVER_PORT = 8000

#########################################
# CORE SACRED GEOMETRY CONSTANTS & ENUMS
#########################################

# Sacred Constants
PHI = (1 + 5 ** 0.5) / 2  # Golden Ratio (1.618...)
SQRT3 = 3 ** 0.5          # Used in Vesica Piscis and Star Tetrahedron
SQRT2 = 2 ** 0.5          # Used in Octahedron
SCHUMANN_RESONANCE = 7.83 # Earth's primary resonance frequency

# Sacred Number Sequences
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
METATRON = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48]  # Tesla's 3-6-9 sequence
SOLFEGGIO = [396, 417, 528, 639, 741, 852, 963]  # Solfeggio frequencies

# Planetary geometric relationships (angular positions)
PLANETARY_ANGLES = {
    "sun": 0,
    "moon": 30,
    "mercury": 60,
    "venus": 90,
    "mars": 120,
    "jupiter": 150,
    "saturn": 180,
    "uranus": 210,
    "neptune": 240,
    "pluto": 270
}

class PacketType(Enum):
    """Network packet types for sacred intention transmission"""
    DATA = 0
    INTENTION = 1
    SACRED_GEOMETRY = 2
    FIELD_HARMONICS = 3
    QUANTUM_RESONANCE = 4


class SacredGeometryField(Enum):
    """Sacred geometry field types"""
    TORUS = "torus"
    MERKABA = "merkaba"
    METATRON = "metatron"
    SRI_YANTRA = "sri_yantra"
    FLOWER_OF_LIFE = "flower_of_life"


class WSMessageType(Enum):
    """WebSocket message types"""
    INTENTION = "INTENTION"
    TORUS_FIELD = "TORUS_FIELD"
    MERKABA = "MERKABA"
    METATRON = "METATRON"
    SRI_YANTRA = "SRI_YANTRA"
    FLOWER_OF_LIFE = "FLOWER_OF_LIFE"
    NETWORK_PACKET = "NETWORK_PACKET"
    SYSTEM = "SYSTEM"


# Global sequence counter for packet IDs
SEQUENCE_COUNTER = 0

# Connected WebSocket clients
WEBSOCKET_CLIENTS = set()


#########################################
# NETWORK PACKET IMPLEMENTATION
#########################################

class PacketHeader:
    """IEEE 802.11 inspired packet header for intention transmission"""
    
    def __init__(self, packet_type: PacketType, payload_length: int):
        global SEQUENCE_COUNTER
        self.version = 1
        self.type = packet_type.value
        self.length = payload_length
        self.sequence_id = SEQUENCE_COUNTER
        SEQUENCE_COUNTER += 1
        self.timestamp = int(time.time() * 1000)  # milliseconds
        self.checksum = None  # Will be calculated later
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert header to dictionary for JSON serialization"""
        return {
            "version": self.version,
            "type": self.type,
            "length": self.length,
            "sequenceId": self.sequence_id,
            "timestamp": self.timestamp,
            "checksum": self.checksum
        }


class IntentionPacket:
    """Complete network packet with intention data"""
    
    def __init__(
        self, 
        intention: str,
        frequency: float = SCHUMANN_RESONANCE,
        field_type: str = "torus",
        target_device: str = "broadcast"
    ):
        self.intention = intention
        self.frequency = frequency
        self.field_type = field_type
        self.target_device = target_device
        
        # Create energy signature with quantum noise
        self.energy_signature = secrets.token_hex(8)
        
        # Generate quantum entanglement key
        self.quantum_key = secrets.token_hex(16)
        
        # Calculate intention strength based on frequency and length
        self.intention_strength = min((len(intention) * frequency) / 100, 100)
        
        # Create packet payload
        self.payload = {
            "intention": intention,
            "frequency": frequency,
            "field_type": field_type,
            "energy_signature": self.energy_signature,
            "quantum_entanglement_key": self.quantum_key
        }
        
        # Create header
        payload_str = json.dumps(self.payload)
        self.header = PacketHeader(PacketType.INTENTION, len(payload_str))
        
        # Calculate checksum
        self.header.checksum = self._calculate_checksum(payload_str)
        
        # Metadata
        self.metadata = {
            "source_device": "sacred-python-platform",
            "target_device": target_device,
            "intention_strength": self.intention_strength,
            "sacred_encoding": "merkaba-torus-fibonacci"
        }
    
    def _calculate_checksum(self, payload: str) -> str:
        """Calculate SHA-256 checksum of payload"""
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for JSON serialization"""
        return {
            "header": self.header.to_dict(),
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert packet to JSON string"""
        return json.dumps(self.to_dict())
    
    def to_base64(self) -> str:
        """Convert packet to base64 string (for network transmission)"""
        return base64.b64encode(self.to_json().encode('utf-8')).decode('utf-8')


def extract_intention_from_packet(packet_base64: str) -> Optional[str]:
    """Extract intention from a base64-encoded packet (for receiving devices)"""
    try:
        # Decode from base64
        json_str = base64.b64decode(packet_base64).decode('utf-8')
        packet = json.loads(json_str)
        
        # Extract intention
        return packet["payload"]["intention"]
    except Exception as e:
        logger.error(f"Failed to extract intention from packet: {e}")
        return None


async def embed_intention_in_network_packet(
    intention: str, 
    frequency: float = SCHUMANN_RESONANCE,
    field_type: str = "torus"
) -> str:
    """Embed intention in network packet and return base64 string"""
    packet = IntentionPacket(intention, frequency, field_type)
    return packet.to_base64()


#########################################
# SACRED GEOMETRY CALCULATIONS
#########################################

class SacredGeometryCalculator:
    """Sacred geometry calculations for various fields and patterns"""
    
    @staticmethod
    async def divine_proportion_amplify(intention: str, multiplier: float = 1.0) -> Dict[str, Any]:
        """Amplify intention using divine proportion (PHI)"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        
        # Calculate hash using SHA-512
        intention_hash = hashlib.sha512(intention.encode('utf-8')).hexdigest()
        
        # Use PHI spiral to generate fibonacci-aligned energetic signature
        phi_segments = []
        for i in range(len(intention_hash)):
            char_code = ord(intention_hash[i])
            segment_value = char_code * (PHI ** ((i % 7) + 1))
            phi_segments.append(f"{int(segment_value % 100):02d}")
        
        amplified = ''.join(phi_segments)
        
        # Create a phi-spiral encoding with the intention
        spiral_hash_data = amplified + intention
        spiral_hash = hashlib.sha256(spiral_hash_data.encode('utf-8')).hexdigest()
        
        # Apply the multiplier using the closest Fibonacci number
        fib_multiplier = next((f for f in FIBONACCI if f >= multiplier), FIBONACCI[-1])
        
        # Calculate Tesla's 3-6-9 principle (sum of char codes modulo 9, or 9 if result is 0)
        metatronic_alignment = sum(ord(c) for c in intention) % 9 or 9
        
        return {
            "original": intention,
            "phi_amplified": spiral_hash,
            "fibonacci_multiplier": fib_multiplier,
            "metatronic_alignment": metatronic_alignment
        }
    
    @staticmethod
    async def merkaba_field_generator(intention: str, frequency: float) -> Dict[str, Any]:
        """Generate merkaba field data based on intention and frequency"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        
        # Create counter-rotating tetrahedrons (male/female energies)
        tetra_up_data = intention + "ascend"
        tetra_up = hashlib.sha256(tetra_up_data.encode('utf-8')).hexdigest()[:12]
        
        tetra_down_data = intention + "descend"
        tetra_down = hashlib.sha256(tetra_down_data.encode('utf-8')).hexdigest()[:12]
        
        # Determine the right spin frequency using solfeggio relationship
        closest_solfeggio = min(SOLFEGGIO, key=lambda x: abs(x - frequency * 100))
        
        # Calculate the merkaba field intensity (sacred geometry)
        field_intensity = ((frequency * SQRT3) / PHI) * (frequency % 9 or 9)
        
        return {
            "intention": intention,
            "tetra_up": tetra_up,
            "tetra_down": tetra_down,
            "merkaba_frequency": frequency,
            "solfeggio_alignment": closest_solfeggio,
            "field_intensity": field_intensity,
            "activation_code": f"{math.floor(field_intensity)} {math.floor(frequency * PHI)} {math.floor(closest_solfeggio / PHI)}"
        }
    
    @staticmethod
    async def flower_of_life_pattern(intention: str, duration: int) -> Dict[str, Any]:
        """Generate Flower of Life pattern based on intention and duration"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        
        # Calculate the cosmic timing (astrological alignment)
        now = datetime.now()
        cosmic_degree = (now.hour * 15) + (now.minute / 4)  # 24 hours = 360 degrees
        
        # Find planetary alignment
        closest_planet = "sun"
        closest_degree = 360
        
        for planet, angle in PLANETARY_ANGLES.items():
            diff = abs(angle - cosmic_degree)
            if diff < closest_degree:
                closest_degree = diff
                closest_planet = planet
        
        # Generate the seven interlocking circles of the Seed of Life
        seed_patterns = []
        for i in range(7):
            angle = i * (360 / 7)
            radius = (i + 1) * PHI
            seed_data = f"{intention}:{angle}:{radius}"
            seed_hash = hashlib.sha256(seed_data.encode('utf-8')).hexdigest()[:8]
            seed_patterns.append(seed_hash)
        
        # Create the full Flower of Life pattern with 19 overlapping circles
        fol_pattern = ''.join(seed_patterns)
        
        # Calculate optimal duration based on Flower of Life geometry
        optimal_duration = max(duration, int(duration * PHI))
        
        return {
            "intention": intention,
            "flower_pattern": fol_pattern,
            "planetary_alignment": closest_planet,
            "cosmic_degree": cosmic_degree,
            "optimal_duration": optimal_duration,
            "vesica_pisces_code": f"{seed_patterns[0]} {seed_patterns[3]} {seed_patterns[6]}"
        }
    
    @staticmethod
    async def metatrons_cube_amplifier(intention: str, boost: bool = False) -> Dict[str, Any]:
        """Generate Metatron's Cube data based on intention"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        
        # The 13 spheres of Metatron's Cube (Archangel Metatron's energy)
        intention_spheres = []
        
        # Create the 13 information spheres in the pattern of Metatron's Cube
        for i in range(13):
            sphere_data = intention + str(METATRON[i % len(METATRON)])
            sphere_hash = hashlib.sha512(sphere_data.encode('utf-8')).hexdigest()[:6]
            intention_spheres.append(sphere_hash)
        
        # Connect the spheres with 78 lines representing consciousness pathways
        if boost:
            # Activate the full Metatronic grid (all 78 lines)
            metatron_code = ''.join(intention_spheres)
        else:
            # Activate partial grid (only the primary 22 lines)
            metatron_code = ''.join(intention_spheres[:5])
        
        # Calculate the Cube's harmonic frequency (Tesla 3-6-9 principle)
        harmonic = sum(ord(c) for c in intention) % 9 or 9  # Tesla's completion number
        
        return {
            "intention": intention,
            "metatron_code": metatron_code,
            "harmonic": harmonic,
            "platonic_solids": {
                "tetrahedron": intention_spheres[0],
                "hexahedron": intention_spheres[1],
                "octahedron": intention_spheres[2],
                "dodecahedron": intention_spheres[3],
                "icosahedron": intention_spheres[4]
            },
            "activation_key": f"{harmonic * 3}-{harmonic * 6}-{harmonic * 9}"
        }
    
    @staticmethod
    async def torus_field_generator(intention: str, hz: float = SCHUMANN_RESONANCE) -> Dict[str, Any]:
        """Generate torus field data based on intention and frequency"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        if hz <= 0:
            raise ValueError("Frequency must be positive")
        
        # Map frequency to the optimal torus ratio based on Earth's Schumann resonance
        schumann_ratio = hz / SCHUMANN_RESONANCE
        
        # Generate the torus inner and outer flows (energy circulation patterns)
        inner_flow_data = intention + "inner"
        inner_flow = hashlib.sha512(inner_flow_data.encode('utf-8')).hexdigest()[:12]
        
        outer_flow_data = intention + "outer"
        outer_flow = hashlib.sha512(outer_flow_data.encode('utf-8')).hexdigest()[:12]
        
        # Calculate the phase angle for maximum resonance
        phase_angle = (hz * 360) % 360
        
        # Determine the coherence ratio (based on cardiac coherence principles)
        coherence = 0.618 * schumann_ratio  # 0.618 is the inverse of the golden ratio
        
        # Find the closest Tesla number (3, 6, or 9) for the torus power node
        tesla_nodes = [3, 6, 9]
        tesla_node = min(tesla_nodes, key=lambda x: abs(x - (hz % 10)))
        
        return {
            "intention": intention,
            "torus_frequency": hz,
            "schumann_ratio": f"{schumann_ratio:.3f}",
            "inner_flow": inner_flow,
            "outer_flow": outer_flow,
            "phase_angle": phase_angle,
            "coherence": f"{coherence:.3f}",
            "tesla_node": tesla_node,
            "activation_sequence": f"{tesla_node}{tesla_node}{inner_flow[:tesla_node]}"
        }
    
    @staticmethod
    async def sri_yantra_encoder(intention: str) -> Dict[str, Any]:
        """Generate Sri Yantra data based on intention"""
        if not intention:
            raise ValueError("Intention cannot be empty")
        
        # The 9 interlocking triangles of the Sri Yantra
        triangles = []
        
        for i in range(9):
            if i % 2 == 0:  # Shiva (masculine) triangles point downward
                triangle_data = intention + f"shiva{i}"
            else:  # Shakti (feminine) triangles point upward
                triangle_data = intention + f"shakti{i}"
            
            triangle_hash = hashlib.sha256(triangle_data.encode('utf-8')).hexdigest()[:8]
            triangles.append(triangle_hash)
        
        # Generate the 43 intersecting points of power (marmas)
        marma_data = ''.join(triangles)
        marma_points = hashlib.sha512(marma_data.encode('utf-8')).hexdigest()
        
        # Calculate the central bindu point (singularity/unity consciousness)
        bindu_data = intention + "bindu"
        bindu = hashlib.sha256(bindu_data.encode('utf-8')).hexdigest()[:9]
        
        # Map to the 9 surrounding circuits (avaranas) for complete encoding
        circuits = []
        for i in range(9):
            circuit_data = triangles[i] + bindu
            circuit = hashlib.sha256(circuit_data.encode('utf-8')).hexdigest()[:6]
            circuits.append(circuit)
        
        return {
            "intention": intention,
            "triangles": triangles,
            "bindu": bindu,
            "circuits": circuits,
            "inner_triangle": triangles[0],
            "outer_triangle": triangles[8],
            "yantra_code": f"{bindu[:3]}-{triangles[0][:3]}-{triangles[8][:3]}"
        }


#########################################
# STORAGE IMPLEMENTATION
#########################################

class SacredStorage:
    """Storage for healing codes, soul archives, and users"""
    
    def __init__(self, db_path: str = 'sacred_computing.db'):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Set up database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        
        # Soul Archive table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS soul_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            intention TEXT,
            frequency TEXT NOT NULL,
            boost INTEGER,
            multiplier INTEGER,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Healing Code table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS healing_code (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            category TEXT
        )
        ''')
        
        conn.commit()
        
        # Initialize with sample healing codes if table is empty
        cursor.execute('SELECT COUNT(*) FROM healing_code')
        count = cursor.fetchone()[0]
        if count == 0:
            self._initialize_healing_codes(cursor, conn)
        
        conn.close()
    
    def _initialize_healing_codes(self, cursor, conn):
        """Initialize with sample healing codes"""
        sample_codes = [
            ("23 74 555", "Healing headaches in general", "CENTRAL NERVOUS SYSTEM"),
            ("58 33 554", "Healing migraine", "CENTRAL NERVOUS SYSTEM"),
            ("71 81 533", "Back pain relief", "CENTRAL NERVOUS SYSTEM"),
            ("33 45 10101", "Forgiveness", "PSYCHOLOGICAL CONCERNS"),
            ("11 96 888", "Low self-esteem to healthy self-image", "SELF-HELP"),
            ("8888", "Divine protection", "SPIRITUAL"),
            ("13 13 514", "Stress relief/relaxation", "SELF-HELP"),
            ("517 489719 841", "Increase self-confidence", "SELF-HELP"),
            ("56 57 893", "Unconditional love", "RELATIONSHIPS"),
            ("888 412 1289018", "Love (general & relationships)", "RELATIONSHIPS")
        ]
        
        cursor.executemany(
            'INSERT INTO healing_code (code, description, category) VALUES (?, ?, ?)',
            sample_codes
        )
        conn.commit()
    
    # User methods
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1]
            }
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1]
            }
        return None
    
    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hash the password (in a real system, use better password hashing)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': user_id,
            'username': username
        }
    
    # Soul Archive methods
    def get_soul_archives(self) -> List[Dict[str, Any]]:
        """Get all soul archives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM soul_archive ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'title', 'description', 'intention', 'frequency', 
                 'boost', 'multiplier', 'pattern_type', 'pattern_data', 'created_at']
        
        archives = []
        for row in rows:
            archive = dict(zip(columns, row))
            archive['boost'] = bool(archive['boost'])
            archive['pattern_data'] = json.loads(archive['pattern_data'])
            archives.append(archive)
        
        return archives
    
    def get_soul_archive_by_id(self, archive_id: int) -> Optional[Dict[str, Any]]:
        """Get soul archive by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM soul_archive WHERE id = ?', (archive_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'title', 'description', 'intention', 'frequency', 
                     'boost', 'multiplier', 'pattern_type', 'pattern_data', 'created_at']
            archive = dict(zip(columns, row))
            archive['boost'] = bool(archive['boost'])
            archive['pattern_data'] = json.loads(archive['pattern_data'])
            return archive
        return None
    
    def create_soul_archive(
        self,
        title: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        description: Optional[str] = None,
        intention: Optional[str] = None,
        frequency: str = str(SCHUMANN_RESONANCE),
        boost: Optional[bool] = False,
        multiplier: Optional[int] = 1
    ) -> Dict[str, Any]:
        """Create a new soul archive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO soul_archive 
            (title, description, intention, frequency, boost, multiplier, pattern_type, pattern_data) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                title, 
                description, 
                intention, 
                frequency, 
                1 if boost else 0, 
                multiplier, 
                pattern_type, 
                json.dumps(pattern_data)
            )
        )
        archive_id = cursor.lastrowid
        conn.commit()
        
        # Get the created archive with datetime
        cursor.execute('SELECT * FROM soul_archive WHERE id = ?', (archive_id,))
        row = cursor.fetchone()
        conn.close()
        
        columns = ['id', 'title', 'description', 'intention', 'frequency', 
                 'boost', 'multiplier', 'pattern_type', 'pattern_data', 'created_at']
        archive = dict(zip(columns, row))
        archive['boost'] = bool(archive['boost'])
        archive['pattern_data'] = json.loads(archive['pattern_data'])
        
        return archive
    
    def delete_soul_archive(self, archive_id: int) -> bool:
        """Delete a soul archive"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM soul_archive WHERE id = ?', (archive_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    # Healing Code methods
    def get_healing_codes(self) -> List[Dict[str, Any]]:
        """Get all healing codes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, code, description, category FROM healing_code')
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'code': row[1],
                'description': row[2],
                'category': row[3]
            }
            for row in rows
        ]
    
    def get_healing_codes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get healing codes by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, code, description, category FROM healing_code WHERE category = ?',
            (category,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'code': row[1],
                'description': row[2],
                'category': row[3]
            }
            for row in rows
        ]
    
    def search_healing_codes(self, query: str) -> List[Dict[str, Any]]:
        """Search healing codes"""
        if not query:
            return self.get_healing_codes()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute(
            '''
            SELECT id, code, description, category FROM healing_code 
            WHERE code LIKE ? OR description LIKE ? OR category LIKE ?
            ''',
            (search_pattern, search_pattern, search_pattern)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'code': row[1],
                'description': row[2],
                'category': row[3]
            }
            for row in rows
        ]
    
    def create_healing_code(
        self, 
        code: str, 
        description: str, 
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new healing code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO healing_code (code, description, category) VALUES (?, ?, ?)',
            (code, description, category)
        )
        code_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': code_id,
            'code': code,
            'description': description,
            'category': category
        }


#########################################
# VISUALIZATION FUNCTIONS
#########################################

class SacredVisualizer:
    """Sacred geometry visualizations"""
    
    @staticmethod
    def generate_torus_points(radius_outer: float = 3.0, radius_inner: float = 1.0, 
                             n_points: int = 100) -> Tuple[List[float], List[float], List[float]]:
        """Generate 3D points for a torus"""
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and numpy")
        
        u = np.linspace(0, 2 * np.pi, n_points)
        v = np.linspace(0, 2 * np.pi, n_points)
        u_grid, v_grid = np.meshgrid(u, v)
        
        x = (radius_outer + radius_inner * np.cos(v_grid)) * np.cos(u_grid)
        y = (radius_outer + radius_inner * np.cos(v_grid)) * np.sin(u_grid)
        z = radius_inner * np.sin(v_grid)
        
        return x, y, z
    
    @staticmethod
    def generate_merkaba_vertices(size: float = 100.0) -> Dict[str, List[Tuple[float, float, float]]]:
        """Generate vertices for a merkaba (two tetrahedrons)"""
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and numpy")
        
        # Tetrahedron pointing up (masculine)
        tetra_up = [
            (0, 0, size),
            (size * math.sqrt(8/9), 0, -size/3),
            (-size * math.sqrt(2/9), size * math.sqrt(2/3), -size/3),
            (-size * math.sqrt(2/9), -size * math.sqrt(2/3), -size/3)
        ]
        
        # Tetrahedron pointing down (feminine)
        tetra_down = [
            (0, 0, -size),
            (size * math.sqrt(8/9), 0, size/3),
            (-size * math.sqrt(2/9), size * math.sqrt(2/3), size/3),
            (-size * math.sqrt(2/9), -size * math.sqrt(2/3), size/3)
        ]
        
        return {
            "tetra_up": tetra_up,
            "tetra_down": tetra_down
        }
    
    @staticmethod
    def generate_flower_of_life_points(radius: float = 100.0, 
                                      levels: int = 7) -> List[Tuple[float, float, float]]:
        """Generate points for the Flower of Life pattern"""
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and numpy")
        
        centers = [(0, 0, 0)]  # Center point
        
        # Generate the pattern of circles
        for level in range(1, levels + 1):
            for i in range(6):
                angle = i * (2 * math.pi / 6)
                x = level * radius * math.cos(angle)
                y = level * radius * math.sin(angle)
                centers.append((x, y, 0))
                
                # Add intermediate circles
                if level > 1:
                    angle1 = i * (2 * math.pi / 6)
                    angle2 = ((i + 1) % 6) * (2 * math.pi / 6)
                    x = level * radius * 0.5 * (math.cos(angle1) + math.cos(angle2))
                    y = level * radius * 0.5 * (math.sin(angle1) + math.sin(angle2))
                    centers.append((x, y, 0))
        
        return centers
    
    @staticmethod
    def generate_sri_yantra_geometry(size: float = 100.0) -> Dict[str, Any]:
        """Generate geometry for Sri Yantra"""
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and numpy")
        
        # Define the triangles (simplified)
        triangles = []
        
        # Outer square
        square = [
            (-size, -size, 0), (size, -size, 0),
            (size, size, 0), (-size, size, 0)
        ]
        
        # Inner triangles (simplified representation)
        for i in range(9):
            scale = 0.9 - (i * 0.1)
            if i % 2 == 0:  # Shiva triangles point downward
                triangle = [
                    (0, size * scale, 0),
                    (-size * scale * 0.866, -size * scale * 0.5, 0),
                    (size * scale * 0.866, -size * scale * 0.5, 0)
                ]
            else:  # Shakti triangles point upward
                triangle = [
                    (0, -size * scale, 0),
                    (-size * scale * 0.866, size * scale * 0.5, 0),
                    (size * scale * 0.866, size * scale * 0.5, 0)
                ]
            triangles.append(triangle)
        
        # Central bindu (point)
        bindu = [(0, 0, 0)]
        
        return {
            "square": square,
            "triangles": triangles,
            "bindu": bindu
        }
    
    @staticmethod
    def generate_metatrons_cube(size: float = 100.0) -> Dict[str, Any]:
        """Generate geometry for Metatron's Cube"""
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and numpy")
        
        # The 13 spheres
        spheres = [(0, 0, 0)]  # Central sphere
        
        # First ring of 6 spheres
        for i in range(6):
            angle = i * (2 * math.pi / 6)
            x = size * math.cos(angle)
            y = size * math.sin(angle)
            spheres.append((x, y, 0))
        
        # Second ring of 6 spheres (offset)
        for i in range(6):
            angle = (i * (2 * math.pi / 6)) + (math.pi / 6)
            x = size * 1.5 * math.cos(angle)
            y = size * 1.5 * math.sin(angle)
            spheres.append((x, y, 0))
        
        # Generate lines connecting the spheres
        lines = []
        for i in range(len(spheres)):
            for j in range(i + 1, len(spheres)):
                lines.append((spheres[i], spheres[j]))
        
        # Platonic solids vertices (simplified)
        platonic = {
            "tetrahedron": [
                (0, 0, size), 
                (size * math.sqrt(8/9), 0, -size/3),
                (-size * math.sqrt(2/9), size * math.sqrt(2/3), -size/3),
                (-size * math.sqrt(2/9), -size * math.sqrt(2/3), -size/3)
            ],
            "cube": [
                (size/2, size/2, size/2), (size/2, size/2, -size/2),
                (size/2, -size/2, size/2), (size/2, -size/2, -size/2),
                (-size/2, size/2, size/2), (-size/2, size/2, -size/2),
                (-size/2, -size/2, size/2), (-size/2, -size/2, -size/2)
            ]
        }
        
        return {
            "spheres": spheres,
            "lines": lines,
            "platonic": platonic
        }
    
    @staticmethod
    def visualize_torus(data: Dict[str, Any], filename: str = "torus.png") -> str:
        """Create torus visualization based on data"""
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and numpy")
        
        # Extract parameters
        intention = data.get("intention", "Peace")
        frequency = float(data.get("torus_frequency", SCHUMANN_RESONANCE))
        ratio = float(data.get("schumann_ratio", 1.0))
        inner_flow = data.get("inner_flow", "")
        
        # Generate color from inner flow
        color_value = int(inner_flow[:6], 16) if inner_flow else 0x0000FF
        r = ((color_value >> 16) & 0xFF) / 255.0
        g = ((color_value >> 8) & 0xFF) / 255.0
        b = (color_value & 0xFF) / 255.0
        
        # Create figure
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Generate torus
        r_outer = 3.0 * ratio
        r_inner = 1.0 * ratio
        x, y, z = SacredVisualizer.generate_torus_points(r_outer, r_inner)
        
        # Plot the torus
        ax.plot_surface(x, y, z, color=(r, g, b, 0.7), rstride=5, cstride=5, alpha=0.7)
        
        # Set viewpoint
        ax.view_init(elev=30, azim=45)
        ax.set_box_aspect([1, 1, 1])
        ax.set_axis_off()
        
        # Add title
        plt.title(f"Torus Field: '{intention}'\nFrequency: {frequency} Hz")
        
        # Save image and return filename
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename


#########################################
# WEBSOCKET SERVER
#########################################

class WSMessage:
    """WebSocket message with type, data, and timestamp"""
    
    def __init__(self, msg_type: WSMessageType, data: Any):
        self.type = msg_type.value
        self.data = data
        self.timestamp = datetime.now().isoformat()
        self.packet_data = None  # For network packet transmissions
    
    async def add_packet_data(self, intention: str, frequency: float = SCHUMANN_RESONANCE):
        """Add network packet data for intention broadcasting"""
        if self.type == WSMessageType.INTENTION.value and intention:
            try:
                self.packet_data = await embed_intention_in_network_packet(
                    intention,
                    frequency
                )
            except Exception as e:
                logger.error(f"Failed to embed intention in network packet: {e}")
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp,
            "packetData": self.packet_data
        })


async def broadcast_message(message: WSMessage):
    """Broadcast message to all connected WebSocket clients"""
    if not WEBSOCKET_CLIENTS:
        return
    
    # Check if this is an intention that should be embedded in network packets
    if (message.type == WSMessageType.INTENTION.value and 
            isinstance(message.data, dict) and
            "intention" in message.data):
        
        # Embed intention in network packet format
        await message.add_packet_data(
            message.data["intention"],
            message.data.get("frequency", SCHUMANN_RESONANCE)
        )
    
    message_str = message.to_json()
    
    # Broadcast to all connected clients
    for websocket in list(WEBSOCKET_CLIENTS):
        try:
            await websocket.send(message_str)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
            WEBSOCKET_CLIENTS.discard(websocket)


async def handle_websocket(websocket, path, storage: SacredStorage):
    """Handle WebSocket connection"""
    try:
        # Add client to set
        WEBSOCKET_CLIENTS.add(websocket)
        
        # Send welcome message
        welcome_msg = WSMessage(
            WSMessageType.SYSTEM,
            {"message": "Connected to Sacred Computing Platform"}
        )
        await websocket.send(welcome_msg.to_json())
        
        async for message in websocket:
            try:
                parsed_message = json.loads(message)
                
                # Process different message types
                if parsed_message["type"] == WSMessageType.INTENTION.value:
                    data = parsed_message["data"]
                    intention = data.get("intention", "")
                    frequency = data.get("frequency", SCHUMANN_RESONANCE)
                    boost = data.get("boost", False)
                    multiplier = data.get("multiplier", 1)
                    
                    # Response to send back
                    response = WSMessage(
                        WSMessageType.INTENTION,
                        {
                            "message": f"Intention '{intention}' processed",
                            "intention": intention,
                            "frequency": frequency,
                            "boost": boost,
                            "multiplier": multiplier
                        }
                    )
                    
                    await broadcast_message(response)
                    
                    # Generate sacred geometry data based on the intention
                    if intention:
                        # Generate torus field after a short delay
                        await asyncio.sleep(0.5)
                        torus_data = await SacredGeometryCalculator.torus_field_generator(
                            intention, frequency
                        )
                        torus_msg = WSMessage(WSMessageType.TORUS_FIELD, torus_data)
                        await broadcast_message(torus_msg)
                        
                        # Apply divine amplification if requested
                        if boost:
                            await asyncio.sleep(0.5)
                            amplified_data = await SacredGeometryCalculator.divine_proportion_amplify(
                                intention, multiplier
                            )
                            amplified_msg = WSMessage(
                                WSMessageType.INTENTION,
                                {
                                    "message": f"Divine amplification applied. Fibonacci multiplier: {amplified_data['fibonacci_multiplier']}.",
                                    **amplified_data
                                }
                            )
                            await broadcast_message(amplified_msg)
                
                elif parsed_message["type"] == WSMessageType.MERKABA.value:
                    data = parsed_message["data"]
                    intention = data.get("intention", "")
                    frequency = data.get("frequency", SCHUMANN_RESONANCE)
                    
                    merkaba_data = await SacredGeometryCalculator.merkaba_field_generator(
                        intention, frequency
                    )
                    merkaba_msg = WSMessage(WSMessageType.MERKABA, merkaba_data)
                    await broadcast_message(merkaba_msg)
                
                elif parsed_message["type"] == WSMessageType.METATRON.value:
                    data = parsed_message["data"]
                    intention = data.get("intention", "")
                    boost = data.get("boost", False)
                    
                    metatron_data = await SacredGeometryCalculator.metatrons_cube_amplifier(
                        intention, boost
                    )
                    metatron_msg = WSMessage(WSMessageType.METATRON, metatron_data)
                    await broadcast_message(metatron_msg)
                
                elif parsed_message["type"] == WSMessageType.SRI_YANTRA.value:
                    data = parsed_message["data"]
                    intention = data.get("intention", "")
                    
                    yantra_data = await SacredGeometryCalculator.sri_yantra_encoder(intention)
                    yantra_msg = WSMessage(WSMessageType.SRI_YANTRA, yantra_data)
                    await broadcast_message(yantra_msg)
                
                elif parsed_message["type"] == WSMessageType.FLOWER_OF_LIFE.value:
                    data = parsed_message["data"]
                    intention = data.get("intention", "")
                    duration = data.get("duration", 60)
                    
                    flower_data = await SacredGeometryCalculator.flower_of_life_pattern(
                        intention, duration
                    )
                    flower_msg = WSMessage(WSMessageType.FLOWER_OF_LIFE, flower_data)
                    await broadcast_message(flower_msg)
                
            except json.JSONDecodeError:
                logger.error("Invalid JSON message")
                await websocket.send(
                    WSMessage(
                        WSMessageType.SYSTEM,
                        {"error": "Invalid message format"}
                    ).to_json()
                )
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send(
                    WSMessage(
                        WSMessageType.SYSTEM,
                        {"error": "Error processing message"}
                    ).to_json()
                )
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Remove client from set when disconnected
        WEBSOCKET_CLIENTS.discard(websocket)


#########################################
# WEB SERVER ROUTES
#########################################

class SacredHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for Sacred Computing Platform"""
    
    def __init__(self, *args, storage=None, **kwargs):
        self.storage = storage
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        # API routes
        if self.path.startswith('/api/'):
            if self.path.startswith('/api/healing-codes'):
                self.handle_healing_codes_get()
            elif self.path.startswith('/api/soul-archives'):
                if '/api/soul-archives/' in self.path and len(self.path.split('/')) > 3:
                    archive_id = int(self.path.split('/')[-1])
                    self.handle_soul_archive_get(archive_id)
                else:
                    self.handle_soul_archives_get()
            else:
                self.send_error(404, "API endpoint not found")
        # Serve static files for web interface
        elif self.path == '/':
            self.serve_html_page('index.html')
        elif self.path.endswith('.js'):
            self.serve_static_file(self.path[1:], 'application/javascript')
        elif self.path.endswith('.css'):
            self.serve_static_file(self.path[1:], 'text/css')
        elif self.path.endswith('.png'):
            self.serve_static_file(self.path[1:], 'image/png')
        elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
            self.serve_static_file(self.path[1:], 'image/jpeg')
        elif self.path.endswith('.html'):
            self.serve_html_page(self.path[1:])
        else:
            # Default to index.html for SPA
            self.serve_html_page('index.html')
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                json_data = json.loads(post_data)
                
                if self.path == '/api/soul-archives':
                    self.handle_soul_archive_post(json_data)
                else:
                    self.send_error(404, "API endpoint not found")
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/api/soul-archives/'):
            try:
                archive_id = int(self.path.split('/')[-1])
                self.handle_soul_archive_delete(archive_id)
            except (ValueError, IndexError):
                self.send_error(400, "Invalid ID")
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_healing_codes_get(self):
        """Handle GET /api/healing-codes"""
        try:
            # Parse query parameters
            query_params = {}
            if '?' in self.path:
                query_string = self.path.split('?')[1]
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=')
                        query_params[key] = value
            
            # Get healing codes
            if 'search' in query_params:
                codes = self.storage.search_healing_codes(query_params['search'])
            elif 'category' in query_params:
                codes = self.storage.get_healing_codes_by_category(query_params['category'])
            else:
                codes = self.storage.get_healing_codes()
            
            self.send_json_response(codes)
        except Exception as e:
            logger.error(f"Error fetching healing codes: {e}")
            self.send_error(500, "Internal server error")
    
    def handle_soul_archives_get(self):
        """Handle GET /api/soul-archives"""
        try:
            archives = self.storage.get_soul_archives()
            self.send_json_response(archives)
        except Exception as e:
            logger.error(f"Error fetching soul archives: {e}")
            self.send_error(500, "Internal server error")
    
    def handle_soul_archive_get(self, archive_id):
        """Handle GET /api/soul-archives/:id"""
        try:
            archive = self.storage.get_soul_archive_by_id(archive_id)
            if archive:
                self.send_json_response(archive)
            else:
                self.send_error(404, "Soul archive not found")
        except Exception as e:
            logger.error(f"Error fetching soul archive: {e}")
            self.send_error(500, "Internal server error")
    
    def handle_soul_archive_post(self, data):
        """Handle POST /api/soul-archives"""
        try:
            required_fields = ['title', 'pattern_type', 'pattern_data']
            for field in required_fields:
                if field not in data:
                    self.send_error(400, f"Missing required field: {field}")
                    return
            
            archive = self.storage.create_soul_archive(
                title=data['title'],
                pattern_type=data['pattern_type'],
                pattern_data=data['pattern_data'],
                description=data.get('description'),
                intention=data.get('intention'),
                frequency=data.get('frequency', str(SCHUMANN_RESONANCE)),
                boost=data.get('boost', False),
                multiplier=data.get('multiplier', 1)
            )
            
            self.send_json_response(archive, status=201)
        except Exception as e:
            logger.error(f"Error creating soul archive: {e}")
            self.send_error(500, "Internal server error")
    
    def handle_soul_archive_delete(self, archive_id):
        """Handle DELETE /api/soul-archives/:id"""
        try:
            success = self.storage.delete_soul_archive(archive_id)
            if success:
                self.send_response(204)
                self.end_headers()
            else:
                self.send_error(404, "Soul archive not found")
        except Exception as e:
            logger.error(f"Error deleting soul archive: {e}")
            self.send_error(500, "Internal server error")
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def serve_html_page(self, filename):
        """Serve HTML page for SPA"""
        # Generate basic HTML with links to the sacred computing React app CDN
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sacred Computing Platform</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {{
            --background: #0f0f0f;
            --foreground: #fafafa;
            --primary: #7f5af0;
            --primary-foreground: #ffffff;
            --secondary: #2a2a2a;
            --accent: #16161a;
            --border: #383838;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--background);
            color: var(--foreground);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border);
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #7f5af0, #2cb67d);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        nav a {{
            color: var(--foreground);
            text-decoration: none;
            margin-left: 1.5rem;
            font-weight: 500;
            transition: color 0.3s ease;
        }}
        
        nav a:hover {{
            color: var(--primary);
        }}
        
        main {{
            flex: 1;
            padding: 2rem;
        }}
        
        .hero {{
            text-align: center;
            padding: 4rem 2rem;
        }}
        
        h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(to right, #7f5af0, #2cb67d);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        p {{
            font-size: 1.2rem;
            max-width: 800px;
            margin: 0 auto 2rem;
            line-height: 1.6;
        }}
        
        .btn {{
            background-color: var(--primary);
            color: var(--primary-foreground);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.375rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
        }}
        
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }}
        
        .card {{
            background-color: var(--secondary);
            border-radius: 0.5rem;
            padding: 1.5rem;
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card h3 {{
            margin-top: 0;
            color: var(--primary);
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            background-color: var(--accent);
            border-top: 1px solid var(--border);
        }}
        
        /* Visualization area */
        .visualization {{
            margin-top: 2rem;
            border-radius: 0.5rem;
            background-color: var(--secondary);
            padding: 1rem;
            text-align: center;
        }}
        
        .visualization-controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1rem;
            justify-content: center;
        }}
        
        .visualization-card {{
            width: 100%;
            height: 400px;
            border-radius: 0.5rem;
            margin-top: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: var(--accent);
            overflow: hidden;
        }}
        
        input, select {{
            background-color: var(--accent);
            border: 1px solid var(--border);
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            color: var(--foreground);
        }}
        
        label {{
            display: block;
            margin-bottom: 0.5rem;
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo">Sacred Computing Platform</div>
        <nav>
            <a href="#intention">Intention</a>
            <a href="#torus">Torus Field</a>
            <a href="#merkaba">Merkaba</a>
            <a href="#healing">Healing Codes</a>
            <a href="#archive">Soul Archive</a>
        </nav>
    </header>
    
    <main>
        <section class="hero">
            <h1>Sacred Geometry Computing</h1>
            <p>Welcome to the integrated platform for sacred geometry visualization, intention broadcasting, and energetic healing through quantum-encoded network packets.</p>
            <a href="#intention" class="btn">Send Intention</a>
        </section>
        
        <div class="container">
            <section id="intention">
                <h2>Broadcast Intention</h2>
                <p>Enter your intention to broadcast it through the quantum field and embed it directly into network packets.</p>
                
                <div class="visualization">
                    <div class="visualization-controls">
                        <div>
                            <label for="intention-input">Intention:</label>
                            <input type="text" id="intention-input" placeholder="Enter your intention..." />
                        </div>
                        
                        <div>
                            <label for="frequency-input">Frequency (Hz):</label>
                            <input type="number" id="frequency-input" value="7.83" step="0.01" min="0.1" />
                        </div>
                        
                        <div>
                            <input type="checkbox" id="boost-input" />
                            <label for="boost-input">Apply Divine Amplification</label>
                        </div>
                        
                        <button class="btn" id="send-intention-btn">Broadcast</button>
                    </div>
                    
                    <div class="visualization-card" id="intention-result">
                        <div id="intention-status">Enter an intention above and click Broadcast</div>
                    </div>
                </div>
            </section>
            
            <section id="torus" style="margin-top: 4rem;">
                <h2>Torus Field Visualization</h2>
                <p>The torus is the fundamental energy pattern found in all living systems and the universe itself.</p>
                
                <div class="visualization">
                    <div class="visualization-controls">
                        <div>
                            <label for="torus-frequency">Torus Frequency (Hz):</label>
                            <input type="number" id="torus-frequency" value="7.83" step="0.01" min="0.1" />
                        </div>
                        
                        <button class="btn" id="visualize-torus-btn">Visualize</button>
                    </div>
                    
                    <div class="visualization-card" id="torus-visualization">
                        <div>Torus Field Visualization</div>
                    </div>
                </div>
            </section>
            
            <section id="merkaba" style="margin-top: 4rem;">
                <h2>Merkaba Field Generator</h2>
                <p>The Merkaba is a crystalline energy field composed of two counter-rotating interlocked tetrahedrons.</p>
                
                <div class="visualization">
                    <div class="visualization-controls">
                        <div>
                            <label for="merkaba-intention">Intention:</label>
                            <input type="text" id="merkaba-intention" placeholder="Enter intention for Merkaba..." />
                        </div>
                        
                        <div>
                            <label for="merkaba-frequency">Spin Frequency:</label>
                            <input type="number" id="merkaba-frequency" value="13.0" step="0.1" min="0.1" />
                        </div>
                        
                        <button class="btn" id="generate-merkaba-btn">Generate</button>
                    </div>
                    
                    <div class="visualization-card" id="merkaba-visualization">
                        <div>Merkaba Field Visualization</div>
                    </div>
                </div>
            </section>
            
            <section id="healing" style="margin-top: 4rem;">
                <h2>Healing Codes Library</h2>
                <p>Access and utilize healing codes for various physical, emotional, and spiritual conditions.</p>
                
                <div class="visualization">
                    <div class="visualization-controls">
                        <div>
                            <label for="healing-search">Search:</label>
                            <input type="text" id="healing-search" placeholder="Search healing codes..." />
                        </div>
                        
                        <div>
                            <label for="healing-category">Category:</label>
                            <select id="healing-category">
                                <option value="">All Categories</option>
                                <option value="CENTRAL NERVOUS SYSTEM">Central Nervous System</option>
                                <option value="PSYCHOLOGICAL CONCERNS">Psychological Concerns</option>
                                <option value="SELF-HELP">Self-Help</option>
                                <option value="SPIRITUAL">Spiritual</option>
                                <option value="RELATIONSHIPS">Relationships</option>
                            </select>
                        </div>
                        
                        <button class="btn" id="fetch-codes-btn">Fetch Codes</button>
                    </div>
                    
                    <div class="visualization-card" id="healing-codes-list" style="overflow-y: auto;">
                        <div>Healing Codes will appear here</div>
                    </div>
                </div>
            </section>
            
            <section id="archive" style="margin-top: 4rem;">
                <h2>Soul Archive</h2>
                <p>Store and access your personal sacred geometry patterns and intentions.</p>
                
                <div class="visualization">
                    <div class="visualization-controls">
                        <div>
                            <label for="archive-title">Title:</label>
                            <input type="text" id="archive-title" placeholder="Title for your soul archive..." />
                        </div>
                        
                        <div>
                            <label for="archive-intention">Intention:</label>
                            <input type="text" id="archive-intention" placeholder="Enter intention..." />
                        </div>
                        
                        <div>
                            <label for="archive-pattern">Pattern Type:</label>
                            <select id="archive-pattern">
                                <option value="torus">Torus Field</option>
                                <option value="merkaba">Merkaba</option>
                                <option value="metatron">Metatron's Cube</option>
                                <option value="sri_yantra">Sri Yantra</option>
                                <option value="flower_of_life">Flower of Life</option>
                            </select>
                        </div>
                        
                        <button class="btn" id="save-archive-btn">Save to Archive</button>
                    </div>
                    
                    <div class="visualization-card" id="soul-archives-list" style="overflow-y: auto;">
                        <div>Your Soul Archives will appear here</div>
                    </div>
                </div>
            </section>
            
            <section style="margin-top: 4rem;">
                <h2>Console and Energetic Feedback</h2>
                <p>Real-time feedback and messages from the sacred computing platform.</p>
                
                <div class="visualization">
                    <div id="console-log" style="text-align: left; height: 200px; overflow-y: auto; padding: 1rem; background-color: var(--accent); border-radius: 0.375rem; font-family: monospace;">
                        <div class="log-entry">[System] Sacred Computing Platform initialized</div>
                        <div class="log-entry">[System] Ready to broadcast intentions</div>
                    </div>
                </div>
            </section>
        </div>
    </main>
    
    <footer>
        <p>Sacred Computing Platform | Quantum Intention Broadcasting | © 2025</p>
    </footer>
    
    <script>
        // Basic functionality for demonstration
        document.addEventListener('DOMContentLoaded', function() {
            const consoleLog = document.getElementById('console-log');
            
            function logMessage(message, type = 'info') {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-${type}`;
                logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                consoleLog.appendChild(logEntry);
                consoleLog.scrollTop = consoleLog.scrollHeight;
            }
            
            // Intention Broadcasting
            document.getElementById('send-intention-btn').addEventListener('click', function() {
                const intention = document.getElementById('intention-input').value;
                const frequency = parseFloat(document.getElementById('frequency-input').value);
                const boost = document.getElementById('boost-input').checked;
                
                if (!intention) {
                    logMessage('Please enter an intention', 'error');
                    return;
                }
                
                logMessage(`Broadcasting intention: "${intention}" at ${frequency} Hz`, 'system');
                document.getElementById('intention-status').innerHTML = `
                    <div style="text-align: center;">
                        <h3 style="margin-top: 0; color: var(--primary);">Intention Broadcast</h3>
                        <p style="margin: 0.5rem 0;">Intention: <strong>${intention}</strong></p>
                        <p style="margin: 0.5rem 0;">Frequency: ${frequency} Hz</p>
                        <p style="margin: 0.5rem 0;">Divine Amplification: ${boost ? 'Yes' : 'No'}</p>
                        <p style="margin-top: 1rem; font-style: italic;">Intention embedded in network packets and broadcast to all connected nodes</p>
                    </div>
                `;
                
                // Request from Python server via fetch here in a real implementation
            });
            
            // Torus Visualization
            document.getElementById('visualize-torus-btn').addEventListener('click', function() {
                const frequency = parseFloat(document.getElementById('torus-frequency').value);
                
                logMessage(`Generating Torus Field at ${frequency} Hz`, 'system');
                document.getElementById('torus-visualization').innerHTML = `
                    <div style="text-align: center;">
                        <h3 style="margin-top: 0; color: var(--primary);">Torus Field</h3>
                        <p style="margin: 0.5rem 0;">Frequency: ${frequency} Hz</p>
                        <p style="margin: 0.5rem 0;">Schumann Ratio: ${(frequency / 7.83).toFixed(3)}</p>
                        <div style="width: 300px; height: 300px; margin: 0 auto; background: radial-gradient(circle, var(--primary) 0%, transparent 70%);">
                            <div style="width: 100%; height: 100%; border-radius: 50%; border: 2px solid var(--primary); animation: pulse 4s infinite alternate;"></div>
                        </div>
                    </div>
                `;
                
                // Request actual visualization from server in a real implementation
            });
            
            // Merkaba Generator
            document.getElementById('generate-merkaba-btn').addEventListener('click', function() {
                const intention = document.getElementById('merkaba-intention').value;
                const frequency = parseFloat(document.getElementById('merkaba-frequency').value);
                
                if (!intention) {
                    logMessage('Please enter an intention for the Merkaba', 'error');
                    return;
                }
                
                logMessage(`Generating Merkaba Field with intention: "${intention}"`, 'system');
                document.getElementById('merkaba-visualization').innerHTML = `
                    <div style="text-align: center;">
                        <h3 style="margin-top: 0; color: var(--primary);">Merkaba Field</h3>
                        <p style="margin: 0.5rem 0;">Intention: <strong>${intention}</strong></p>
                        <p style="margin: 0.5rem 0;">Spin Frequency: ${frequency} Hz</p>
                        <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
                            <!-- Simplified merkaba representation -->
                            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; border: 2px solid #7f5af0; animation: rotate 8s linear infinite;"></div>
                            <div style="position: absolute; top: 25%; left: 25%; width: 50%; height: 50%; transform: rotate(45deg); border: 2px solid #2cb67d; animation: rotate 8s linear infinite reverse;"></div>
                        </div>
                    </div>
                `;
                
                // Request actual visualization from server in a real implementation
            });
            
            // Fetch healing codes
            document.getElementById('fetch-codes-btn').addEventListener('click', function() {
                const search = document.getElementById('healing-search').value;
                const category = document.getElementById('healing-category').value;
                
                logMessage(`Fetching healing codes${category ? ` for category: ${category}` : ''}${search ? ` matching: "${search}"` : ''}`, 'system');
                
                // In a real implementation, fetch from server
                // For now, show sample data
                const sampleCodes = [
                    { code: "23 74 555", description: "Healing headaches in general", category: "CENTRAL NERVOUS SYSTEM" },
                    { code: "58 33 554", description: "Healing migraine", category: "CENTRAL NERVOUS SYSTEM" },
                    { code: "8888", description: "Divine protection", category: "SPIRITUAL" },
                    { code: "13 13 514", description: "Stress relief/relaxation", category: "SELF-HELP" }
                ];
                
                const filteredCodes = category 
                    ? sampleCodes.filter(code => code.category === category)
                    : sampleCodes;
                
                const searchedCodes = search
                    ? filteredCodes.filter(code => 
                        code.code.includes(search) || 
                        code.description.toLowerCase().includes(search.toLowerCase()) ||
                        (code.category && code.category.toLowerCase().includes(search.toLowerCase()))
                      )
                    : filteredCodes;
                
                if (searchedCodes.length === 0) {
                    document.getElementById('healing-codes-list').innerHTML = `
                        <div style="text-align: center; padding: 2rem;">
                            <p>No healing codes found matching your criteria.</p>
                        </div>
                    `;
                    return;
                }
                
                const codesHtml = searchedCodes.map(code => `
                    <div style="background-color: var(--secondary); padding: 1rem; margin-bottom: 1rem; border-radius: 0.375rem;">
                        <h4 style="margin-top: 0; color: var(--primary);">${code.code}</h4>
                        <p style="margin: 0.5rem 0;">${code.description}</p>
                        <p style="margin: 0; font-size: 0.8rem; color: #888;">Category: ${code.category}</p>
                    </div>
                `).join('');
                
                document.getElementById('healing-codes-list').innerHTML = `
                    <div style="padding: 1rem;">
                        <h3>Healing Codes</h3>
                        ${codesHtml}
                    </div>
                `;
            });
            
            // Soul Archive
            document.getElementById('save-archive-btn').addEventListener('click', function() {
                const title = document.getElementById('archive-title').value;
                const intention = document.getElementById('archive-intention').value;
                const patternType = document.getElementById('archive-pattern').value;
                
                if (!title || !intention) {
                    logMessage('Please enter both title and intention', 'error');
                    return;
                }
                
                logMessage(`Saving to Soul Archive: "${title}"`, 'system');
                
                // Fetch archives (in a real implementation, would be from server)
                const sampleArchives = [
                    {
                        id: 1,
                        title: "Inner Peace",
                        intention: "Peace and tranquility",
                        pattern_type: "torus",
                        created_at: new Date().toISOString()
                    },
                    {
                        id: 2,
                        title: "Healing Energy",
                        intention: "Physical healing",
                        pattern_type: "merkaba",
                        created_at: new Date().toISOString()
                    }
                ];
                
                // Add new archive to list
                sampleArchives.push({
                    id: sampleArchives.length + 1,
                    title,
                    intention,
                    pattern_type: patternType,
                    created_at: new Date().toISOString()
                });
                
                const archivesHtml = sampleArchives.map(archive => `
                    <div style="background-color: var(--secondary); padding: 1rem; margin-bottom: 1rem; border-radius: 0.375rem;">
                        <h4 style="margin-top: 0; color: var(--primary);">${archive.title}</h4>
                        <p style="margin: 0.5rem 0;">Intention: ${archive.intention}</p>
                        <p style="margin: 0.5rem 0;">Pattern: ${archive.pattern_type}</p>
                        <p style="margin: 0; font-size: 0.8rem; color: #888;">Created: ${new Date(archive.created_at).toLocaleString()}</p>
                    </div>
                `).join('');
                
                document.getElementById('soul-archives-list').innerHTML = `
                    <div style="padding: 1rem;">
                        <h3>Your Soul Archives</h3>
                        ${archivesHtml}
                    </div>
                `;
                
                // Clear form
                document.getElementById('archive-title').value = '';
                document.getElementById('archive-intention').value = '';
            });
            
            // Initial log messages
            setTimeout(() => {
                logMessage('Connected to quantum field', 'system');
                logMessage('Schumann resonance detected at 7.83 Hz', 'info');
            }, 1000);
            
            // Add style for animations
            const style = document.createElement('style');
            style.textContent = `
                @keyframes pulse {
                    0% { transform: scale(0.95); opacity: 0.7; }
                    100% { transform: scale(1.05); opacity: 1; }
                }
                
                @keyframes rotate {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                
                .log-entry {
                    padding: 0.25rem 0;
                    border-bottom: 1px solid var(--border);
                }
                
                .log-error {
                    color: #e45858;
                }
                
                .log-system {
                    color: #7f5af0;
                }
                
                .log-info {
                    color: #2cb67d;
                }
            `;
            document.head.appendChild(style);
        });
    </script>
</body>
</html>
'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_static_file(self, filename, content_type):
        """Serve static file with proper content type"""
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.serve_html_page('index.html')


class SacredHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threaded HTTP server"""
    
    def __init__(self, server_address, RequestHandlerClass, storage):
        self.storage = storage
        super().__init__(server_address, RequestHandlerClass)
    
    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass"""
        self.RequestHandlerClass(request, client_address, self, storage=self.storage)


#########################################
# INTENTION BROADCASTER
#########################################

class SacredIntentionBroadcaster:
    """Main class for broadcasting intentions over networks"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
    
    async def create_intention_packet(
        self, 
        intention: str,
        frequency: float = SCHUMANN_RESONANCE,
        field_type: str = "torus"
    ) -> str:
        """Create a network packet containing the intention"""
        return await embed_intention_in_network_packet(intention, frequency, field_type)
    
    async def broadcast_intention(
        self,
        intention: str,
        frequency: float = SCHUMANN_RESONANCE,
        field_type: str = "torus",
        amplify: bool = False,
        multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """Broadcast intention over network"""
        logger.info(f"Broadcasting intention: '{intention}'")
        
        # Create the basic packet
        packet_base64 = await self.create_intention_packet(intention, frequency, field_type)
        
        # Calculate sacred geometry data
        geometry_data = None
        if field_type == "torus":
            geometry_data = await SacredGeometryCalculator.torus_field_generator(intention, frequency)
        elif field_type == "merkaba":
            geometry_data = await SacredGeometryCalculator.merkaba_field_generator(intention, frequency)
        elif field_type == "metatron":
            geometry_data = await SacredGeometryCalculator.metatrons_cube_amplifier(intention, amplify)
        elif field_type == "sri_yantra":
            geometry_data = await SacredGeometryCalculator.sri_yantra_encoder(intention)
        elif field_type == "flower_of_life":
            geometry_data = await SacredGeometryCalculator.flower_of_life_pattern(intention, 60)
        
        # Apply divine amplification if requested
        amplified_data = None
        if amplify:
            amplified_data = await SacredGeometryCalculator.divine_proportion_amplify(intention, multiplier)
            logger.info(f"Divine amplification applied. Fibonacci multiplier: {amplified_data['fibonacci_multiplier']}")
        
        # Extract intention from packet to verify
        extracted = extract_intention_from_packet(packet_base64)
        logger.info(f"Verification - extracted intention: '{extracted}'")
        
        # Return result
        result = {
            "intention": intention,
            "frequency": frequency,
            "field_type": field_type,
            "packet_base64": packet_base64
        }
        
        if geometry_data:
            result["geometry_data"] = geometry_data
        
        if amplified_data:
            result["amplified_data"] = amplified_data
        
        logger.info(f"Intention broadcast complete: {intention}")
        logger.info(f"Field type: {field_type}, Frequency: {frequency} Hz")
        
        return result


#########################################
# MAIN APPLICATION
#########################################

async def start_websocket_server(storage, port: int = 8765):
    """Start WebSocket server"""
    if not HAS_WEBSOCKETS:
        logger.error("WebSockets support requires 'websockets' package")
        return None
    
    # Create handler with access to storage
    async def _handler(websocket, path):
        await handle_websocket(websocket, path, storage)
    
    # Start server
    async with websockets.serve(_handler, "0.0.0.0", port):
        logger.info(f"WebSocket server started on port {port}")
        # Keep the server running
        await asyncio.Future()  # Run forever


async def run_server_mode(storage, http_port: int = SERVER_PORT, ws_port: int = 8765):
    """Run the application in server mode"""
    logger.info("Starting Sacred Computing Platform in server mode")
    
    # Start HTTP server in a separate thread
    http_server = SacredHTTPServer(("0.0.0.0", http_port), SacredHTTPHandler, storage)
    http_thread = threading.Thread(target=http_server.serve_forever)
    http_thread.daemon = True
    http_thread.start()
    logger.info(f"HTTP server started on port {http_port}")
    
    # Open browser
    try:
        webbrowser.open(f"http://localhost:{http_port}")
    except Exception:
        logger.info(f"Please open your browser to http://localhost:{http_port}")
    
    # Start WebSocket server if websockets is available
    if HAS_WEBSOCKETS:
        try:
            await start_websocket_server(storage, ws_port)
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
    else:
        logger.warning("WebSocket functionality disabled. Install 'websockets' package for full functionality.")
        # Keep the server running
        await asyncio.Future()  # Run forever


async def run_broadcast_mode(
    intention: str,
    frequency: float = SCHUMANN_RESONANCE,
    field_type: str = "torus",
    amplify: bool = False,
    multiplier: float = 1.0,
    output: Optional[str] = None,
    debug: bool = False
):
    """Run the application in broadcast mode"""
    logger.info("Starting Sacred Computing Platform in broadcast mode")
    
    broadcaster = SacredIntentionBroadcaster(debug=debug)
    
    result = await broadcaster.broadcast_intention(
        intention=intention,
        frequency=frequency,
        field_type=field_type,
        amplify=amplify,
        multiplier=multiplier
    )
    
    # Print result
    print(f"\nIntention: {intention}")
    print(f"Frequency: {frequency} Hz")
    print(f"Field type: {field_type}")
    print(f"Embedded in packet: {result['packet_base64'][:30]}...{result['packet_base64'][-10:]}\n")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Intention data saved to {output}")
    
    print("Packet ready for transmission to end users")


async def run_calculate_mode(
    intention: str,
    field_type: str = "torus",
    frequency: float = SCHUMANN_RESONANCE,
    amplify: bool = False,
    multiplier: float = 1.0,
    output: Optional[str] = None,
    debug: bool = False
):
    """Run the application in calculate mode"""
    logger.info("Starting Sacred Computing Platform in calculate mode")
    
    result = {}
    
    # Calculate based on field type
    if field_type == "torus":
        result = await SacredGeometryCalculator.torus_field_generator(intention, frequency)
    elif field_type == "merkaba":
        result = await SacredGeometryCalculator.merkaba_field_generator(intention, frequency)
    elif field_type == "metatron":
        result = await SacredGeometryCalculator.metatrons_cube_amplifier(intention, amplify)
    elif field_type == "sri_yantra":
        result = await SacredGeometryCalculator.sri_yantra_encoder(intention)
    elif field_type == "flower_of_life":
        result = await SacredGeometryCalculator.flower_of_life_pattern(intention, 60)
    else:
        logger.error(f"Unknown field type: {field_type}")
        return
    
    # Apply divine amplification if requested
    if amplify:
        amplified_data = await SacredGeometryCalculator.divine_proportion_amplify(intention, multiplier)
        result["amplified_data"] = amplified_data
    
    # Print result
    print(f"\nCalculated Sacred Geometry for '{intention}'")
    print(f"Field Type: {field_type}")
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Generate visualization if matplotlib is available
    if HAS_VISUALIZATION and field_type == "torus":
        filename = f"{field_type}_{int(time.time())}.png"
        vis_file = SacredVisualizer.visualize_torus(result, filename)
        print(f"Visualization saved to: {vis_file}")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Calculation data saved to {output}")


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Sacred Computing Platform")
    parser.add_argument("--mode", required=True, choices=["server", "broadcast", "calculate"],
                        help="Operation mode")
    
    # Common options
    parser.add_argument("--intention", help="Intention to broadcast or calculate")
    parser.add_argument("--frequency", type=float, default=SCHUMANN_RESONANCE,
                        help=f"Frequency in Hz (default: {SCHUMANN_RESONANCE} - Earth's Schumann resonance)")
    parser.add_argument("--field-type", choices=["torus", "merkaba", "metatron", "sri_yantra", "flower_of_life"],
                        default="torus", help="Sacred geometry field type")
    parser.add_argument("--amplify", action="store_true", help="Apply divine proportion amplification")
    parser.add_argument("--multiplier", type=float, default=1.0, help="Fibonacci multiplier for amplification")
    parser.add_argument("--output", help="Output file to save data (JSON format)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    # Server options
    parser.add_argument("--http-port", type=int, default=SERVER_PORT, help="HTTP server port")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket server port")
    parser.add_argument("--db-path", default="sacred_computing.db", help="Database file path")
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Initialize storage
    storage = SacredStorage(db_path=args.db_path)
    
    # Run appropriate mode
    if args.mode == "server":
        print(f"Starting Sacred Computing Platform server on http://localhost:{args.http_port}")
        print("Press Ctrl+C to stop the server")
        asyncio.run(run_server_mode(storage, args.http_port, args.ws_port))
    
    elif args.mode == "broadcast":
        if not args.intention:
            print("Error: --intention is required for broadcast mode")
            return
        asyncio.run(run_broadcast_mode(
            intention=args.intention,
            frequency=args.frequency,
            field_type=args.field_type,
            amplify=args.amplify,
            multiplier=args.multiplier,
            output=args.output,
            debug=args.debug
        ))
    
    elif args.mode == "calculate":
        if not args.intention:
            print("Error: --intention is required for calculate mode")
            return
        asyncio.run(run_calculate_mode(
            intention=args.intention,
            field_type=args.field_type,
            frequency=args.frequency,
            amplify=args.amplify,
            multiplier=args.multiplier,
            output=args.output,
            debug=args.debug
        ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSacred Computing Platform shutting down...")
        sys.exit(0)
