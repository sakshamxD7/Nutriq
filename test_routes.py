import unittest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.food import FoodItem, FoodLog
from app.models.plan import Subscription, WeightLog

from config import TestingConfig

class NutriqRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Create database
        db.create_all()
        
        # Seed basic food items for trivia and quick-add
        f1 = FoodItem(name="Idli", name_hindi="इडली", category="Breakfast", calories_per_100g=112.0, protein_g=3.2, carbs_g=23.0, fat_g=0.5, is_verified=True, source="manual")
        f2 = FoodItem(name="Poha", name_hindi="पोहा", category="Breakfast", calories_per_100g=180.0, protein_g=3.5, carbs_g=32.0, fat_g=4.2, is_verified=True, source="manual")
        f3 = FoodItem(name="Aloo Paratha", name_hindi="आलू पराठा", category="Breakfast", calories_per_100g=210.0, protein_g=5.0, carbs_g=33.0, fat_g=6.8, is_verified=True, source="manual")
        
        db.session.add_all([f1, f2, f3])
        db.session.commit()
        
        # Create mock user
        self.user = User(
            name="Test User",
            email="test@example.com",
            age=25,
            gender="male",
            height_cm=175.0,
            weight_kg=70.0,
            activity_level="moderate",
            goal="maintain",
            dietary_pref="veg",
            is_premium=True
        )
        self.user.set_password("password123")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self):
        return self.client.post('/auth/login', data=dict(
            email='test@example.com',
            password='password123'
        ), follow_redirects=True)

    def test_unauthenticated_redirects(self):
        # Unauthenticated calls should redirect to login
        endpoints = ['/', '/food/search', '/diary/', '/goals/', '/trivia/', '/ai/plan', '/ai/chat']
        for url in endpoints:
            rv = self.client.get(url)
            self.assertEqual(rv.status_code, 302, f"URL {url} did not redirect (status code: {rv.status_code})")

    def test_authenticated_pages(self):
        self.login()
        
        # Test main endpoints
        endpoints = [
            ('/', 200),
            ('/food/search', 200),
            ('/food/barcode', 200),
            ('/diary/', 200),
            ('/goals/', 200),
            ('/trivia/', 200),
            ('/ai/plan', 200),
            ('/ai/chat', 200),
            ('/billing/plans', 200),
            ('/notifications/settings', 200)
        ]
        
        for url, expected_code in endpoints:
            rv = self.client.get(url)
            self.assertEqual(rv.status_code, expected_code, f"URL {url} failed with status {rv.status_code}")
            
    def test_food_search_ajax(self):
        self.login()
        rv = self.client.get('/food/search?q=Idli&format=json', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Idli', rv.data)
        
    def test_trivia_logic(self):
        self.login()
        # Test next question retrieval
        rv = self.client.get('/trivia/next', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(rv.status_code, 200)
        
    def test_weight_log(self):
        self.login()
        rv = self.client.post('/goals/log', data={'weight_kg': '72.5'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Successfully logged today', rv.data)

if __name__ == '__main__':
    unittest.main()
