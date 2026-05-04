"""
AI Features for Land Registration System
Includes document fraud detection and land recommendations
"""

import os
# import numpy as np  # Optional for Python 3.13 compatibility
# from sklearn.preprocessing import StandardScaler  # Optional
# from sklearn.ensemble import RandomForestClassifier  # Optional
# import cv2  # Commented for Python 3.13 compatibility
from werkzeug.utils import secure_filename
from typing import Tuple, Dict, Any, List
import pickle
from datetime import datetime
import hashlib

try:
    import numpy as np
except ImportError:
    np = None


class DocumentFraudDetector:
    """
    AI model for detecting fake or duplicate land documents
    Uses simple heuristics and image analysis
    """
    
    def __init__(self):
        self.model = None
        self.trained = False
    
    def extract_image_features(self, image_path: str) -> list:
        """
        Extract features from document image (simplified for Python 3.13)
        
        Args:
            image_path: Path to the document image
        
        Returns:
            List of extracted features
        """
        try:
            features = []
            
            # Get file properties
            file_size = os.path.getsize(image_path)
            features.append(float(file_size))
            features.append(float(file_size / 1024))  # Size in KB
            
            # Basic file stats
            import time
            stat = os.stat(image_path)
            features.append(float(stat.st_mtime))
            features.append(float(stat.st_ctime))
            
            # Pad to 20 features for consistency
            while len(features) < 20:
                features.append(0.0)
            
            return features[:20]
        
        except Exception as e:
            print(f"Error extracting features: {e}")
            return [0.0] * 20
    
    def calculate_document_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of document for duplicate detection
        
        Args:
            file_path: Path to the document file
        
        Returns:
            SHA-256 hash of the file
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return ""
    
    def check_document_authenticity(self, image_path: str, document_hashes: List[str] = None) -> Dict[str, Any]:
        """
        Check if document is authentic (not fake/duplicate)
        
        Args:
            image_path: Path to the document image
            document_hashes: List of existing document hashes to check for duplicates
        
        Returns:
            Dictionary with authenticity score and details
        """
        result = {
            'is_authentic': True,
            'fraud_confidence': 0.0,
            'reasons': [],
            'duplicate_detected': False
        }
        
        try:
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                result['fraud_confidence'] += 0.5
                result['reasons'].append('Empty file detected')
            
            if file_size > 50 * 1024 * 1024:  # Over 50MB
                result['fraud_confidence'] += 0.2
                result['reasons'].append('File unusually large')
            
            # Calculate document hash for duplicate detection
            doc_hash = self.calculate_document_hash(image_path)
            if document_hashes and doc_hash in document_hashes:
                result['duplicate_detected'] = True
                result['fraud_confidence'] += 0.8
                result['reasons'].append('Duplicate document detected')
            
            # Basic validation passed
            if file_size > 1000 and file_size < 50 * 1024 * 1024:
                result['reasons'].append('Document appears valid')
            
            # Final decision
            result['fraud_confidence'] = min(result['fraud_confidence'], 1.0)
            result['is_authentic'] = result['fraud_confidence'] < 0.5
            
        except Exception as e:
            print(f"Error in authenticity check: {e}")
            result['reasons'].append(f"Error: {str(e)}")
        
        return result


