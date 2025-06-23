from models.classroom.classroom import Classroom

def isValidClass(class_name):
    return Classroom.query.filter_by(class_name=class_name).first()