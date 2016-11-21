# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bookshelf import get_model
from flask import Blueprint, redirect, render_template, request, url_for, jsonify, abort


crud = Blueprint('crud', __name__)


@crud.route("/API/locations", methods=['GET'])
def api_list_locations():
    locations, next_page_token = get_model().list(limit=None, cursor=None)
    return jsonify(locations)

@crud.route("/API/<location_id>/routes", methods=['GET'])
def api_list_routes(location_id):
    location = get_model().read(location_id)
    try:
        route_ids = location["route"].split(",")
    except KeyError:
        route_ids = []
    if len(route_ids) > 0:
        routes = get_model().list_routes_API(route_ids)
    else:
        routes = []

    return jsonify(routes)


@crud.route('/API/addlocation', methods=['POST'])
def api_add_location():
    if not request.get_json(force=True):
        print("No data")
        abort(400)
    elif 'name' not in request.json:
        print("nope")
        abort(400)

    new_location = request.get_json(force=True)

    # it is an add.
    get_model().create(new_location)
    print(request.json['name'])
    return jsonify(new_location), 201

@crud.route('/API/<location_id>/addroute', methods=['POST'])
def api_add_route(location_id):
    if not request.get_json(force=True):
        print("No data")
        abort(400)
    elif 'name' not in request.json:
        print("nope")
        abort(400)

    location = get_model().read(location_id)

    data = request.get_json(force=True)
    route = get_model().create_route(data)
    if route is None:
        print(data)
    try:
        location["route"] = str(location["route"]) + "," + str(route["id"])
    except KeyError:
        location["route"] = str(route["id"])
    location = get_model().update(location, location_id)
    return jsonify(route), 201
    #return redirect(url_for('.view_route', route_id=route['id'], location_id=location['id']))

@crud.route('/API/<location_id>', methods=['PUT'])
def api_edit_location(location_id):
    if not request.get_json(force=True):
        abort(400)
    elif 'name' not in request.json:
        abort(400)

    #if there is an id then we are doing an update
    location = get_model().read(location_id)
    route_string = location["route"]

    data = request.get_json(force=True)
    data["route"] = route_string
    location = get_model().update(data, location_id)
    return jsonify(location), 201

@crud.route('/API/<location_id>/<route_id>', methods=['PUT'])
def api_edit_route(location_id, route_id):
    if not request.get_json(force=True):
        abort(400)
    elif 'name' not in request.json:
        abort(400)

    data = request.get_json(force=True)
    #data["route"] = route_string
    route = get_model().update_route(data, route_id)
    return jsonify(route), 201


@crud.route('/API/delete', methods=['DELETE'])
def api_delete_location():
    if not request.get_json(force=True):
        abort(400)

    data = request.get_json(force=True)
    location = get_model().delete(data["id"])
    return jsonify(None), 201

@crud.route('/API/<location_id>/delete', methods=['DELETE'])
def api_delete_route(location_id):
    if not request.get_json(force=True):
        abort(400)

    data = request.get_json(force=True)
    location = get_model().delete_route(location_id, data["id"])
    return jsonify(location), 201

# [START list]
@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    books, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        locations=books,
        next_page_token=next_page_token)
# [END list]

@crud.route('/<location_id>/<route_id>')
def view_route(location_id, route_id):
    location = get_model().read(location_id)
    route = get_model().read_route(route_id)

    return render_template(
        "viewRoute.html",
        route=route,
        location=location)

@crud.route('/<id>')
def view(id):
    location = get_model().read(id)
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    route_ids  = location["route"].split(",")
    routes, next_page_token = get_model().list_routes(route_ids, cursor=token)
    return render_template("view.html", location=location, routes=routes, next_page_token=next_page_token)


# [START add]
@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        book = get_model().create(data)

        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Add", location={})
# [END add]

@crud.route('/<id>/add', methods=['GET', 'POST'])
def add_rout(id):
    location = get_model().read(id)
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        route = get_model().create_route(data)
        try:
            location["route"] = str(location["route"]) + "," + str(route["id"])
        except Exception:
            location["route"] = str(route["id"])
        location = get_model().update(location, id)
        return redirect(url_for('.view_route', route_id=route['id'], location_id=location['id']))

    return render_template("routeForm.html", action="Add", location=location, route={})

@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    book = get_model().read(id)
    route_string = book["route"]

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        data["route"] = route_string
        book = get_model().update(data, id)

        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Edit", location=book)

@crud.route('/<id>/<route_id>/edit', methods=['GET', 'POST'])
def edit_route(id, route_id):
    location = get_model().read(id)
    route = get_model().read_route(route_id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        route = get_model().update_route(data, id)

        return redirect(url_for('.view_route', route_id=route['id'], location_id=location['id']))

    return render_template("routeForm.html", action="Edit", route=route, location=location)


@crud.route('/<id>/delete')
def delete(id):
    location = get_model().read(id)
    routes = location["route"].split(",")
    for route in routes:
        delete_route(id, route)
    get_model().delete(id)
    return redirect(url_for('.list'))

@crud.route('/<id>/<route_id>/delete')
def delete_route(id, route_id):
    get_model().delete_route(route_id)
    return redirect(url_for('.view', id=id))
