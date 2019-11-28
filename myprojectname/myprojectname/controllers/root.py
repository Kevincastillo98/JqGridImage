# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from myprojectname import model
from myprojectname.controllers.secure import SecureController
from myprojectname.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from myprojectname.lib.base import BaseController
from myprojectname.controllers.error import ErrorController

from myprojectname.model import Entrevistador,Solicitante,solicitante_entrevistador_tabla
import transaction

from myprojectname.controllers.jqgrid import jqgridDataGrabber


from myprojectname.lib.base import BaseController
from myprojectname.controllers.error import ErrorController
import requests
import base64

from tg import  render_template

__all__ = ['RootController']


class RootController(BaseController):
    pass



    @expose('myprojectname.templates.ManyToMany.Relaciones')
    def GridPrincipal(self):
    return dict()


    @expose('json')
    def displayUsuarios(self, **kw):
        displayusuarios = render_template({"list": list}, "mako", 'myprojectname.templates.ManyToMany.displayusuarios')
        return dict(displayusuarios=displayusuarios)


    @expose('json')
    def displayBooks(self, **kw):
        displaybooks = render_template({"list": list}, "mako", 'myprojectname.templates.ManyToMany.displaybooks')
        return dict(displaybooks=displaybooks)


    @expose('json')
    def loadUsuario(self, **kw):
        filter = []
        return jqgridDataGrabber(Usuario, 'usuario_id', filter, kw).loadGrid()


    @expose('json')
    def updateUsuario(self, **kw):
        filter = []
        return jqgridDataGrabber(Usuario, 'usuario_id', filter, kw).updateGrid()


    @expose('json')
    def loadAuthor(self, **kw):
        filter = []
        return jqgridDataGrabber(Author, 'author_id', filter, kw).loadGrid()


    @expose('json')
    def addUsuario(self, **kw):
        print(kw)

        if kw["usuario_id"] == 0:
            kw['handler'] = Usuario()
        else:
            kw['handler'] = DBSession.query(Usuario).filter_by(usuario_id=kw['usuario_id']).first()
        dialogagrega = render_template({"list": list}, "mako", 'myprojectname.templates.ManyToMany.agregausuario')
        print(dialogagrega)
        return dict(dialogagrega=dialogagrega)


    @expose('json')
    def saveFile(self, **kw):
        print(kw)
        name = kw["name"]
        age = kw["age"]
        phone = kw["phone"]
        email_address = kw["email_address"]

        if kw["image"] == "undefined":
            return dict(error="Archivo obligatorio")
        if name == "" or age == "" or phone == "" or email_address == "":
            return dict(error="Campos obligatorios")

        image = kw["image"]
        if image.file:
            fileName = image.filename
            if fileName.find(".png") > 0 or fileName.find(".jpeg") > 0 or fileName.find(".jpg") > 0 or fileName.find(
                    ".doc") > 0 or fileName.find(".PDF") > 0 or fileName.find(".pdf") > 0:
                ftyoe = ""
                if fileName.find(".png") > 0 or fileName.find(".jpeg") > 0 or fileName.find(".jpg") > 0:
                    ftyoe = "image"
                if fileName.find(".doc") > 0:
                    ftyoe = "doc"
                if fileName.find(".pdf") > 0:
                    ftyoe = "pdf"
                if fileName.find(".PDF") > 0:
                    ftyoe = "pdf"

                newUser = Usuario()
                newUser.name = name
                newUser.age = age
                newUser.phone = phone
                newUser.email_address = email_address
                newUser.image = image.file.read()

                DBSession.add(newUser)
                DBSession.flush()
            else:
                return dict(error="Archivo obligatorio de tipo PNG, JPEG, DOC, PDF")
        return dict(error="ok")


    @expose('json')
    def updateAuthor(self, **kw):
        filter = []
        return jqgridDataGrabber(Author, 'author_id', filter, kw).updateGrid()


    @expose('json')
    def loadBook(self, **kw):
        filter = []
        return jqgridDataGrabber(Book, 'book_id', filter, kw).loadGrid()


    @expose('json')
    def updateBook(self, **kw):
        filter = []
        return jqgridDataGrabber(Book, 'book_id', filter, kw).updateGrid()


    @expose('json')
    def openClose(self, **kw):
        handler_user = DBSession.query(prestamo_books_table).filter_by(usuario_id=kw['id']).all()
        kw['usuario'] = DBSession.query(Usuario).filter_by(usuario_id=kw['id']).first()
        kw['book'] = []
        kw['image'] = ""

        for item in handler_user:
            handler_book = DBSession.query(Book).filter_by(book_id=item.book_id).first()
            if handler_book != None:
                kw['book'].append({'book_name': handler_book.book_name})
        if kw['usuario'].image != None:
            kw['image'] = base64.b64encode(kw['usuario'].image)
            kw['image'] = str(kw['image']).replace("b'", "")
            kw['image'] = str(kw['image']).replace("'", "")
        dialogtemplate = render_template(kw, "mako", 'myprojectname.templates.ManyToMany.hello')
        return dict(dialogtemplate=dialogtemplate)


    @expose('myprojectname.templates.ManyToMany.libreria')
    def tablaBase(self):
        return dict()


    @expose('myprojectname.templates.ManyToMany.testbasededatos')
    def tablaBase2(self):
        return dict()


    @expose('json')
    def tablaBaseConec(self, **kw):
        prestamos = DBSession.query(
            prestamo_books_table).all()  # prestamos recibe todos los elementos de la tabla prestamos
        relacion = []  # Se crea una nueva lista donde almacenaremos datos
        for prestamo in prestamos:  # Recorremos los elementos de prestamos
            usuario = DBSession.query(Usuario).filter_by(
                usuario_id=prestamo.usuario_id).first()  # la variable usuario recibe elementos de la tabla Usuario donde usuario_id es igual a la misma posicion en prestamos
            libro = DBSession.query(Book).filter_by(
                book_id=prestamo.book_id).first()  # la variable libro recibe elementos de la tabla Book donde book_id es igual a la misma posicion en prestamos
            relacion.append({'usuario_id': usuario.name,
                             'book_id': libro.book_name})  # Se regresa a relacion cada posicion recorrida en prestamos y se envia el nombre de las tablas Book y Usuario
        return dict(total=200, page=1, records=500,
                    rows=relacion)  # Regresamos un Json con formato total, page, records, rows que es como lo requiere nuestro jqgrid


    @expose('json')
    def prestamosTemplate(self, **kw):
        list = []
        prestamostemplate = render_template({"list": list}, "mako", 'myprojectname.templates.ManyToMany.prestamostemplate')
        return dict(prestamostemplate=prestamostemplate)


    @expose('json')
    def alertPrestamo(self, **kw):
        usuario_id = kw["usuario_id"]
        book_id = kw["book_id"]
        error = "ok"
        books = []  # lista de libros
        usuario = DBSession.query(Usuario).filter_by(usuario_id=usuario_id).first()  # Busca el Usuario
        print(usuario)
        count = 0
        for item in usuario.book:  # Busca los libros que ya tiene el usuario asignado
            books.append(item)  # Agregalos a la lista
            count += 1
        if count < 3:
            if usuario != None:  # Si existe el usuario busca el libro
                book = DBSession.query(Book).filter_by(book_id=book_id).first()  # Busca el libro
                if book != None:  # Si existe el libro
                    if book not in books:  # Si el libro no lo tiene el usuario aun
                        books.append(book)  # Agrega el libro a la lista
                    else:
                        error = "Ya lo tiene asignado"
                usuario.book = books  # Agrega a la lista de libros al usuario
        else:
            error = "Ya tiene 3 libros asignados. No puede sacar más libros"
        return dict(book=book)
