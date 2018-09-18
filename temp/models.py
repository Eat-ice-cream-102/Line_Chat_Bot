# models.py
from main import db

class employee(db.Model):
    __tablename__ = 'employee'
    test_no = db.Column(db.Numeric(4), primary_key=True)
    test_name = db.Column(db.String(20), nullable=False)
    def __init__(self, test_no, test_name):
        self.test_no = test_no
        self.test_name = test_name
    def __repr__(self):
        return '<Test %r>' % self.test_name

class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Numeric(4), primary_key=True)
    test_name = db.Column(db.String(20), nullable=False)
    def __init__(self, id, test_name):
        self.id = id
        self.test_name = test_name
    def __repr__(self):
        return '<Test %r>' % self.test_name
