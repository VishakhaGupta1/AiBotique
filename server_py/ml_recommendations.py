"""
Professional Fashion Recommendation Engine
Uses collaborative filtering, content-based filtering, and hybrid approaches
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import sqlite3
import json
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FashionRecommendationEngine:
    def __init__(self, db_path: str = "fashion_db.sqlite"):
        """Initialize the recommendation engine with database connection"""
        self.db_path = db_path
        self.conn = None
        self.user_item_matrix = None
        self.item_features_matrix = None
        self.svd_model = None
        self.tfidf_vectorizer = None
        
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            
    def load_user_interaction_data(self) -> pd.DataFrame:
        """Load user interaction data for collaborative filtering"""
        query = """
        SELECT ui.user_id, ui.product_id, ui.rating, ui.interaction_type,
               u.age, u.gender, p.category, p.color, p.brand, p.price
        FROM user_interactions ui
        JOIN users u ON ui.user_id = u.id
        JOIN products p ON ui.product_id = p.id
        WHERE ui.rating IS NOT NULL
        """
        return pd.read_sql_query(query, self.conn)
    
    def load_product_features(self) -> pd.DataFrame:
        """Load product features for content-based filtering"""
        query = """
        SELECT id, name, brand, category, subcategory, color, price, 
               target_gender, target_age_min, target_age_max, season, material,
               popularity_score
        FROM products
        WHERE in_stock = TRUE
        """
        return pd.read_sql_query(query, self.conn)
    
    def build_user_item_matrix(self, interactions_df: pd.DataFrame):
        """Build user-item interaction matrix for collaborative filtering"""
        # Create user-item matrix
        self.user_item_matrix = interactions_df.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='rating',
            fill_value=0
        )
        logger.info(f"User-Item matrix shape: {self.user_item_matrix.shape}")
        
    def build_item_features_matrix(self, products_df: pd.DataFrame):
        """Build item features matrix for content-based filtering"""
        # Combine text features
        products_df['combined_features'] = (
            products_df['brand'] + ' ' + 
            products_df['category'] + ' ' + 
            products_df['subcategory'] + ' ' + 
            products_df['color'] + ' ' + 
            products_df['material'] + ' ' + 
            products_df['season']
        )
        
        # TF-IDF Vectorization
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(products_df['combined_features'])
        
        # Add numerical features
        numerical_features = products_df[['price', 'popularity_score']].values
        numerical_features = (numerical_features - numerical_features.mean()) / numerical_features.std()
        
        # Combine TF-IDF and numerical features
        from scipy.sparse import hstack
        self.item_features_matrix = hstack([tfidf_matrix, numerical_features])
        
        logger.info(f"Item features matrix shape: {self.item_features_matrix.shape}")
        
    def train_collaborative_filtering(self):
        """Train SVD model for collaborative filtering"""
        if self.user_item_matrix is None:
            raise ValueError("User-item matrix not built")
            
        # Use SVD for dimensionality reduction
        self.svd_model = TruncatedSVD(n_components=50, random_state=42)
        self.svd_model.fit(self.user_item_matrix)
        
        logger.info("Collaborative filtering model trained")
        
    def get_collaborative_recommendations(self, user_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get recommendations using collaborative filtering"""
        if self.svd_model is None:
            raise ValueError("Collaborative filtering model not trained")
            
        try:
            user_idx = self.user_item_matrix.index.get_loc(user_id)
        except KeyError:
            # Cold start problem - return popular items
            return self.get_popular_items(n_recommendations)
            
        # Get user's latent factors
        user_factors = self.svd_model.transform(self.user_item_matrix.iloc[[user_idx]])
        
        # Get all item factors
        item_factors = self.svd_model.components_.T
        
        # Calculate predicted ratings
        predicted_ratings = np.dot(user_factors, item_factors.T)[0]
        
        # Get items user hasn't rated
        user_items = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        all_items = set(self.user_item_matrix.columns)
        unrated_items = list(all_items - user_items)
        
        # Get recommendations
        recommendations = []
        for item_id in unrated_items:
            item_idx = self.user_item_matrix.columns.get_loc(item_id)
            score = predicted_ratings[item_idx]
            recommendations.append((item_id, score))
            
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
        
    def get_content_based_recommendations(self, product_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get recommendations using content-based filtering"""
        if self.item_features_matrix is None:
            raise ValueError("Item features matrix not built")
            
        # Get product features
        query = "SELECT id FROM products ORDER BY id"
        products = pd.read_sql_query(query, self.conn)
        product_indices = {row['id']: idx for idx, row in products.iterrows()}
        
        try:
            product_idx = product_indices[product_id]
        except KeyError:
            return []
            
        # Calculate similarity with all other products
        product_vector = self.item_features_matrix[product_idx:product_idx+1]
        similarities = cosine_similarity(product_vector, self.item_features_matrix)[0]
        
        # Get top similar products (excluding itself)
        similar_indices = similarities.argsort()[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            similar_product_id = products.iloc[idx]['id']
            score = similarities[idx]
            recommendations.append((similar_product_id, float(score)))
            
        return recommendations
        
    def get_hybrid_recommendations(self, user_id: int, user_preferences: Dict, n_recommendations: int = 10) -> List[Dict]:
        """Get hybrid recommendations combining multiple approaches"""
        recommendations = []
        
        # 1. Collaborative filtering recommendations
        try:
            cf_recs = self.get_collaborative_recommendations(user_id, n_recommendations // 2)
            for product_id, score in cf_recs:
                recommendations.append({
                    'product_id': product_id,
                    'score': score * 0.6,  # Weight for CF
                    'source': 'collaborative'
                })
        except Exception as e:
            logger.warning(f"Collaborative filtering failed: {e}")
            
        # 2. Content-based recommendations based on preferences
        try:
            # Find products matching user preferences
            matching_products = self.find_products_by_preferences(user_preferences, n_recommendations // 2)
            for product_id, score in matching_products:
                recommendations.append({
                    'product_id': product_id,
                    'score': score * 0.4,  # Weight for content-based
                    'source': 'content'
                })
        except Exception as e:
            logger.warning(f"Content-based filtering failed: {e}")
            
        # 3. Remove duplicates and sort
        seen_products = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['product_id'] not in seen_products:
                seen_products.add(rec['product_id'])
                unique_recommendations.append(rec)
                
        unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # 4. Get full product details
        final_recommendations = []
        for rec in unique_recommendations[:n_recommendations]:
            product_details = self.get_product_details(rec['product_id'])
            if product_details:
                product_details.update({
                    'recommendation_score': rec['score'],
                    'recommendation_source': rec['source']
                })
                final_recommendations.append(product_details)
                
        return final_recommendations
        
    def find_products_by_preferences(self, preferences: Dict, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Find products matching user preferences"""
        query = """
        SELECT id, name, brand, category, color, price, target_gender, target_age_min, target_age_max
        FROM products
        WHERE in_stock = TRUE
        """
        
        conditions = []
        params = []
        
        # Add filters based on preferences
        if 'gender' in preferences:
            conditions.append("(target_gender = ? OR target_gender = 'unisex')")
            params.append(preferences['gender'])
            
        if 'color' in preferences:
            conditions.append("color = ?")
            params.append(preferences['color'])
            
        if 'style' in preferences:
            conditions.append("category = ?")
            params.append(preferences['style'])
            
        if 'budget' in preferences:
            conditions.append("price <= ?")
            params.append(preferences['budget'])
            
        if 'age' in preferences:
            age = preferences['age']
            conditions.append("(target_age_min <= ? AND target_age_max >= ?)")
            params.extend([age, age])
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY popularity_score DESC LIMIT ?"
        params.append(n_recommendations)
        
        try:
            results = pd.read_sql_query(query, self.conn, params=params)
            recommendations = []
            for _, row in results.iterrows():
                # Calculate preference match score
                score = self.calculate_preference_score(row, preferences)
                recommendations.append((row['id'], score))
                
            return sorted(recommendations, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding products by preferences: {e}")
            return []
            
    def calculate_preference_score(self, product: pd.Series, preferences: Dict) -> float:
        """Calculate how well a product matches user preferences"""
        score = 0.0
        
        # Gender match
        if 'gender' in preferences:
            if product['target_gender'] == 'unisex' or product['target_gender'] == preferences['gender']:
                score += 30
            else:
                score -= 20
                
        # Color match
        if 'color' in preferences and product['color'].lower() == preferences['color'].lower():
            score += 25
            
        # Style match
        if 'style' in preferences and product['category'].lower() == preferences['style'].lower():
            score += 25
            
        # Budget fit
        if 'budget' in preferences:
            if product['price'] <= preferences['budget']:
                if product['price'] <= preferences['budget'] * 0.5:
                    score += 15
                else:
                    score += 10
            else:
                score -= 15
                
        # Age appropriateness
        if 'age' in preferences:
            age = preferences['age']
            if product['target_age_min'] <= age <= product['target_age_max']:
                score += 20
            elif abs(age - product['target_age_min']) <= 5 or abs(age - product['target_age_max']) <= 5:
                score += 10
                
        # Popularity boost
        score += product['popularity_score'] * 0.1
        
        return score
        
    def get_product_details(self, product_id: int) -> Dict:
        """Get detailed product information"""
        query = """
        SELECT id, name, brand, category, subcategory, color, size, price, 
               image_url, description, target_gender, target_age_min, target_age_max,
               season, material, popularity_score
        FROM products
        WHERE id = ? AND in_stock = TRUE
        """
        
        try:
            result = pd.read_sql_query(query, self.conn, params=[product_id])
            if not result.empty:
                return result.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            
        return None
        
    def get_popular_items(self, n_items: int = 10) -> List[Tuple[int, float]]:
        """Get popular items for cold start problem"""
        query = """
        SELECT id, popularity_score
        FROM products
        WHERE in_stock = TRUE
        ORDER BY popularity_score DESC
        LIMIT ?
        """
        
        try:
            results = pd.read_sql_query(query, self.conn, params=[n_items])
            return [(row['id'], float(row['popularity_score'])) for _, row in results.iterrows()]
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            return []
            
    def create_complete_outfits(self, recommendations: List[Dict], user_preferences: Dict) -> List[Dict]:
        """Create complete outfits from recommended products"""
        outfits = []
        
        # Group recommendations by style
        style_groups = {}
        for rec in recommendations:
            style = rec['category']
            if style not in style_groups:
                style_groups[style] = []
            style_groups[style].append(rec)
            
        # Create outfits for each style
        for style, products in style_groups.items():
            outfit = self.create_outfit_from_products(products, user_preferences)
            if outfit:
                outfits.append(outfit)
                
        return outfits[:5]  # Return top 5 outfits
        
    def create_outfit_from_products(self, products: List[Dict], user_preferences: Dict) -> Dict:
        """Create a complete outfit from a list of products"""
        outfit_items = []
        total_price = 0
        item_types = {'top': None, 'bottom': None, 'shoes': None, 'accessory': None}
        
        for product in products:
            # Determine item type based on category
            if product['category'] in ['shirts', 'tops', 'hoodies', 'jackets']:
                item_type = 'top'
            elif product['category'] in ['jeans', 'trousers', 'shorts']:
                item_type = 'bottom'
            elif product['subcategory'] == 'shoes':
                item_type = 'shoes'
            else:
                item_type = 'accessory'
                
            # Add to outfit if we don't have this item type yet
            if item_types[item_type] is None:
                item_types[item_type] = product
                outfit_items.append({
                    'type': item_type,
                    'name': product['name'],
                    'brand': product['brand'],
                    'price': product['price'],
                    'image_url': product['image_url']
                })
                total_price += product['price']
                
        # Create outfit if we have at least 2 items
        if len(outfit_items) >= 2:
            return {
                'outfit_id': f"generated_{len(outfit_items)}",
                'name': f"{user_preferences.get('style', 'Casual')} {user_preferences.get('color', 'Multi')} Outfit",
                'description': f"Complete {user_preferences.get('style', 'casual')} outfit with {len(outfit_items)} items",
                'items': outfit_items,
                'total_price': total_price,
                'style': user_preferences.get('style', 'casual'),
                'color_scheme': user_preferences.get('color', 'multi'),
                'target_gender': user_preferences.get('gender', 'unisex'),
                'target_age': f"{user_preferences.get('age', 25)}",
                'in_stock': True
            }
            
        return None
        
    def train_models(self):
        """Train all recommendation models"""
        logger.info("Training recommendation models...")
        
        # Load data
        interactions_df = self.load_user_interaction_data()
        products_df = self.load_product_features()
        
        # Build matrices
        self.build_user_item_matrix(interactions_df)
        self.build_item_features_matrix(products_df)
        
        # Train collaborative filtering
        if not interactions_df.empty:
            self.train_collaborative_filtering()
            
        logger.info("Model training completed")
        
    def get_recommendations_for_user(self, user_id: int, user_preferences: Dict) -> List[Dict]:
        """Get complete outfit recommendations for a user"""
        # Get hybrid recommendations
        product_recommendations = self.get_hybrid_recommendations(user_id, user_preferences, 20)
        
        # Create complete outfits
        outfits = self.create_complete_outfits(product_recommendations, user_preferences)
        
        return outfits

# Initialize the recommendation engine
recommendation_engine = FashionRecommendationEngine()

def get_fashion_recommendations(user_profile: Dict, k: int = 8) -> List[Dict]:
    """
    Main function to get fashion recommendations
    """
    try:
        # Connect to database
        recommendation_engine.connect_database()
        
        # Train models (in production, this would be done periodically)
        recommendation_engine.train_models()
        
        # Get recommendations
        user_id = user_profile.get('user_id', 1)  # Default user ID for demo
        recommendations = recommendation_engine.get_recommendations_for_user(user_id, user_profile)
        
        return recommendations[:k]
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        # Fallback to simple recommendations
        return get_fallback_recommendations(user_profile, k)
        
def get_fallback_recommendations(user_profile: Dict, k: int = 8) -> List[Dict]:
    """Fallback recommendations when ML models fail"""
    # Simple rule-based recommendations
    fallback_outfits = [
        {
            'outfit_id': 'fallback_1',
            'name': 'Classic Casual Outfit',
            'description': 'A comfortable and stylish casual outfit',
            'items': [
                {'type': 'top', 'name': 'White T-Shirt', 'brand': 'Basic', 'price': 799, 'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=200&h=200&fit=crop'},
                {'type': 'bottom', 'name': 'Blue Jeans', 'brand': 'Denim Co', 'price': 2499, 'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&h=200&fit=crop'},
                {'type': 'shoes', 'name': 'White Sneakers', 'brand': 'Sports', 'price': 3999, 'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&h=200&fit=crop'}
            ],
            'total_price': 7297,
            'style': 'casual',
            'color_scheme': 'blue_white',
            'target_gender': 'unisex',
            'target_age': '20-30',
            'in_stock': True
        }
    ]
    
    return fallback_outfits * min(k, len(fallback_outfits))
