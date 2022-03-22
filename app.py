from flask import Flask ,jsonify,request
from models import db,User,Room,Message,Participants
from flask_cors import CORS

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
CORS(app)

db.init_app(app)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://onsdzvghhzqmlg:d626aaf93e38b6f5e2bfd9436ec620a0663e402c9d153d1d3b901366067fd001@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/daelhpjvj07nd1"
# "postgresql://sqfchhvcywmegt:1e4f30c9447087c90170fe999bdbd7cdf542f57f61dbe368baaeb2e358a62329@ec2-176-34-105-15.eu-west-1.compute.amazonaws.com:5432/d3e165le2np51u"
# "sqlite:///test.db"
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Message, db.session))
admin.add_view(ModelView(Participants, db.session))

@app.route('/contacts/<string:uid>',methods=["GET"])
def get_contacts(uid):
	uid=int(uid)
	contacts=[]
	print(f"uid :{uid}")
	Rooms=Participants.query.filter_by(user_id=uid).all()
	print(Rooms)
	contacts =[[P for P in  Participants.query.filter_by(room_id=R.room_id) if P.user_id!=uid][0] for R in Rooms]
	# contacts_users=[R.user_id for R in Participants.query.filter_by(room_id=R.id,) if R.user_id!=uid]
	print(contacts)
	last_msgs=[Message.query.filter_by(user_id=R.user_id,room_id=R.room_id).order_by(Message.id.desc()).first().msg for R in contacts]
	print(last_msgs)
	output=[{
		"room_id":Rooms[i].room_id,
		"user_name":User.query.filter_by(id=contacts[i].user_id).first().email,
		"last_msg":last_msgs[i],
	} for i in range(len(Rooms))]
	return jsonify(output)
# .order_by(Message.id.desc())

@app.route('/add_message',methods=['POST'])
def add_msg():
	try:
		data = request.get_json(force=True)
		new_msg = Message(
			user_id=data['user_id'], 
			room_id=data['room_id'], 
			msg=data['msg']
		    )
		db.session.add(new_msg)
		db.session.commit()
		return jsonify({'message' : 'New message created!'})
	except Exception as e:
		return jsonify({"message":"error"})

@app.route('/add_room',methods=['POST'])
def add_room():
	# try:
	data = request.get_json(force=True)
	user_id=data['user_id']
	uid=data['uid']
	R=Room(room=f"room{user_id}-{uid}")
	db.session.add(R)
	db.session.commit()
	print(R.id)
	db.session.add(Participants(user_id=user_id,room_id=R.id))
	db.session.add(Participants(user_id=uid,room_id=R.id))
	db.session.commit()
	return jsonify({'message' : 'New Contact created!'})
	# except Exception as e:
	# 	return jsonify({"message":"error"})


if __name__ == '__main__':
	app.run(debug=True)


# web: gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
	
