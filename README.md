# Oracle APEX Python Email Service

A simple email service that integrates Oracle APEX with a Python FastAPI backend. Oracle APEX sends email details through a REST API, and the Python service processes the request and sends the email through an SMTP server.

## Overview

This demonstrates how Oracle APEX can use a Python FastAPI service to send emails.

Oracle APEX prepares the email information, including the recipient, CC, subject, and email body. The information is converted into a JSON request and sent to the Python FastAPI service through an HTTP POST request.

The Python service receives the request, validates the input, creates the email message, connects to the configured SMTP server, and sends the email to the specified recipients.


### `email_service.py`

Python FastAPI application that provides the email API endpoint.

It:

* Receives email details from Oracle APEX
* Validates the JSON request
* Creates the email message
* Connects to the SMTP server
* Sends the email to the recipients

### `apex_email_trigger.sql`

Oracle APEX PL/SQL code used to call the Python FastAPI email service.

It:

* Prepares the email body
* Creates the JSON request
* Sets the REST request headers
* Calls the FastAPI endpoint using `APEX_WEB_SERVICE.MAKE_REST_REQUEST`


## Oracle APEX Integration

Oracle APEX sends the email request to the FastAPI service using `APEX_WEB_SERVICE.MAKE_REST_REQUEST`.

Example:

```sql
V_RESULT := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
    p_url         => 'https://<YOUR-SERVER>/<EMAIL_API_ENDPOINT>',
    p_http_method => 'POST',
    p_body        => V_MAIL
);
```

The JSON request contains the recipient, CC, subject, and email body.

## Python Email Service

The FastAPI application receives the JSON request through the API endpoint.

Pydantic is used to validate the incoming request and ensure that the required fields are provided in the expected format.

The service then creates an HTML email using Python's email libraries and sends it through the configured SMTP server.

