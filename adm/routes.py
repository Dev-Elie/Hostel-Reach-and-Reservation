from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from auth.forms import register_form
from .forms import *
from . import *
from wtforms import ValidationError, validators
from app import db, bcrypt, login_manager
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
from flask_bcrypt import generate_password_hash, check_password_hash
from models import *
from decorators import admin_required, moderator_required, permission_required
import json,re

adm = Blueprint("adm", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def global_hostels():
    g_hostels = Hostel.query.with_entities(Hostel.name, Hostel.id)
    g.global_h = list(g_hostels)
    return g.global_h
    
def all_rooms(par):
    room_count = list()
    for i in par:
        i = re.sub('[^0-9]','', str(i))
        room_count.append(int(i))
    available = sum(room_count)

    return available

# ADMIN route
@adm.route("/admin", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
def admindash():
    hostels = Hostel.query.order_by(Hostel.id.desc()).all()

    booked = Room.query.order_by(Room.id.desc()).count()
    vacant = Room.query.order_by(Room.id.desc()).count()
    occupied = Room.query.order_by(Room.id.desc()).count()


    bs = Room.query.filter_by(size='Bedsitter').order_by(Room.id.desc()).count()
    single = Room.query.filter_by(size='Single').order_by(Room.id.desc()).count()    
    oneb = Room.query.filter_by(size='1 B').order_by(Room.id.desc()).count()
    twob = Room.query.filter_by(size='2 B').order_by(Room.id.desc()).count()


    data=list((booked,vacant,occupied))
    labels=list(("booked","vacant","occupied"))



    labels2=list(("Bedsitter","Single","1 B","2 B"))
    data2 = list((bs,single,oneb,twob))

    

    user_count = User.query.order_by(User.id.desc()).count()
    hostel_count = Hostel.query.order_by(Hostel.id.desc()).count()

    room_count = Hostel.query.with_entities(Hostel.rooms).all()
    room_count = all_rooms(room_count)

    return render_template("adm/dashboard.html",
        hostels=hostels,
        data=data,
        data2=data2,
        labels=labels,
        labels2=labels2,
        user_count=user_count,
        hostel_count=hostel_count,
        room_count=room_count,
        title='Admin Dashboard'
        )

# All Users route
@adm.route("/users", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
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

    return render_template("adm/users.html",
        form=form,
        users=users,
        all_hostels=all_hostels,
        action="Add User",
        action_btn="Save",
        title='Users'
        )

# Hostels route
@adm.route("/hostels", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
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
            contact = form.contact.data
            description = form.description.data
            newHostel = Hostel(
                name=name,
                location=location,
                management=management,
                rooms=rooms,
                caretaker=caretaker,
                contact=contact,
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

    return render_template("adm/hostels.html",
        form=form,
        hostels=hostels,
        action="Add Hostel",
        action_btn="Save",
        title='Hostels')

# View Hostels Route
@adm.route("/hostel/<int:hostel_id>/view", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
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
            newRoom = Room(hostel_id=hostel_id,rent=rent,deposit=deposit,amenities=amenities,size=size)

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

    return render_template("adm/hostel_view.html",
        hostel=hostel,
        rooms=rooms,
        form=form,
        action_btn="Save",
        action_type="Add Room",
        title="Hostel | View")
# Rooms route
@adm.route("/rooms", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
def rooms():
    rooms = Room.query.order_by(Room.id.desc()).all()

    return render_template("adm/rooms.html",rooms=rooms,title='Booked rooms')

# Booked rooms route
@adm.route("/rooms/booked", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
def booked_rooms():
    rooms = BookedRoom.query.order_by(BookedRoom.id.desc()).all()

    return render_template("adm/booked_rooms.html",rooms=rooms,title='Rooms')

                        # ALL EDIT ROUTES
# Edit user route
@adm.route("/edit/<int:user_id>", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
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

    return render_template("adm/users.html",
        form=form,
        user=user,
        action="Edit User",
        action_btn="Save Changes",
        title='Users | Edit')


# Edit rooms route

@adm.route("/rooms/<int:hostel_id>/<int:room_id>", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
# @admin_required
def edit_room(hostel_id,room_id):
    form = Rooms()
    hostel =  Hostel.query.filter_by(id=hostel_id).first()
    rooms= Room.query.filter_by(hostel_id=hostel_id).order_by(Room.id.desc()).all()
    room =  Room.query.filter_by(id=room_id).first()

    if form.validate_on_submit():
        try:
            room.rent = form.rent.data
            room.deposit = form.deposit.data
            room.amenities = form.amenities.data
            room.size = form.size.data

            db.session.commit()
            flash("Room has been updated", "success")
            return redirect(url_for("adm.rooms"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"Room already exists!.", "warning")
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
        form.rent.data = room.rent 
        form.deposit.data = room.deposit 
        form.amenities.data= room.amenities
        form.size.data = room.size

    return render_template("adm/hostel_view.html",
        hostel=hostel,
        rooms=rooms,
        form=form,
        action_btn="Save Changes",
        action_type="Edit Room",
        title='Rooms | Edit')

# Edit hostel
@adm.route("/hostels/<int:hostel_id>/edit", methods=("GET", "POST"), strict_slashes=False)
@login_required
@admin_required
def edit_hostel(hostel_id):
    hostel =  Hostel.query.filter_by(id=hostel_id).first()
    hostels = Hostel.query.order_by(Hostel.id.desc()).all()
    form = AddHostel()
    if form.validate_on_submit():
        try:
            hostel.name = form.name.data
            hostel.location = form.location.data
            hostel.management = form.management.data
            hostel.rooms = form.rooms.data
            hostel.caretaker = form.caretaker.data
            hostel.contact = form.contact.data
            hostel.description = form.description.data

            db.session.commit()
            flash("Hostel has been updated", "success")
            return redirect(url_for("adm.hostels"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"Hostel already exists!.", "warning")
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
        form.name.data=hostel.name
        form.location.data = hostel.location
        form.management.data = hostel.management
        form.rooms.data = hostel.rooms
        form.caretaker.data = hostel.caretaker
        form.contact.data = hostel.contact
        form.description.data = hostel.description

    return render_template("adm/hostels.html",
        form=form,
        hostels=hostels,
        hostel=hostel,
        action_type="Edit Hostel",
        action_btn="Save Changes",
        title='Hostel | Edit')


                                # ALL DELETE ROUTES
@adm.route("/delete/<int:user_id>", methods=("GET", "POST"), strict_slashes=False)
@login_required
# @admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    flash("User has been deleted succesfully ", "success")
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("adm.admindash"))