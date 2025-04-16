from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

# Configuración de la base de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)

# Declarar la base para los modelos
Base = declarative_base()

# Definición del modelo Producto
class ProductoSQLAlchemy(Base):
    __tablename__ = 'productos_sqlalchemy'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    fecha_ingreso = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<Producto(codigo='{self.codigo}', nombre='{self.nombre}', precio={self.precio})>"

# Crear tablas
Base.metadata.create_all(engine)

# Crear una sesión
SessionLocal = sessionmaker(bind=engine)

# Función para obtener una sesión
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
        
# Funciones de manipulación de datos
def agregar_producto(nombre, codigo, descripcion, precio, stock):
    db = get_db()
    try:
        nuevo_producto = ProductoSQLAlchemy(
            nombre=nombre,
            codigo=codigo,
            descripcion=descripcion,
            precio=precio,
            stock=stock
        )
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto
    except Exception as e:
        db.rollback()
        raise e

def obtener_productos():
    db = get_db()
    return db.query(ProductoSQLAlchemy).all()

def obtener_producto_por_codigo(codigo):
    db = get_db()
    return db.query(ProductoSQLAlchemy).filter(ProductoSQLAlchemy.codigo == codigo).first()

def actualizar_stock(codigo, cantidad):
    db = get_db()
    try:
        producto = db.query(ProductoSQLAlchemy).filter(ProductoSQLAlchemy.codigo == codigo).first()
        if producto:
            producto.stock = cantidad
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e

def eliminar_producto(codigo):
    db = get_db()
    try:
        producto = db.query(ProductoSQLAlchemy).filter(ProductoSQLAlchemy.codigo == codigo).first()
        if producto:
            db.delete(producto)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e 