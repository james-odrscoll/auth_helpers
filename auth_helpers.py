
from gluon.html import URL
from gluon import redirect

try:
    react_loader_name = 'applications.{app_name}.modules.react_loader.react_loader'.format(app_name="welcome")
    react_loader = __import__(react_loader_name, globals(), locals(), ['*'])
except Exception, import_error:
    raise import_error


def user_function(request, session, auth, use_usernames, recaptcha_site_key):

    if 'cas' in request.args:
        if not request.ajax:
            if request.args == ['cas', 'login']:
                _form = auth()
                auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})
                auth_form.requires_login = True
                auth_form.formname = 'login'

                if request.vars._next:
                    auth_form.next = request.vars._next

                if request.vars.service:
                    auth_form.next = request.vars.service

                return dict(
                    url=URL(request.application, 'default', 'user', args=['cas']),
                    auth_form=auth_form,
                    react_app_data=dict(
                    )
                )

        return auth()
    elif request.ajax:
        if request.args(0) == 'profile':
            if request.post_vars:

                if session.profile_request:
                    record_id = session.profile_request[request.post_vars.id]
                else:
                    record_id = None
                    redirect(auth.settings.login_url)

                request.post_vars.update(id=record_id)

                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    assert e.message == '200 OK'
                    assert e.status == 200

                    auth_form = None

                if not auth_form:
                    new_user = dict(**{
                        'first_name': auth.user.first_name,
                        'last_name': auth.user.last_name,
                        'email': auth.user.email,
                        'username': auth.user.username,
                    })

                    return react_loader.dump_json(dict(
                        user=new_user,
                        next='/'.join(auth.settings.login_url.split('/')[:-1]) + '/logout',
                        errors=dict(),
                    ))
                else:
                    return react_loader.dump_json(dict(
                        errors=dict(auth_form.form.errors),
                        vars=dict(auth_form.form.latest),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                form = auth()
                auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})

                record_id = auth_form.form.record_id

                # need to pass id for the update
                profile_vars = auth_form.form.latest

                import string
                import random

                # create a random string
                # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
                session_key = ''.join(
                    random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

                session.profile_request = dict({session_key: record_id, })

                profile_vars.update(id=session_key)

                return react_loader.dump_json(dict(
                    errors=dict(),
                    vars=dict(profile_vars),
                    formkey=auth_form.formkey,
                    formname=auth_form.formname
                ))
        elif request.args(0) == 'login':
            if request.post_vars:
                try:
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form,  'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    assert e.message == '200 OK'
                    assert e.status == 200
                    auth_form = None

                if not auth_form:
                    if auth.user:
                        return react_loader.dump_json(dict(
                            user=dict(**{
                                'first_name': auth.user.first_name,
                                'last_name': auth.user.last_name,
                                'email': auth.user.email,
                                'username': auth.user.username,
                            }),
                            errors=dict(),
                        ))
                    else:
                        form = auth()
                        auth_form = react_loader.W2PUserReactForm(**{'form': form,  'recaptcha_site_key': recaptcha_site_key})
                        if auth_form.errors.keys().__len__() == 0:
                            if use_usernames:
                                auth_form.errors['username'] = 'Login Failed'
                            else:
                                auth_form.errors['email'] = 'Login Failed'
                            auth_form.errors['password'] = 'Login Failed'
                        return react_loader.dump_json(dict(
                            errors=auth_form.errors,
                            vars=auth_form.vars,
                            formkey=auth_form.formkey,
                            formname=auth_form.formname
                        ))
                else:
                    return react_loader.dump_json(dict(
                        errors=auth_form.errors,
                        vars=auth_form.vars,
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                auth_form = react_loader.W2PUserReactForm(**{'form': auth(), 'recaptcha_site_key': recaptcha_site_key})

                return react_loader.dump_json(dict(
                    errors=dict(),
                    vars=dict(),
                    formkey=auth_form.formkey,
                    formname=auth_form.formname
                ))
        elif request.args(0) == 'change_password':
            if request.post_vars:
                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    assert e.message == '200 OK'
                    assert e.status == 200

                    auth_form = None

                if not auth_form:
                    return react_loader.dump_json(dict(
                        errors=dict(),
                    ))
                else:
                    return react_loader.dump_json(dict(
                        vars=dict(),
                        errors=dict(auth_form.form.errors),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                form = auth()
                auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                return react_loader.dump_json(dict(
                    errors=dict(),
                    formkey=auth_form.formkey,
                    formname=auth_form.formname
                ))
        elif request.args(0) == 'register':
            if request.post_vars:

                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    assert e.message == '200 OK'
                    assert e.status == 200

                    auth_form = None

                if not auth_form:
                    if auth.settings.registration_requires_verification:
                        return react_loader.dump_json(dict(
                            errors=dict(),
                        ))
                    else:
                        new_user = dict(**{
                            'first_name': auth.user.first_name,
                            'last_name': auth.user.last_name,
                            'email': auth.user.email,
                        })
                        return react_loader.dump_json(dict(
                            user=new_user,
                            errors=dict(),
                        ))
                else:
                    return react_loader.dump_json(dict(
                        errors=dict(auth_form.form.errors),
                        vars=dict(auth_form.form.latest),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                form = auth()
                auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})

                return react_loader.dump_json(dict(
                    errors=dict(),
                    vars=dict(auth_form.form.latest),
                    formkey=auth_form.formkey,
                    formname=auth_form.formname
                ))
        elif request.args(0) == 'retrieve_password':
            if request.post_vars:

                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    assert e.message == '200 OK'
                    assert e.status == 200

                    auth_form = None

                if not auth_form:
                    return react_loader.dump_json(dict(
                        errors=dict(),
                    ))
                else:
                    return react_loader.dump_json(dict(
                        errors=dict(auth_form.form.errors),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                form = auth()
                auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})

                return react_loader.dump_json(dict(
                    errors=dict(),
                    vars=dict(auth_form.form.latest),
                    formkey=auth_form.formkey,
                    formname=auth_form.formname
                ))
        elif request.args(0) == 'reset_password':
            # do not copy this version
            # different setup
            if request.post_vars:
                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    auth_form = None

                    if e.message == '200 OK':
                        assert e.message == '200 OK'
                        assert e.status == 200

                    elif e.message == '303 SEE OTHER':
                        assert e.message == '303 SEE OTHER'
                        assert e.status == 303
                        return react_loader.dump_json(dict(
                            vars=dict(),
                            errors=dict(),
                        ))

                if not auth_form:
                    return react_loader.dump_json(dict(
                        errors=dict(),
                        next='{url_scheme}://{host}{next}'.format(
                            url_scheme=request.env.wsgi_url_scheme,
                            host=request.env.http_host,
                            next=auth.settings.reset_password_next
                        ),
                    ))
                else:
                    return react_loader.dump_json(dict(
                        errors=dict(auth_form.form.errors),
                        vars=dict(),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    assert e.message == '200 OK'
                    assert e.status == 200
                    auth_form = None

                if not auth_form:
                    return react_loader.dump_json(dict(
                        errors=dict(),
                        next='{url_scheme}://{host}{next}'.format(
                            url_scheme=request.env.wsgi_url_scheme,
                            host=request.env.http_host,
                            next=auth.settings.reset_password_next
                        ),
                    ))
                else:
                    return react_loader.dump_json(dict(
                        errors=dict(auth_form.form.errors),
                        vars=dict(auth_form.form.latest),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))

        _form = auth()
        auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})

        auth_form.requires_login = True

        return react_loader.dump_json(dict(
            errors=dict(),
            vars=dict(),
            formkey=auth_form.formkey,
            formname=auth_form.formname
        ))
    elif request.args(0):
        if request.args(0) == 'reset_password':
            # do not copy this version
            # different setup
            if request.post_vars:
                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    auth_form = None

                    if e.message == '200 OK':
                        assert e.message == '200 OK'
                        assert e.status == 200

                    elif e.message == '303 SEE OTHER':
                        assert e.message == '303 SEE OTHER'
                        assert e.status == 303
                        return react_loader.dump_json(dict(
                            vars=dict(),
                            errors=dict(),
                        ))

                if not auth_form:
                    return react_loader.dump_json(dict(
                        errors=dict(),
                        next='{url_scheme}://{host}{next}'.format(
                            url_scheme=request.env.wsgi_url_scheme,
                            host=request.env.http_host,
                            next=auth.settings.reset_password_next
                        ),
                    ))
                else:
                    return react_loader.dump_json(dict(
                        errors=dict(auth_form.form.errors),
                        vars=dict(),
                        formkey=auth_form.formkey,
                        formname=auth_form.formname
                    ))
            else:
                try:
                    # auth.profile() does not update db only auth.user in session
                    # similar problem ...
                    # https://stackoverflow.com/questions/13059557/web2py-auth-user-object-returns-obsolete-data
                    form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': form, 'recaptcha_site_key': recaptcha_site_key})
                    # on successful form submission either with a login fail or otherwise, a redirect occurs
                    # this Exception is actually a HTTP event
                except Exception, e:
                    auth_form = None

                    if e.message == '200 OK':
                        assert e.message == '200 OK'
                        assert e.status == 200
                    elif e.message == '303 SEE OTHER':
                        assert e.message == '303 SEE OTHER'
                        assert e.status == 303
                        raise e

                if not auth_form:
                    return react_loader.dump_json(dict(
                        errors=dict(),
                        next='{url_scheme}://{host}{next}'.format(
                            url_scheme=request.env.wsgi_url_scheme,
                            host=request.env.http_host,
                            next=auth.settings.reset_password_next
                        ),
                    ))
                else:
                    auth_form.requires_login = True
                    return dict(
                        url=URL(request.application, 'default', 'user'),
                        auth_form=auth_form,
                        react_app_data=dict(
                        )
                    )
        elif request.args(0) == 'login':
            _form = auth()

            auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})
            auth_form.requires_login = False if auth.user else True
            auth_form.formname = "login"

            if request.vars._next:
                auth_form.next = request.vars._next

            if request.vars.service:
                auth_form.next = request.vars.service

            return dict(
                url=URL(request.application, 'default', 'user'),
                auth_form=auth_form,
                react_app_data=dict(
                )
            )

    _form = auth()

    auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})
    auth_form.requires_login = True
    auth_form.formname = "login"

    if request.vars._next:
        auth_form.next = request.vars._next

    if request.vars.service:
        auth_form.next = request.vars.service

    return dict(
        url=URL(request.application, 'default', 'user'),
        auth_form=auth_form,
        react_app_data=dict(
        )
    )


def auth_controller_helper(**kwargs):
    unpack_keys = ('request', 'session', 'auth', 'is_this_cas_provider_app', 'use_cas_provider', 'react_loader', 'recaptcha_site_key')
    request, session, auth, is_this_cas_provider_app, use_cas_provider, react_loader, recaptcha_site_key = [kwargs[k] for k in unpack_keys]

    if use_cas_provider == "no":
        _form = auth()
        auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})
    else:
        if is_this_cas_provider_app:
            try:
                _form = auth()
            except Exception, e:
                raise e
            auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})
        else:
            # using cas from another app
            if not session.token:
                if request.args.__len__() == 0:
                    auth_form = react_loader.W2PUserReactForm(**{'recaptcha_site_key': recaptcha_site_key})
                    auth_form.formname = 'login'

                    return auth_form
                else:
                    _form = auth()
                    auth_form = react_loader.W2PUserReactForm(**{'form': _form, 'recaptcha_site_key': recaptcha_site_key})
            else:
                auth_form = react_loader.W2PUserReactForm(**{'recaptcha_site_key': recaptcha_site_key})
                auth_form.formname = 'login'
                auth_form.vars = dict(**session.token)
                auth_form.vars.pop('id')

    if request.args(0):
        if request.args(0) == 'login':
            auth_form.requires_login = True
        elif request.args(0) == 'cas':
            auth_form.requires_login = True

        auth_form.formname = 'login'

        if request.vars._next:
            auth_form.next = request.vars._next

        if request.vars.service:
            auth_form.next = request.vars.service

    if request.args(0):
        if request.args(0) == 'reset_password':
            auth_form.requires_login = True
            auth_form.formname = 'reset_password'

    return auth_form

