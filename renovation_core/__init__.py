# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe.core.doctype.sms_settings.sms_settings
import frappe.model.sync
from frappe.email.doctype.notification.notification import Notification
from frappe.model.meta import Meta

from .renovation_dashboard_def.utils import clear_dashboard_cache
from .utils.notification import send_notification
from .utils.sms_setting import validate_receiver_nos
from .utils.sync import _get_doc_files, process

__version__ = '1.0.5'

Meta.process = process
frappe.model.sync.get_doc_files = _get_doc_files
frappe.core.doctype.sms_settings.sms_settings.validate_receiver_nos = validate_receiver_nos

# Notification Send fn override
# To include FCM
Notification.send = send_notification


def clear_cache():
  from .utils.meta import clear_all_meta_cache
  clear_all_meta_cache()

  from .utils.renovation import clear_cache
  clear_cache()

  clear_dashboard_cache()


def on_login(login_manager):
  import frappe.permissions

  append_user_info_to_response(login_manager.user)


def on_session_creation(login_manager):
  from .utils.auth import make_jwt
  if frappe.form_dict.get('use_jwt'):
    frappe.local.response['token'] = make_jwt(
        login_manager.user, frappe.flags.get('jwt_expire_on'))
    frappe.flags.jwt_clear_cookies = True


def append_user_info_to_response(user):
  user_details = frappe.db.get_value(
      "User", user, ["name", "full_name", "quick_login_pin", "user_image", "language"])
  frappe.local.response = frappe._dict({
      "user": user,
      "message": "Logged In",
      "home_page": "/desk",
      "user_image": user_details[3],
      "full_name": user_details[1],
      "has_quick_login_pin": user_details[2] != None,
      "lang": user_details[-1]
  })

  for method in frappe.get_hooks().get("renovation_login_response", []):
    frappe.call(frappe.get_attr(method), user=user)


@frappe.whitelist()
def get_logged_user():
  user = frappe.session.user
  append_user_info_to_response(user)


def on_logout():
  from .utils.fcm import delete_token_on_logout
  delete_token_on_logout()
