#db
create database customer;

# 會員
create table `customer`.`member`(
 phone_number varchar(10)  not null,
 member_name varchar(20) Not Null,
 line_account varchar(255) unique,
 brithdate datetime,
 e_mail varchar(50) unique,
 credit_card varchar(50),
 photo varchar(255),
 member_password varchar(255),	 
 has_confirmed boolean,
 c_time datetime,
 has_photo boolean,
 gender int,
 primary key(phone_number)
)CHARACTER SET=utf8;

#確認碼
create table customer.confirmString(
	c_id int auto_increment,
	c_user varchar(10),
	code int,
	c_time datetime,
	primary key(c_id),
	foreign key(c_user) references customer.member(phone_number) 
)CHARACTER SET=utf8;

#進出記錄(訂單)
create table `customer`.`inorout`(
	come_time datetime,
	left_time datetime,
	phone_number varchar(10),
	inorout int,
	primary key(come_time),
	foreign key(phone_number) references `customer`.`member`(phone_number)
)CHARACTER SET=utf8;

#產品類別
create table customer.category(
	category_no int auto_increment,
	category_name varchar(50),
	primary key (category_no)
)CHARACTER SET=utf8;

#產品
create table customer.product(
	product_id int AUTO_INCREMENT,
	product_name varchar(50),
	price int,
	category_no int,
	stock int,
	product_url varchar(255),
	picture_url varchar(255),
	re_product_id int,
	primary key(product_id),
	foreign key(category_no) references customer.category(category_no)
)CHARACTER SET=utf8;

#購物
create table `customer`.`purchase`(
	purchase_no int not null AUTO_INCREMENT,
	come_time datetime,
	product_id int,
	quantity int,
	satisfaction int,
	neededcall int,
	primary key(purchase_no),
	foreign key(come_time) references `customer`.`inorout`(come_time),
	foreign key(product_id) references `customer`.`product`(product_id)
)CHARACTER SET=utf8;
