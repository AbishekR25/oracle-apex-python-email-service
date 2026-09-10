DECLARE
    V_BODY   VARCHAR2(4000);
    V_MAIL   VARCHAR2(4000);
    V_RESULT CLOB;
BEGIN

    -- Email body
    V_BODY :=
          'Hi User,<br><br>'
           This is a system generated email;

    -- JSON request body expected by Python FastAPI
    V_MAIL :=
          '{"p_to": ["' || P_TO || '"],'
       || '"p_cc": [],'
       || '"p_subj": "' || V_SUB || '",'
       || '"p_body": "' || V_BODY || '"}';

    DBMS_OUTPUT.PUT_LINE(V_MAIL);

    -- Set REST request headers
    APEX_WEB_SERVICE.SET_REQUEST_HEADERS(
        p_name_01  => 'Content-Type',
        p_value_01 => 'application/json',
        p_reset    => TRUE
    );

    -- Call Python FastAPI email service
    V_RESULT := APEX_WEB_SERVICE.MAKE_REST_REQUEST(
        p_url         => 'https://<YOUR-SERVER>/<EMAIL_API_ENDPOINT>',
        p_http_method => 'POST',
        p_body        => V_MAIL
    );

END;
/
