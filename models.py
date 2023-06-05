import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, ForeignKey, Integer, String

# DATABASE_USER = os.environ["DATABASE_USER"]
# DATABASE_PASS = os.environ["DATABASE_PASS"]
# DATABASE_NAME = os.environ["DATABASE_NAME"]
# DATABASE_HOST = os.environ["DATABASE_HOST"]
# DATABASE_PATH = "postgresql://{}:{}@{}/{}".format(
#     DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_NAME
# )
DATABASE_PATH = os.environ['DATABASE_URL']
if DATABASE_PATH.startswith("postgres://"):
  DATABASE_PATH = DATABASE_PATH.replace("postgres://", "postgresql://", 1)


db = SQLAlchemy()


"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, database_path=DATABASE_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)              # A unique identifier for each portfolio
    asset_class_desc = Column(String, nullable=False)   # The description or category of the asset class associated with the portfolio (it provides information about the type of assets in the portfolio, such as stocks, bonds, commodities)
    weight = Column(Float, nullable=False)              # The weight or proportion of the asset class within the porfolio
    benchmark_desc = Column(String, nullable=False)     # It provides information about the benchmark against which the performance of the portfolio is evaluated or compared
    sort_id = Column(Integer, nullable=False)           # Represents a type or category identifier for the portfolio
    bloomberg_qry = Column(String, nullable=False)      # Store a query or reference related to Bloomberg or a reference to Bloomberg data relevant to the portfolio

    def __init__(
        self, asset_class_desc, weight, benchmark_desc, sort_id, bloomberg_qry
    ):
        self.asset_class_desc = asset_class_desc
        self.weight = weight
        self.benchmark_desc = benchmark_desc
        self.sort_id = sort_id
        self.bloomberg_qry = bloomberg_qry

    def __repr__(self):
        return self.format()

    """
    insert()
        inserts a new model into a database
        EXAMPLE
            portfolio = Portfolio(asset_class_desc=req_asset_class_desc,
                                    weight=req_weight, 
                                    benchmark_desc=req_benchmark_desc,
                                    sort_id=req_sort_id,
                                    bloomberg_qry=req_bloomberg_qry)
            portfolio.insert()
    """

    def insert(self):
        db.session.add(self)
        db.session.commit()

    """
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            portfolio = Portfolio.query.filter(Portfolio.id == id).one_or_none()
            portfolio.weight = '0.14'
            portfolio.update()
    """

    def update(self):
        db.session.commit()

    """
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            portfolio = Portfolio(asset_class_desc=req_asset_class_desc,
                                    weight=req_weight, 
                                    benchmark_desc=req_benchmark_desc,
                                    sort_id=req_sort_id,
                                    bloomberg_qry=req_bloomberg_qry)
            portfolio.delete()
    """

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "asset_class_desc": self.asset_class_desc,
            "weight": self.weight,
            "benchmark_desc": self.benchmark_desc,
            "sort_id": self.sort_id,
            "bloomberg_qry": self.bloomberg_qry,
        }


class AssetPriceHistory(db.Model):
    __tablename__ = "asset_price_histories"

    id = Column(Integer, primary_key=True)                        # A unique identifier for each price history entry
    asset_type = Column(String, nullable=False)                   # The type of underlying asset (bond, shares, commodity, etc.)
    price = Column(Float, nullable=False)                         # The price of the asset
    date = Column(String, nullable=False)                         # The date associated with the asset price
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))   # The foreign key referencing the portfolio


    def __init__(self, asset_type, price, date, portfolio_id):
        self.asset_type = asset_type
        self.price = price
        self.date = date
        self.portfolio_id = portfolio_id


    def __repr__(self):
        return self.format()
    
    
    """
    insert()
        inserts a new model into a database
        EXAMPLE
            assetPriceHist = AssetPriceHistory(asset_type=req_asset_type,
                                                price=req_price,
                                                date=req_date,
                                                portfolio_id=req_portfolio_id)
            assetPriceHist.insert()
    """

    def insert(self):
        db.session.add(self)
        db.session.commit()

    """
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            assetPriceHist = AssetPriceHistory.query.filter(AssetPriceHistory.id == id).one_or_none()
            assetPriceHist.price = '259.21'
            assetPriceHist.update()
    """

    def update(self):
        db.session.commit()

    """
    delete()
        deletes a new model into a database
        the model must exist in the databasec
        EXAMPLE
            assetPriceHist = AssetPriceHistory(asset_type=req_asset_type,
                                                price=req_price,
                                                date=req_date,
                                                portfolio_id=req_portfolio_id)
            assetPriceHist.delete()
    """

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "asset_type": self.asset_type,
            "price": self.price,
            "date": self.date,
            "portfolio_id": self.portfolio_id
        }