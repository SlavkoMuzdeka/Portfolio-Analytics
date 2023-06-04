import unittest, json, os
from app import app
from models import AssetPriceHistory, Portfolio

USER_TOKEN = os.environ['USER_TOKEN']
ADMIN_TOKEN = os.environ['ADMIN_TOKEN']

class CapstoneTestCase(unittest.TestCase):
    """This class represents the capstone test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client

        self.portfolio = Portfolio('Some class', 0.4, 'Some benchmark description', 22, 'Some bloomberg query')
        self.portfolio.insert()

        self.asset_price_history = AssetPriceHistory('Bond', 234.3, '02-02-2002', self.portfolio.id)
        self.asset_price_history.insert()


    def tearDown(self):
        """Executed after reach test"""
        if self.asset_price_history:
            self.asset_price_history.delete()
        self.portfolio.delete()

        
    def test_get_portfolios_without_token(self):
        res = self.client().get('/portfolios',)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)


    def test_get_portfolios_with_token(self):
        res = self.client().get('/portfolios', headers={
            'Authorization': "Bearer {}".format(USER_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['portfolios']))


    def test_404_get_portfolios(self):
        self.asset_price_history.delete()
        self.portfolio.delete()

        res = self.client().get('/portfolios/example', headers={
            'Authorization': "Bearer {}".format(USER_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_asset_price_histories(self):
        res = self.client().get('/asset_price_histories', headers={
            'Authorization': "Bearer {}".format(USER_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['asset_price_histories']))


    def test_404_get_asset_price_histories(self):
        self.asset_price_history.delete()
        res = self.client().get('/asset_price_histories/example', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_create_portfolio_with_permission(self):
        new_portfolio = {
            'asset_class_desc': 'some_desc',
            'weight': 238,
            'benchmark_desc': 'some_bench_desc',
            'sort_id': 2,
            'bloomberg_qry': 'some_exampl_desc',
        }

        res = self.client().post('/portfolios', json=new_portfolio, content_type='application/json', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        created_portfolio = Portfolio.query.filter(Portfolio.id == data['created']).one_or_none()
        if created_portfolio:
            created_portfolio.delete()


    def test_create_portfolio_without_permission(self):
        new_portfolio = {
            'asset_class_desc': 'some_desc',
            'weight': 238,
            'benchmark_desc': 'some_bench_desc',
            'sort_id': 2,
            'bloomberg_qry': 'some_exampl_desc',
        }

        res = self.client().post('/portfolios', json=new_portfolio, content_type='application/json', headers={
            'Authorization': "Bearer {}".format(USER_TOKEN)
        })

        self.assertEqual(res.status_code, 401)

    
    def test_422_create_portfolio(self):
        new_portfolio = {
            'asset_class_desc': 'some_desc',
            'weight': 238,
            'benchmark_desc': 'some_bench_desc',
            'sort_id': 2,
        }
        
        res = self.client().post('/portfolios', json=new_portfolio, content_type='application/json', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_edit_asset_price_history(self):
        self.asset_price_history.price = 100

        res = self.client().patch(f'/asset_price_histories/{self.asset_price_history.id}/edit', json=self.asset_price_history.format(), content_type='application/json', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_422_edit_asset_price_history(self):
        new_asset_price_history = {
            'id': self.asset_price_history.id,
            'asset_type': self.asset_price_history.asset_type,
            'price': self.asset_price_history.price,
            'date': self.asset_price_history.date
        }

        res = self.client().patch(f'/asset_price_histories/{self.asset_price_history.id}/edit', json=new_asset_price_history, content_type='application/json', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_delete_portfolio(self):
        self.asset_price_history.delete()
        portfolio_id = self.portfolio.id
        res = self.client().delete(f'/portfolios/{portfolio_id}', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], portfolio_id)

    
    def test_404_delete_portfolio(self):
        res = self.client().delete('/portfolios/2323232232', headers={
            'Authorization': "Bearer {}".format(ADMIN_TOKEN)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()