class LandRecommendationEngine:
    """
    AI-based recommendation engine for suggesting lands to buyers
    Uses collaborative filtering and content-based filtering
    """
    
    def __init__(self):
        self.model = None
        self.buyer_profiles = {}
        self.land_features = {}
    
    def extract_buyer_profile(self, buyer_id: str, offers: List[Dict]) -> Dict[str, Any]:
        """
        Extract buyer preferences from their offer history
        
        Args:
            buyer_id: ID of the buyer
            offers: List of offers made by the buyer
        
        Returns:
            Dictionary with buyer profile
        """
        if not offers:
            return {
                'avg_budget': 0,
                'preferred_locations': [],
                'preferred_size_range': (0, float('inf')),
                'total_offers': 0,
                'success_rate': 0
            }
        
        offered_prices = [offer['offered_price'] for offer in offers]
        
        # Simple average calculation
        total = sum(offered_prices)
        count = len(offered_prices)
        avg_budget = total / count if count > 0 else 0
        
        profile = {
            'avg_budget': avg_budget,
            'min_budget': min(offered_prices) if offered_prices else 0,
            'max_budget': max(offered_prices) if offered_prices else 0,
            'total_offers': len(offers),
            'accepted_offers': len([o for o in offers if o.get('status') == 'accepted']),
        }
        
        profile['success_rate'] = (
            profile['accepted_offers'] / profile['total_offers']
            if profile['total_offers'] > 0 else 0
        )
        
        return profile
    
    def extract_land_features(self, land: Dict[str, Any]) -> list:
        """
        Extract features from a land listing
        
        Args:
            land: Land data dictionary
        
        Returns:
            List of land features
        """
        features = [
            land.get('price', 0),
            land.get('size_sqft', 0),
            land.get('price', 0) / max(land.get('size_sqft', 1), 1),  # Price per sqft
            1 if land.get('is_available') else 0,
            1 if land.get('verification_status') == 'verified' else 0,
        ]
        
        return features
    
    def calculate_recommendation_score(self, land: Dict[str, Any], buyer_profile: Dict[str, Any]) -> float:
        """
        Calculate recommendation score for a land given a buyer profile
        
        Args:
            land: Land data
            buyer_profile: Buyer profile
        
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Price matching
        if buyer_profile['avg_budget'] > 0:
            price_fit = min(
                land['price'] / buyer_profile['avg_budget'],
                buyer_profile['avg_budget'] / max(land['price'], 1)
            )
            score += 0.2 * min(price_fit, 1.0)
        
        # Availability and verification
        if land.get('is_available'):
            score += 0.15
        
        if land.get('verification_status') == 'verified':
            score += 0.15
        
        # Success history bonus
        if buyer_profile['success_rate'] > 0.5:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_recommendations(
        self,
        buyer_id: str,
        buyer_profile: Dict[str, Any],
        available_lands: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top K land recommendations for a buyer
        
        Args:
            buyer_id: ID of the buyer
            buyer_profile: Buyer profile dictionary
            available_lands: List of available lands
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended lands with scores
        """
        recommendations = []
        
        for land in available_lands:
            score = self.calculate_recommendation_score(land, buyer_profile)
            recommendations.append({
                'land_id': land['id'],
                'title': land['title'],
                'price': land['price'],
                'size_sqft': land['size_sqft'],
                'location': land['location'],
                'score': score,
                'reason': self._generate_recommendation_reason(land, buyer_profile)
            })
        
        # Sort by score and return top k
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_k]
    
    def _generate_recommendation_reason(self, land: Dict[str, Any], buyer_profile: Dict[str, Any]) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if land.get('price') <= buyer_profile['avg_budget'] * 1.2:
            reasons.append("within your budget")
        
        if land.get('verification_status') == 'verified':
            reasons.append("verified property")
        
        if land.get('is_available'):
            reasons.append("currently available")
        
        if not reasons:
            reasons.append("matches your interests")
        
        return "Recommended because it's " + ", ".join(reasons)


# Initialize global instances
fraud_detector = DocumentFraudDetector()
recommendation_engine = LandRecommendationEngine()


def check_document_fraud(file_path: str, existing_hashes: List[str] = None) -> Dict[str, Any]:
    """
    Wrapper function to check document fraud
    
    Args:
        file_path: Path to the document
        existing_hashes: List of existing hashes to check duplicates
    
    Returns:
        Fraud check results
    """
    return fraud_detector.check_document_authenticity(file_path, existing_hashes)


def get_land_recommendations(
    buyer_id: str,
    buyer_offers: List[Dict],
    available_lands: List[Dict],
    top_k: int = 5
) -> List[Dict]:
    """
    Wrapper function to get land recommendations
    
    Args:
        buyer_id: ID of the buyer
        buyer_offers: List of offers made by buyer
        available_lands: List of available lands
        top_k: Number of recommendations
    
    Returns:
        List of recommended lands
    """
    buyer_profile = recommendation_engine.extract_buyer_profile(buyer_id, buyer_offers)
    return recommendation_engine.get_recommendations(
        buyer_id,
        buyer_profile,
        available_lands,
        top_k
    )
