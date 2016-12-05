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

from flask import current_app
from google.cloud import datastore


builtin_list = list


def init_app(app):
    pass


def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]

#START API
def list_API(limit=10, cursor=None):
    ds = get_client()
    query = ds.query(kind='Location', order=['name'])
    it = query.fetch(start_cursor=cursor)
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    return entities, cursor.decode('utf-8') if len(entities) == limit else None

def list_routes_API(route_ids):
    routes = []

    for route_id in route_ids:
        routes.append(read_route(route_id))

    return routes

def create_user(data):
    ds = get_client()
    query = ds.query(kind="User")
    it = query.fetch()
    query.add_filter("username", "=", data["username"])
    cursor = None
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    if len(entities) == 0 or entities is None:
        key = ds.key('User')
        entity = datastore.Entity(key=key)
        entity.update(data)
        ds.put(entity)
        return from_datastore(entity)
    else:
        return None

def login(data):
    ds = get_client()
    query = ds.query(kind="User")
    it = query.fetch()
    query.add_filter("username", "=", data["username"])
    query.add_filter("password", "=", data["password"])
    cursor = None
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    if len(entities) == 0 or entities is None:
        return False
    else:
        return True

def update_user(data, id):
    ds = get_client()

    key = ds.key('User', int(id))

    entity = datastore.Entity(key=key)

    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)
#END API


# [START list]
def list(limit=10, cursor=None):
    ds = get_client()
    query = ds.query(kind='Location', order=['name'])
    it = query.fetch(limit=limit, start_cursor=cursor)
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    return entities, cursor.decode('utf-8') if len(entities) == limit else None
# [END list]

def list_routes(route_ids, limit=10, cursor=None):
    ds = get_client()
    routes = []
    query = ds.query(kind='Route')
    for route_id in route_ids:
        routes.append(read_route(route_id))
    it = query.fetch(limit=limit, start_cursor=cursor)
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    return routes, None

def read(id):
    ds = get_client()
    key = ds.key('Location', int(id))
    results = ds.get(key)
    return from_datastore(results)

def read_user(username):
    ds = get_client()
    query = ds.query(kind='User')
    query.add_filter("username", "=", username)
    it = query.fetch()
    cursor = None
    entities, more_results, cursor = it.next_page()
    entities = builtin_list(map(from_datastore, entities))
    print(entities)
    if len(entities) == 1:
        id = entities[0]
        id = id["id"]
    else:
        return None
    key = ds.key('User', int(id))
    results = ds.get(key)
    return from_datastore(results)

def read_route(id):
    ds = get_client()
    key = ds.key('Route', int(id))
    results = ds.get(key)
    return from_datastore(results)

# [START update]
def update(data, id=None):
    ds = get_client()
    if id:
        key = ds.key('Location', int(id))
    else:
        data["route"] = []
        key = ds.key('Location')

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['description'])

    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)

create = update
# [END update]


def update_route(data, id=None):
    ds = get_client()
    if id:
        key = ds.key('Route', int(id))
    else:
        key = ds.key('Route')

    entity = datastore.Entity(key=key)

    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)

create_route = update_route


def delete(id):
    ds = get_client()
    key = ds.key('Location', int(id))
    ds.delete(key)
    return None

def delete_user(id):
    ds = get_client()
    key = ds.key('User', int(id))
    ds.delete(key)
    return "true"

def delete_route(location_id, route_id):
    ds = get_client()
    location = read_user(location_id)
    key = ds.key('Route', int(route_id))
    route_ids = location["route"].split(",")
    if str(route_id) in route_ids:
        route_ids.remove(route_id)
    location["route"] = ",".join(route_ids)
    location = update_user(location, location["id"])
    ds.delete(key)
    return location
