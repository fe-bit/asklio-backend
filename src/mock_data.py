


from .models import ProcurementRequest, Status, OrderLine
from .db import get_db_connection, serialize_order_lines, get_commodity_group


def add_mock_data():
	conn = get_db_connection()
	c = conn.cursor()
	# Check if mock data exists
	c.execute('SELECT COUNT(*) FROM procurement_requests')
	count = c.fetchone()[0]
	if count > 0:
		return

	commodity = get_commodity_group("001")
	if commodity is None:
		raise ValueError("Commodity group with id '001' does not exist. Please add it before inserting mock data.")
	mock_requests = [
		ProcurementRequest(
			requestor_name='Alice Johnson',
			title='Laptop Purchase',
			vendor_name='TechWorld Inc.',
			vat_id='DE123456789',
			commodity_group='IT Equipment',
			total_cost=1899.99,
			department='Engineering',
			status=Status.open,
			order_lines=[
				OrderLine(
					position_description='Dell XPS 13 Laptop',
					unit_price=1599.99,
					amount=1,
					unit='piece',
					total_price=1599.99
				),
				OrderLine(
					position_description='Laptop Bag',
					unit_price=50.00,
					amount=2,
					unit='piece',
					total_price=100.00
				),
				OrderLine(
					position_description='Wireless Mouse',
					unit_price=100.00,
					amount=2,
					unit='piece',
					total_price=200.00
				),
			]
		),
		ProcurementRequest(
			requestor_name='Bob Smith',
			title='Office Chairs',
			vendor_name='Comfort Seating',
			vat_id='GB987654321',
			commodity_group='Office Supplies',
			total_cost=1250.0,
			department='Facilities',
			status=Status.open,
			order_lines=[
				OrderLine(
					position_description='Ergonomic Office Chair',
					unit_price=250.00,
					amount=5,
					unit='piece',
					total_price=1250.00
				),
			]
		),
		ProcurementRequest(
			requestor_name='Carol Lee',
			title='Cloud Subscription',
			vendor_name='CloudCo',
			vat_id='US55-778899',
			commodity_group='Software',
			total_cost=499.5,
			department='IT',
			status=Status.open,
			order_lines=[
				OrderLine(
					position_description='Cloud Storage Subscription',
					unit_price=99.90,
					amount=5,
					unit='license',
					total_price=499.50
				),
			]
		),
	]

	for req in mock_requests:
		c.execute('''INSERT INTO procurement_requests (
			requestor_name, title, vendor_name, vat_id, commodity_group, total_cost, department, status, order_lines
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
			req.requestor_name, req.title, req.vendor_name, req.vat_id, req.commodity_group,
			req.total_cost, req.department, req.status, serialize_order_lines(req.order_lines)
		))
	conn.commit()
