from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from .forms import *
from ..auth.forms import register_form
from . import *
from wtforms import ValidationError, validators
from ..app import db, bcrypt, login_manager
from flask import current_app
from flask_login import (
    UserMixin,
    login_required,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    abort,
    session,
    g,
    send_from_directory,
)
from werkzeug.routing import BuildError
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from ..utils import *
from flask_bcrypt import generate_password_hash, check_password_hash
from ..models import *

adm = Blueprint("adm", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def global_hostels():
    g_hostels = Hostel.query.with_entities(Hostel.name, Hostel.id)
    g.global_h = list(g_hostels)
    return g.global_h
    

# ADMIN route
@adm.route("/admin", methods=("GET", "POST"), strict_slashes=False)
def admindash():
    hostels = Hostel.query.order_by(Hostel.id.desc()).all()
    return render_template("dashboard.html",hostels=hostels)

@adm.route("/results", methods=("GET", "POST"), strict_slashes=False)
def result():
    hostels = Hostel.query.order_by(Hostel.id.desc()).all()
    return render_template("action.html",hostels=hostels)


@adm.route("/users", methods=("GET", "POST"), strict_slashes=False)
def users():
    all_hostels = global_hostels()
    users = User.query.order_by(User.id.desc()).all()
    form = register_form()
    if form.validate_on_submit():
        try:
            uname = form.uname.data
            email = form.email.data
            pwd = form.pwd.data

            # print(uname,email,pwd)
            newuser = User(
                uname=uname,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("adm.users"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")

    return render_template("users.html",form=form,users=users,all_hostels=all_hostels,action="Add User",action_btn="Save")


@adm.route("/transactions", methods=("GET", "POST"), strict_slashes=False)
def transactions():
    return render_template("transactions.html")

@adm.route("/hostels", methods=("GET", "POST"), strict_slashes=False)
def hostels():
    hostels = Hostel.query.order_by(Hostel.id.desc()).all()
    form = AddHostel()
    if form.validate_on_submit():
        try:
            name = form.name.data
            location = form.location.data
            management = form.management.data
            rooms = form.rooms.data
            caretaker = form.caretaker.data
            description = form.description.data
            newHostel = Hostel(
                name=name,
                location=location,
                management=management,
                rooms=rooms,
                caretaker=caretaker,
                description=description
                )

            db.session.add(newHostel)
            db.session.commit()
            flash("Hostel has been updated", "success")
            return redirect(url_for("adm.hostels"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")

    return render_template("hostels.html",form=form,hostels=hostels,action="Add Hostel",action_btn="Save")

@adm.route("/hostel/<int:hostel_id>/view", methods=("GET", "POST"), strict_slashes=False)
@login_required
# @admin_required
def hostel_view(hostel_id):
    form = Rooms()
    hostel =  Hostel.query.filter_by(id=hostel_id).first()
    rooms= Room.query.filter_by(hostel_id=hostel_id).order_by(Room.id.desc()).all()
    
    if form.validate_on_submit():
        try:
            hostel_id = hostel_id
            rent = form.rent.data
            deposit = form.deposit.data
            amenities = form.amenities.data
            size = form.size.data
            status = form.status.data
            newRoom = Room(
                hostel_id=hostel_id,rent=rent,deposit=deposit,amenities=amenities,size=size,status=status
                )

            db.session.add(newRoom)
            db.session.commit()
            flash("Room has been added", "success")
            return redirect(url_for("adm.hostels"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")

    return render_template("hostel_view.html",hostel=hostel,rooms=rooms,form=form,action_btn="Save")

@adm.route("/rooms", methods=("GET", "POST"), strict_slashes=False)
def rooms():
    rooms = Room.query.order_by(Room.id.desc()).all()

    return render_template("rooms.html",rooms=rooms)

@adm.route("/edit/<int:user_id>", methods=("GET", "POST"), strict_slashes=False)
@login_required
# @admin_required
def account(user_id):
    user =  User.query.filter_by(id=user_id).first()
    form = UpdateProfile()
    if form.validate_on_submit():
        try:

            user.uname = form.uname.data
            user.email = form.email.data

            db.session.commit()
            flash("User has been updated", "success")
            return redirect(url_for("adm.users"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    elif request.method == "GET":
        form.uname.data = user.uname
        form.email.data = user.email

    return render_template("users.html",form=form,user=user,action="Edit User",action_btn="Save Changes")



@adm.route("/delete/<int:user_id>", methods=("GET", "POST"), strict_slashes=False)
@login_required
# @admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    flash("User has been deleted succesfully ", "success")
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("adm.admindash"))