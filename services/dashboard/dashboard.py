import os
import re
import datetime
import traceback
import numpy
import math
import json
import traceback
import ConfigParser
import datetime

from operator import itemgetter

from business.utils.twilioutils import TwilioUtils

# flask imports
from flask import Flask
from flask import request, abort
from flask import Response
from flask import Blueprint

# json handling
import jsonpickle
from bson.json_util import dumps
from bson.objectid import ObjectId

from dto.response.classes.base import Base
from dto.response.classes.object import Object
from dto.response.utils.baseutils import BaseUtils
from dto.response.classes.preference import Preference

from persistence.mongodatabase import mongoDatabase

from business.implementations.implementations import Implementations

from persistence.collections.users import Users
from persistence.collections.preferences import Preferences
from persistence.collections.listingowners import ListingOwners
from persistence.collections.messages import Messages


# load constants
# MONGO_URL = 'mongodb://jhon:1234@dogen.mongohq.com:10080/app31803464'
# MONGO_DB = "app31803464"
# MONGO_URL = "mongodb://jhon:1234@kahana.mongohq.com:10066/app30172457"
# MONGO_DB = "app30172457"

# TODO: improve the way this vars are loaded
# load constants
config = ConfigParser.ConfigParser()
config.read("config.cfg")
mongo_section = 'mongo_config'
MONGO_URL = config.get(mongo_section, 'url')
MONGO_DB = config.get(mongo_section, 'db')

# init db connection
myDB = mongoDatabase(MONGO_URL)
db = myDB.getDB(MONGO_DB)

dashboard_api = Blueprint('dashboard_api', __name__)

@dashboard_api.route('/test', methods=['POST'])
def create_test_data():
    try:
        test_instance = Implementations()
        test_instance.load_all_database_test_data()
        return Response()

    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/users/test', methods=['POST'])
def create_test_users():
    try:
        test_instance = Implementations()
        test_instance.load_users_test_data()
        return Response()

    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/listingowners/test', methods=['POST'])
def create_test_listing_owners():
    try:
        ## get calibration value
        test_instance = Implementations()
        test_instance.load_listing_owners_test_data()
        return Response()

    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/messages/test', methods=['POST'])
def create_test_messages():
    try:
        test_instance = Implementations()
        test_instance.load_messages_test_data()
        return Response()

    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/notifications/test', methods=['POST'])
def create_test_notifications():
    try:
        notifications_instance = Implementations()
        notifications_instance.load_notifications_test_data()
        return Response()

    except Exception as e:
        print "There was an unexpected error: " , str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/notifications/user/<user_id>', methods=['GET'])
def get_unread_notifications(user_id = None):
    try:
        if user_id is not None:
            ## get calibration value
            implementations_instance = Implementations()
            notifcations_list = implementations_instance.get_unread_notifications(user_id)
            json_obj = jsonpickle.encode(notifcations_list, unpicklable=False)
            return Response(json_obj)
        else:
            abort(500)
    except Exception as e:
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/mandrillreplies', methods=['POST']) #Here i will make some changes tetete ksks sdsad
def save_received_user_mandrill_email():
    """
    print "save_received_user_mandrill_email"
    return Response()
    """
    try:
        mandrill_events = request.form.get('mandrill_events')
        mandrill_message = jsonpickle.decode(mandrill_events)[0]['msg']
        mandrill_message_text = mandrill_message['text']
        mandrill_message_from_email = mandrill_message['from_email']

        #print "mandrill_message_text"
        #print mandrill_message_text
        #print "mandrill_message_from_email"
        #print mandrill_message_from_email

        separator_string = "## Please do not write below this line ##"
        conversation_separator_string = "CONVERSATION_ID###"

        mandrill_message_reply_list = mandrill_message_text.split(separator_string)
        mandrill_message_reply_text = mandrill_message_reply_list[0]
        text_for_conversation = mandrill_message_reply_list[1]
        conversation_split_list = text_for_conversation.split(conversation_separator_string)
        conversation_id_string = conversation_split_list[1]

        print "mandrill_message_reply_text"
        print mandrill_message_reply_text
        print "conversation_id_string"
        print conversation_id_string

        if (mandrill_message_reply_text is not None) and (mandrill_message_from_email is not None)and (conversation_id_string is not None):
            implementations_instance = Implementations()
            implementations_instance.save_received_user_mandrill_email(mandrill_message_reply_text, mandrill_message_from_email, conversation_id_string )
            return Response()
        else:
            abort(500)
        return Response()
    except Exception as e:
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()
        abort(500)


@dashboard_api.route('/twiliomessages', methods=['POST'])
def save_received_realtor_twilio_messages():
    try:
        print "save_received_realtor_twilio_messages"
        request_form_sid = request.form.get('MessageSid') # Twilio's unique identifier of the message
        request_form_from = request.form.get('From')      # number that sent us the sms
        request_form_to = request.form.get('To')          # Twilio number we used to receive the sms
        request_form_body = request.form.get('Body')      # Content of the sms

        if (request_form_sid is not None) and (request_form_from is not None) and (request_form_to is not None) and (request_form_body is not None):
            implementations_instance = Implementations()
            implementations_instance.save_realtor_twilio_message(request_form_sid, request_form_from, request_form_to, request_form_body)
            json_obj = jsonpickle.encode([], unpicklable=False)
            return Response(json_obj)
        else:
            abort(500)
    except Exception as e:
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/messages/user/<user_id>', methods=['GET'])
def get_received_messages(user_id = None):
    try:
        if user_id is not None:
            ## get calibration value
            messages_collection_obj = Messages(db)
            message_list = messages_collection_obj.get_received_messages(user_id)
            print "message_list"
            print message_list
            json_obj = jsonpickle.encode(message_list, unpicklable=False)
            return Response(json_obj)
        else:
            abort(500)
    except Exception as e:
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()
        abort(500)

@dashboard_api.route('/listingowners/<listing_owner_id>', methods=['GET'])
def get_listing_owner(listing_owner_id = None):
    try:
        if listing_owner_id is not None:
            ## get calibration value
            listing_owner_collection_obj = ListingOwners(db)
            message_list = listing_owner_collection_obj.gell_listing_owner(listing_owner_id)
            #print "message_list"
            #print message_list
            json_obj = jsonpickle.encode(message_list, unpicklable=False)
            return Response(json_obj)
        else:
            abort(500)
    except Exception as e:
        print "There was an unexpected error: ", str(e)
        print traceback.format_exc()
        abort(500)