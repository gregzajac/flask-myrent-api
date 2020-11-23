import os
from flask import jsonify, abort, current_app, send_file, request, url_for, \
                    render_template, redirect
from werkzeug.utils import secure_filename
from pathlib import Path

from myrent_app import db
from myrent_app.pictures import pictures_bp
from myrent_app.models import Picture, Flat, PictureSchema, picture_schema
from myrent_app.utils import allowed_picture, token_landlord_required


@pictures_bp.route('/', methods=['GET'])
def upload_test_file():
    return render_template('myrent_api_documentation.html')


@pictures_bp.route('/pictures', methods=['GET'])
def get_pictures():
    pictures = Picture.query.all()

    return jsonify({
        'success': True,
        'data': PictureSchema(many=True).dump(pictures)
    })


@pictures_bp.route('/flats/<int:flat_id>/pictures', methods=['GET'])
def get_flat_pictures(flat_id: int):
    flat = Flat.query.get_or_404(flat_id, description=f'Flat with id {flat_id} not found')

    return jsonify({
        'success': True,
        'data': PictureSchema(many=True).dump(flat.pictures)
    })


@pictures_bp.route('/pictures/<int:picture_id>', methods=['GET'])
def get_picture(picture_id: int):
    picture = Picture.query.get_or_404(picture_id, 
                description=f'Picture with id {picture_id} not found')

    return jsonify({
        'success': True,
        'data': picture_schema.dump(picture)
    })


@pictures_bp.route('/flats/<int:flat_id>/pictures', methods=['POST'])
@token_landlord_required
def add_picture(landlord_id: int, flat_id: int):   
    flat = Flat.query.get_or_404(flat_id, description=f'Flat with id {flat_id} not found')

    if flat.landlord_id != landlord_id:
        abort(404, description=f'Flat with id {flat_id} not found')

    file = request.files['picture']
    description = request.form.get('description')

    if file.filename == '':
        abort(422, description=f'Picture is not attached')

    if not allowed_picture(file.filename):
        extensions = [e for e in current_app.config.get('ALLOWED_EXTENSIONS')]
        abort(422, description=f'Not allowed picture extension ({extensions})')

    picture_with_this_filename = Picture.query.filter(Picture.name == file.filename).first()
    if picture_with_this_filename is not None:
        abort(409, description=f'Picture with name {file.filename} already exists')

    filename = secure_filename(file.filename)
    target = os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename)

    picture = Picture(name=filename, path=str(target), flat_id=flat_id)
    if description is not None:
        picture.description = description

    db.session.add(picture)
    db.session.commit()
    file.save(target)

    return jsonify({
        'success': True,
        'data': picture_schema.dump(picture)
    }), 201


@pictures_bp.route('/pictures/<int:picture_id>', methods=['DELETE'])
@token_landlord_required
def delete_picture(landlord_id: int, picture_id: int):
    picture = Picture.query.get_or_404(picture_id, 
                                description=f'Picture with id {picture_id} not found')

    if picture.flat.landlord_id != landlord_id:
        abort(404, description=f'Picture with id {picture_id} not found')

    db.session.delete(picture)
    db.session.commit()

    if os.path.isfile(picture.path):
        os.remove(picture.path)

    return jsonify({
        'success': True,
        'data': f'Picture with id {picture_id} has been deleted'
    })