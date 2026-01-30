"""
Phase 3: Vector Utilities

Helper functions for pgvector operations.
"""

from typing import List
import math


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score (0-1, higher is more similar)
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")
    
    # Dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    # Cosine similarity
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def normalize_vector(vec: List[float]) -> List[float]:
    """
    Normalize vector to unit length.
    
    Args:
        vec: Input vector
        
    Returns:
        Normalized vector (magnitude = 1)
    """
    magnitude = math.sqrt(sum(x * x for x in vec))
    
    if magnitude == 0:
        return vec
    
    return [x / magnitude for x in vec]


def vector_to_string(vec: List[float]) -> str:
    """
    Convert vector to PostgreSQL array string format.
    
    Args:
        vec: Vector as list of floats
        
    Returns:
        String like '[0.1, 0.2, 0.3]'
    """
    return '[' + ','.join(str(x) for x in vec) + ']'


def validate_vector_dimensions(vec: List[float], expected: int = 1536) -> bool:
    """
    Validate vector has expected dimensions.
    
    Args:
        vec: Vector to validate
        expected: Expected dimension count (default 1536 for OpenAI)
        
    Returns:
        True if valid, False otherwise
    """
    return len(vec) == expected


def calculate_storage_size(num_vectors: int, dimensions: int = 1536) -> dict:
    """
    Estimate storage size for vectors.
    
    Args:
        num_vectors: Number of vectors
        dimensions: Vector dimensions (default 1536)
        
    Returns:
            Dict with size estimates
    """
    # pgvector stores float32 (4 bytes per dimension)
    bytes_per_vector = dimensions * 4
    total_bytes = num_vectors * bytes_per_vector
    
    # HNSW index overhead (approximately 50% of data size)
    index_bytes = int(total_bytes * 0.5)
    
    return {
        'num_vectors': num_vectors,
        'dimensions': dimensions,
        'data_size_mb': round(total_bytes / 1024 / 1024, 2),
        'index_size_mb': round(index_bytes / 1024 / 1024, 2),
        'total_size_mb': round((total_bytes + index_bytes) / 1024 / 1024, 2)
    }
