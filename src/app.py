from flask import Flask, render_template, url_for, request, make_response, session, redirect, jsonify,escape,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt

from os import environ
import os
import json
import base64
import csv
from usuario import Usuario
import pdfkit
from werkzeug.security import generate_password_hash, check_password_hash
UPLOAD_FOLDER=os.path.abspath("./archivos/")
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
dbdir="sqlite:///"+os.path.abspath(os.getcwd())+"/database.db"

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = dbdir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER


db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name =  db.Column(db.String(70))
    last_name = db.Column(db.String(70))
    username = db.Column(db.String(70),unique=True)
    contrasena = db.Column(db.String(70))

class Clientes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name =  db.Column(db.String(70))
    last_name = db.Column(db.String(70))
    username = db.Column(db.String(70),unique=True)
    contrasena = db.Column(db.String(70))

class Receta(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Titulo = db.Column(db.String(70))
    Resumen = db.Column(db.String(120))
    Ingredientes = db.Column(db.String(80))
    Preparacion = db.Column(db.String(80))
    Tiempo_preparacion = db.Column(db.String(20))
    Imagenes = db.Column(db.String(80))
    




app.secret_key = b'contrasenita'



def validar_login(user, contrasena):
    for usuario in usuarios:
        if usuario.usuario == user and usuario.contrasena == contrasena:
            return usuario
    return None

def validar_cliente(user,contrasena):
    cliente = Clientes.query.filter_by(username=user).first()
    if cliente:
        nombre = cliente.name
        contraseña= cliente.contrasena
        if contraseña == contrasena:
             return nombre
    return None

@app.route('/')
def init():
    return redirect("home")    

@app.route('/home')
def home():
    recetas = Receta.query.all()
    if 'usuario_logeado' in session:
        return render_template("home2.html",usuario=session['usuario_logeado'],recetas=recetas)
    return render_template('home.html', usuario=None,recetas=recetas)

@app.route('/homeadmin')
def homeadmin():
    recetas = Receta.query.all()
    if 'usuario_logeado' in session:
        return render_template("homadmin.html",usuario=session['usuario_logeado'],recetas=recetas)
    return render_template('home.html', usuario=None,recetas=recetas)  
 


@app.route('/login', methods=['POST', 'GET'])
def login():
    error= None
    if request.method =='POST':
        admin = request.form['usuario']
        contra = request.form['contrasena']
        busqueda = Usuario.query.filter_by(username=admin).first()
        if busqueda:
            contra2 = busqueda.contrasena
            if contra == contra2:
                session['usuario_logeado']=admin
                return redirect('homeadmin')
            else:
                error="contraseña invalida"
                return render_template('login.html', usuario=None, error=error,bienvenido="Admin")
    if 'usuario_logeado' in session:
        return redirect('homeadmin')
    return render_template('login.html',error=None,bienvenido="Admin")

@app.route('/login2', methods=['POST', 'GET'])
def loginadmin():
    error= None
    if request.method =='POST':
        cliente = request.form['usuario']
        contra = request.form['contrasena']
        busqueda = Clientes.query.filter_by(username=cliente).first()
        if busqueda:
            contra2 = busqueda.contrasena
            if contra == contra2:
                session['usuario_logeado']=cliente
                return redirect('home')
            else:
                error="contraseña invalida"
                return render_template('login.html', usuario=None, error=error,bienvenido="cliente")
    if 'usuario_logeado' in session:
        return redirect('home')
    return render_template('login.html',error=None,bienvenido="cliente")


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('usuario_logeado', None)
    return redirect('login')


@app.route('/registro',methods=['POST','GET'])
def registro():
    if request.method=='POST':
        nombre=request.form['nombre']
        apellido=request.form['apellido']
        userrr=request.form['usuario']
        contrasena = request.form['contrasena']
        contrasena2 =request.form['contrasena2']
        if contrasena==contrasena2:
            busqueda = Clientes.query.filter_by(username=userrr).first()
            if busqueda:
                contrañamal = "el usuario ya existe"
                return render_template('registro.html', error=contrañamal)
            else:
                    nuevocliente = Clientes(name=nombre,last_name=apellido,username=userrr,contrasena=contrasena)
                    db.session.add(nuevocliente)
                    db.session.commit()
                    next = request.args.get('next',None)
                    if next:
                        return redirect (next)
                    return redirect(url_for('loginadmin'))
                
        else:
            contrañamal = "contraseña debe coincidir"
            return render_template('registro.html', error=contrañamal)
    return render_template("registro.html",error=None)   

@app.route('/perfil',methods=['POST','GET'])
def perfil():
    usuario=session['usuario_logeado']
    user =session['usuario_logeado']
    nombre = Clientes.query.filter_by(username=user).first()
    if nombre:
        ape=nombre.last_name
        nom=nombre.name
        contra=nombre.contrasena       
    if request.method=='POST':
        nom=request.form['nombre']
        ape=request.form['apellido']
        userrr=request.form['usuario']
        contrasena = request.form['contrasena']
        contrasena2 =request.form['contrasena2']
        if contrasena==contrasena2:
            busqueda = Clientes.query.filter_by(username=userrr).first()
            if busqueda:
                n=nombre.username
                if n==userrr:
                    nombre.name= request.form['nombre']
                    nombre.last_name=request.form['apellido']
                    nombre.contrasena=request.form['contrasena']
                    db.session.add(nombre)
                    db.session.commit()
                    next = request.args.get('next',None)
                    if next:
                        return redirect (next)
                    return redirect(url_for('logout'))
                else:  
                    contrañamal = "el usuario ya existe"
                    return render_template('modificarperfl.html', error=contrañamal,usuario=usuario,nombre=nom,apellido=ape,contrasena=contra) 
            else:   
                nombre.name= request.form['nombre']
                nombre.last_name=request.form['apellido']
                nombre.username=request.form['usuario']
                nombre.contrasena=request.form['contrasena']
                db.session.add(nombre)
                db.session.commit()
                next = request.args.get('next',None)
                if next:
                    return redirect (next)
                return redirect(url_for('logout'))   
        else:
            contrañamal = "contraseña debe coincidir"
            return render_template('modificarperfl.html', error=contrañamal,usuario=usuario,nombre=nom,apellido=ape,contrasena=contra)
    return render_template('modificarperfl.html',error=None,usuario=usuario,nombre=nom,apellido=ape,contrasena=contra)  

@app.route('/perfiladmin',methods=['POST','GET'])
def perfiladmin():
    usuario=session['usuario_logeado']
    user =session['usuario_logeado']
    nombre = Usuario.query.filter_by(username=user).first()
    if nombre:
        ape=nombre.last_name
        nom=nombre.name
        contra=nombre.contrasena       
    if request.method=='POST':
        nom=request.form['nombre']
        ape=request.form['apellido']
        userrr=request.form['usuario']
        contrasena = request.form['contrasena']
        contrasena2 =request.form['contrasena2']
        if contrasena==contrasena2:
            busqueda = Usuario.query.filter_by(username=userrr).first()
            if busqueda:
                n=nombre.username
                if n==userrr:
                    nombre.name= request.form['nombre']
                    nombre.last_name=request.form['apellido']
                    nombre.contrasena=request.form['contrasena']
                    db.session.add(nombre)
                    db.session.commit()
                    next = request.args.get('next',None)
                    if next:
                        return redirect (next)
                    return redirect(url_for('logout'))
                else:  
                    contrañamal = "el usuario ya existe"
                    return render_template('modifcarperfiladmin.html', error=contrañamal,usuario=usuario,nombre=nom,apellido=ape,contrasena=contra) 
            else:   
                nombre.name= request.form['nombre']
                nombre.last_name=request.form['apellido']
                nombre.username=request.form['usuario']
                nombre.contrasena=request.form['contrasena']
                db.session.add(nombre)
                db.session.commit()
                next = request.args.get('next',None)
                if next:
                    return redirect (next)
                return redirect(url_for('logout'))   
        else:
            contrañamal = "contraseña debe coincidir"
            return render_template('modifcarperfiladmin.html', error=contrañamal,usuario=usuario,nombre=nom,apellido=ape,contrasena=contra)
    return render_template('modifcarperfiladmin.html',error=None,usuario=usuario,nombre=nom,apellido=ape,contrasena=contra)    

@app.route('/login/contraseña',methods=['POST','GET'])
def olvide():
    if request.method=='POST':
        consulta = request.form['usuario']
        error = Clientes.query.filter_by(username=consulta).first()
        if error:
            loencontre="tu contrasena es:"+error.contrasena
            return render_template('contraeña.html', error=loencontre)
        else:
            loencontre="no lo encontre"
            return render_template('contraeña.html', error=loencontre)
    return render_template("contraeña.html",error=None)   

@app.route('/receta',methods=['POST','GET'])
def receta():
    if request.method=='POST':
        titulo = request.form['titulo']
        resumen = request.form['resumen']
        ingredientes = request.form['ingredientes']
        preparacion = request.form['preparacion']
        tiempo = request.form['tiempo']
        link = request.form['imagen']
        nuevareceta = Receta(Titulo=request.form['titulo'],Resumen=resumen,Ingredientes=ingredientes,Preparacion=preparacion,Tiempo_preparacion=tiempo,Imagenes=link)
        db.session.add(nuevareceta)
        db.session.commit()
        next = request.args.get('next',None)
        if next:
            return redirect (next)
        return redirect(url_for('home'))
    return render_template("recetas.html")
@app.route('/recetaadmin',methods=['POST','GET'])
def recetaadmin():
    if request.method=='POST':
        titulo = request.form['titulo']
        resumen = request.form['resumen']
        ingredientes = request.form['ingredientes']
        preparacion = request.form['preparacion']
        tiempo = request.form['tiempo']
        link = request.form['imagen']
        nuevareceta = Receta(Titulo=request.form['titulo'],Resumen=resumen,Ingredientes=ingredientes,Preparacion=preparacion,Tiempo_preparacion=tiempo,Imagenes=link)
        db.session.add(nuevareceta)
        db.session.commit()
        next = request.args.get('next',None)
        if next:
            return redirect (next)
        return redirect(url_for('home'))
    return render_template("recetadmin.html")


@app.route('/recetas/<string:nombre>')
def idreceta(nombre):
        buscarreceta=Receta.query.filter_by(Titulo=nombre).first()
        if buscarreceta:
            res=buscarreceta.Resumen
            tit=buscarreceta.Titulo
            ing=buscarreceta.Ingredientes
            prep=buscarreceta.Preparacion
            tie=buscarreceta.Tiempo_preparacion
            imagen=buscarreceta.Imagenes
        return render_template("receta.html",titulo=tit,resumen=res,ingredientes=ing,preparacion=prep,tiempo=tie,imagen=imagen)

@app.route('/delete/<string:nombre>',methods=['DELETE','GET'])
def delete(nombre):
        buscarreceta=Receta.query.filter_by(Titulo=nombre).first()
        if buscarreceta:
            db.session.delete(buscarreceta)
            db.session.commit()
        return redirect(url_for('tablarec'))
@app.route('/tabla',methods=['DELETE','GET'])
def tablarec():
    tabla = Receta.query.all()
    return render_template("tablarecetas.html",recetas=tabla)     
@app.route('/tablaclientes',methods=['DELETE','GET'])
def tablaclientes():
    tabla = Clientes.query.all()
    return render_template("tablaclientes.html",clientes=tabla)
    
      

@app.route('/deletec/<string:nombre>',methods=['DELETE','GET'])
def deletecliente(nombre):
        buscarreceta=Clientes.query.filter_by(username=nombre).first()
        if buscarreceta:
            db.session.delete(buscarreceta)
            db.session.commit()
        return redirect(url_for('tablaclientes'))

@app.route('/cargarArchivo', methods=['POST','GET'])
def agregarRecetas():
    if request.method=='POST':
        datos = request.get_json()

        if datos['data'] == '':
            return {"msg": 'Error en contenido'}

        contenido = base64.b64decode(datos['data']).decode('utf-8')

        filas = contenido.splitlines()
        reader = csv.reader(filas, delimiter=';')
        for row in reader:
            receta = Receta(Titulo=row[0],Resumen=row[1],Ingredientes=row[2],Preparacion=row[3],Tiempo_preparacion=row[4],Imagenes=row[5])
            db.session.add(receta)
            db.session.commit()
        return render_template("homeadmin.html")
    return render_template("subir.html")
@app.route("/pdf",methods=['GET'])
def index():
    recetas = Receta.query.all()
    html = render_template(
        "reporte.html",
        recetas=recetas)
    pdfkit.from_string(html,"recetas.pdf",configuration=config)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=reporte.pdf"
    return response
    return render_template("homeadmin.html")
     
if __name__=='__main__':
    db.create_all()
    app.run(debug=True,port=5000)