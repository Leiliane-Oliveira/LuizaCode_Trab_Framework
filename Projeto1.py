from fastapi import FastAPI
from typing import List
from typing import Union #Não sei pq importou
from typing import TypedDict #Não sie pq importoufrom typing import Union
from pydantic import BaseModel

app = FastAPI()

OK = "OK"
FALHA = "FAILURE"

# Classe representando os dados do endereço do cliente.
class Address(BaseModel):
    id: Union[int, None] = None
    id_user: int
    road: str
    number: str
    complement: str
    cep: str
    city: str
    state: str

# Classe representando os dados do cliente.
class User(BaseModel):
    id: int
    name: str
    email: str

# Classe representando a lista de endereços de um cliente
class UserAddressList(BaseModel):
    user: User
    address: List[Address] = []
    
# Classe representando os dados do produto.
class Product(BaseModel):
    id: int
    name: str
    description: str
    category: str
    subcategory: str
    price: float
    
# Classe representando o carrinho de compras de um cliente com uma lista de produtos.
class ShoppingCart():
    id_user: int
    products: List[Product] = []
    total_price: float
    quantity_of_products: int
    
# Persistência de dados (bancos)
db_users = {}
db_products = {}
db_add = {}
db_cart = {}

# Rotas da API

# Saudação de boas-vindas.
@app.get("/")
async def welcome():
    site = "Seja bem-vinda e fça uma ótima compra!"
    return site.replace('\n', '')

# Cria um usuário
# Um usuário irá ter um código identificador único no sistema.
@app.post("/user/")
async def created_user(user: User):
    if user.id in db_users:
        return "Id já existe na base de dados"
    db_users[user.id] = user
    return OK

# Consultar um usuário pelo seu código identificador.
@app.get("/user/{id}")
async def retorn_user_by_id(id: int):
    if id in db_users:
        return db_users[id]
    return FALHA

# Consultar um usuário pelo primeiro nome dele.
@app.get("/user/")
async def retorn_user_by_name(name: str):
    for id in db_users:
        if db_users[id].name == name:
            return db_users[id]
    return FALHA

# Remover um usuário pelo código dele.
@app.delete("/user/{id}")
async def delete_user(id: int):
    if id in db_users:
        db_users.pop(id)
        return OK
    return FALHA

# Cadastrar o(s) endereço(s) do usuário.
@app.post("/address/")
async def created_address(address: Address):
    if address.id_user not in db_users:
        return FALHA
    if address.id in db_add:
        return "Id já existe na base de Dados"
    id_new_address = len(list(db_add)) + 1
    address.id = id_new_address 
    db_add[id_new_address]  = address
    return OK

 #Pesquisar os endereços de um usuário.
@app.get("/user/{id_user}/address/")
async def return_address_by_user(id_user: int):
    address = []
    if id_user not in db_users:
        return FALHA
    for id in db_add:
        if db_add[id].id_user == id_user:
            address.append(db_add[id])
    return address

# Remover um endereço do usuário pelo seu código identificador.
@app.delete("/user/{id_user}/address/{id}")
async def delete_address(id: int, id_user:int):
    if id_user not in db_add:
        return FALHA
    else:
        if id not in db_add:
            return FALHA
        db_add.pop(id)
        return OK
    
# Cadastrar um produto, que possua nome, descrição, preço e código identificador.
@app.post("/product/")
async def criar_product(product: Product):
    if product.id in db_products:
        return "Id já existente na base de Dados"
    db_products[product.id] = product
    return OK

# Remover um produto pelo código.
@app.delete("/product/{id_product}/")
async def delete_product(id_product: int):
    if id_product in db_products:
        db_products.pop(id_product)
        return OK
    return FALHA

# Criar um carrinho de compras associado a um usuário.
# Adicionar produtos ao carrinho de compras.
# Calcular o valor total do carrinho.
@app.post("/cart/{id_user}/{id_product}")
async def add_cart(id_user: int, id_product: int):
    if id_user not in db_users or id_product not in db_products:
        return FALHA

    if id_user in db_cart:
        db_cart[id_user].products.append(db_products[id_product])
        db_cart[id_user].total_price = db_cart[id_user].total_price + \
            db_products[id_product].price
        db_cart[id_user].quantity_of_products= len(
            db_cart[id_user].products)
    else:
        shopping_cart= ShoppingCart()
        shopping_cart.id_user = id_user
        shopping_cart.products.append(db_products[id_product])

        shopping_cart.total_price = 0.0
        shopping_cart.total_price = shopping_cart.total_price + \
            db_products[id_product].price

        shopping_cart.quantity_of_products = len(
            shopping_cart.products
            )

        db_cart[id_user] = shopping_cart

    return db_cart[id_user]

#Consultar carrinho de compras
@app.get("/cart/{id_user}")
async def return_cart_by_user(id_user: int):
    if id_user not in db_users:
        return FALHA
    return db_cart[id_user] 

# Remover produtos do carrinho de compras.
@app.delete("/cart/{id_user}/product/{id_product}")
async def remove_product(id_user: int, id_product: int):
    if id_user not in db_cart:
        return FALHA
    if id_product not in db_cart:
        return FALHA

    db_cart[id_user].products.remove(db_products[id_product])
    db_cart[id_user].total_price = db_cart[id_user].total_price - \
        db_products[id_product].price
    db_cart[id_user].quantity_of_products = db_cart[id_user].quantity_of_products - 1
    return OK

#Calcular o valor total do carrinho
@app.get("/cart/{id_user}/total")
async def return_total_cart(id_user: int):
    if id_user not in db_cart:
        return FALHA
    total = db_cart[id_user].total_price
    return total

#Remover o Carrinho de Compras
@app.delete("/cart/{id_user}")
async def delete_cart(id_user: int):
    if id_user in db_cart:
        db_cart.pop(id_user)
        return OK
    return FALHA