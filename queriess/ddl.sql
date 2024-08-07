CREATE TABLE sellers (
	seller_id VARCHAR NOT NULL,
	seller_state VARCHAR,
	CONSTRAINT SELLERS_PK PRIMARY KEY (seller_id)
);

CREATE TABLE products (
	product_id VARCHAR NOT NULL,
	product_category_name VARCHAR,
	product_weight_g FLOAT,
	CONSTRAINT PRODUCTS_PK PRIMARY KEY (product_id)
);

CREATE TABLE orders (
	order_id VARCHAR NOT NULL,
	"timestamp" VARCHAR,
	customer_contact VARCHAR,
	CONSTRAINT ORDERS_PK PRIMARY KEY (order_id)
);

CREATE TABLE order_reviews (
	review_id VARCHAR NOT NULL, 
	order_id VARCHAR, 
	review_score INTEGER, 
	review_comment_message VARCHAR, 
	PRIMARY KEY (review_id), 
	FOREIGN KEY(order_id) REFERENCES orders (order_id)
);

CREATE TABLE order_items (
	order_items_pk INTEGER NOT NULL,
	order_id VARCHAR,
	product_id VARCHAR,
	seller_id VARCHAR,
	price FLOAT,
	CONSTRAINT ORDER_ITEMS_PK PRIMARY KEY (order_items_pk),
	CONSTRAINT FK_order_items_orders FOREIGN KEY (order_id) REFERENCES orders(order_id),
	CONSTRAINT FK_order_items_products FOREIGN KEY (product_id) REFERENCES products(product_id),
	CONSTRAINT FK_order_items_sellers FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);
