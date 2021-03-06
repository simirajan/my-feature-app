from flask import Flask, render_template, request, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

application = Flask(__name__)
application.config.from_object('config')
db = SQLAlchemy(application)

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    client = db.Column(db.String(5), nullable=False)
    product_area = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Feature %r>' % self.title

@application.route("/")
def main():
    features = Feature.query.order_by('-id').all()
    return render_template('listFeatures.html', features=features)

@application.route('/createRequest', methods=['GET', 'POST'])
def createRequest():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        client = request.form['client']
        priority = int(request.form['priority'])
        target = datetime.strptime(request.form['target'], '%Y-%m-%d')
        #target=request.form['target']
        #print(target)
        area = request.form['area']
     
        # validate the received values
        if title:
            new_feature  = Feature(
                title=title,
                description=description,
                priority=priority,
                target_date=target,
                client=client,
                product_area=area
            )
            db.session.add(new_feature)

            # Feature for a specific client cannot have the same priority so re-order features' priorities if a new one
            # with the same priority is added
            priority_to_update = priority
            features_to_update_count = Feature.query.filter_by(client=client, priority=priority_to_update).count()
            while features_to_update_count > 1:
                feature_to_update = Feature.query.filter_by(client=client, priority=priority_to_update).order_by('id').first()
                feature_to_update.priority = feature_to_update.priority + 1
                priority_to_update = priority_to_update + 1
                features_to_update_count = Feature.query.filter_by(client=client, priority=priority_to_update).count()

            db.session.commit()
            
            return json.dumps({'html':'<span>All good</span>'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})
    elif request.method == 'GET':
        return render_template('createRequest.html')

@application.route('/delete/<int:feature_id>', methods=['GET', 'DELETE'])
def deleteFeature(feature_id):
    if request.method == 'DELETE':
        if feature_id:
            feature_to_delete = Feature.query.get(feature_id)
            db.session.delete(feature_to_delete)
            db.session.commit()
            return json.dumps({'html':'<span>All good</span>'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

if __name__ == "__main__":
    #application.debug = True
    application.run()