# vim: set ts=4 sts=4 sw=4 expandtab:
from flask import request, jsonify
from api import app, db, make_json_error, support_jsonp
from api.meta import require_client_id
from api.scripts.laundry import Room

'''
DATABASE OBJECTS: View templates on the private repository README.
'''

# simplify database names
ldb = db.laundry


@app.route('/laundry')
@support_jsonp
@require_client_id()
def laundry_index():
    return make_json_error('No method specified. '
                           'See documentation for endpoints.')


@app.route('/laundry/rooms')
@support_jsonp
@require_client_id()
def req_laundry_room_list():
    results = ldb.find({}, {'_id': False, 'machines': False})
    result_list = [r for r in results]
    return jsonify(num_result=len(result_list), results=result_list)


@app.route('/laundry/rooms/<room_id>')
@support_jsonp
@require_client_id()
def req_room_detail(room_id):
    room = ldb.find_one({'id': str(room_id)}, {'_id': False})
    if room is None:
        return make_json_error('Room not found')
    return jsonify(result=room)


@app.route('/laundry/rooms/<room_id>/machines')
@support_jsonp
@require_client_id()
def req_machines(room_id):
    # TODO make a type field to filter on (washer, dryer, etc)

    room = ldb.find_one({'id': str(room_id)},
                        {'_id': False, 'id': True, 'machines': True})
    if room is None:
        return make_json_error('Room not found')

    # support a get_status parameter to optionally get machine statuses
    if bool(request.args.get('get_status')):
        room = Room.get_machine_statuses(room)

    del room['id']
    return jsonify(results=room['machines'])


@app.route('/laundry/rooms/<room_id>/machines/<machine_id>')
@support_jsonp
@require_client_id()
def req_machine_details(room_id, machine_id):
    # get_statuses = request.args.get('get_statuses')

    room = ldb.find_one({'id': str(room_id), 'machines.id': str(machine_id)},
                        {'_id': False, 'machines': True, 'id': True})
    if room is None:
        return make_json_error("Machine or room not found")

    print(room)

    # support a get_status parameter to optionally get machine status
    if bool(request.args.get('get_status')):
        room = Room.get_machine_statuses(room)

    m = list(filter(lambda x: x['id'] == str(machine_id), room['machines']))
    if len(m) == 0:
        return make_json_error("Machine not found")

    return jsonify(result=m[0])
