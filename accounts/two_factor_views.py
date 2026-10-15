import base64
from io import BytesIO

import qrcode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from django_otp import login as otp_login
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice


PRE_2FA_TIMEOUT_SECONDS = 300


def _create_recovery_codes(user):
    """
    Replace existing recovery codes with eight new single-use codes.
    """

    recovery_device, _ = StaticDevice.objects.get_or_create(
        user=user,
        name='Deep Ink Recovery Codes',
    )

    recovery_device.token_set.all().delete()

    recovery_codes = [
        StaticToken.random_token()
        for _ in range(8)
    ]

    StaticToken.objects.bulk_create([
        StaticToken(
            device=recovery_device,
            token=code,
        )
        for code in recovery_codes
    ])

    return recovery_codes


def _get_pending_user(request):
    """
    Return the user who successfully passed the password step.

    The temporary authentication session expires after five minutes.
    """

    user_id = request.session.get('pre_2fa_user_id')
    started_at = request.session.get('pre_2fa_started_at')

    if not user_id or not started_at:
        return None

    try:
        elapsed = timezone.now().timestamp() - float(started_at)
    except (TypeError, ValueError):
        return None

    if elapsed > PRE_2FA_TIMEOUT_SECONDS:
        _clear_pending_login(request)
        return None

    try:
        return User.objects.get(
            id=user_id,
            is_active=True,
        )
    except User.DoesNotExist:
        _clear_pending_login(request)
        return None


def _clear_pending_login(request):
    """
    Remove temporary password-authentication information.
    """

    request.session.pop('pre_2fa_user_id', None)
    request.session.pop('pre_2fa_started_at', None)
    request.session.pop('pre_2fa_remember_me', None)
    request.session.pop('pre_2fa_next', None)
    request.session.pop('new_recovery_codes', None)


def _complete_login(request, user, otp_device):
    """
    Complete authentication after a valid OTP or recovery code.
    """

    authentication_backends = getattr(
        settings,
        'AUTHENTICATION_BACKENDS',
        ['django.contrib.auth.backends.ModelBackend'],
    )

    remember_me = request.session.get('pre_2fa_remember_me')
    next_url = request.session.get('pre_2fa_next')

    if not next_url or not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = '/dashboard/'

    login(
        request,
        user,
        backend=authentication_backends[0],
    )

    # Mark the session as officially verified by django-otp.
    otp_login(request, otp_device)

    if remember_me:
        request.session.set_expiry(60 * 60 * 24 * 14)
    else:
        request.session.set_expiry(0)

    _clear_pending_login(request)

    return redirect(next_url)


def two_factor_setup(request):
    """
    Allow a staff member to register an authenticator application.
    """

    user = _get_pending_user(request)

    if user is None:
        messages.error(
            request,
            'Your login session expired. Please sign in again.',
        )
        return redirect('login')

    confirmed_device = TOTPDevice.objects.filter(
        user=user,
        confirmed=True,
    ).first()

    if confirmed_device:
        return redirect('two_factor_verify')

    device = TOTPDevice.objects.filter(
        user=user,
        confirmed=False,
    ).first()

    if device is None:
        device = TOTPDevice.objects.create(
            user=user,
            name='Deep Ink Authenticator',
            confirmed=False,
        )

    if request.method == 'POST':
        token = request.POST.get(
            'token',
            '',
        ).replace(' ', '')

        if device.verify_token(token):
            device.confirmed = True
            device.save(
                update_fields=['confirmed'],
            )

            recovery_codes = _create_recovery_codes(user)

            request.session['new_recovery_codes'] = recovery_codes

            return redirect('two_factor_recovery_codes')

        messages.error(
            request,
            'The authentication code is incorrect. Please try again.',
        )

    qr_image = qrcode.make(device.config_url)
    image_buffer = BytesIO()

    qr_image.save(
        image_buffer,
        format='PNG',
    )

    qr_code = base64.b64encode(
        image_buffer.getvalue()
    ).decode('utf-8')

    secret_key = base64.b32encode(
        device.bin_key
    ).decode('utf-8').rstrip('=')

    return render(
        request,
        'accounts/two_factor_setup.html',
        {
            'qr_code': qr_code,
            'secret_key': secret_key,
        },
    )


def two_factor_recovery_codes(request):
    """
    Display newly generated recovery codes once during 2FA setup.
    """

    user = _get_pending_user(request)

    if user is None:
        messages.error(
            request,
            'Your login session expired. Please sign in again.',
        )
        return redirect('login')

    recovery_codes = request.session.get('new_recovery_codes')

    if not recovery_codes:
        return redirect('two_factor_verify')

    confirmed_device = TOTPDevice.objects.filter(
        user=user,
        confirmed=True,
    ).first()

    if confirmed_device is None:
        return redirect('two_factor_setup')

    if request.method == 'POST':
        messages.success(
            request,
            'Two-factor authentication has been enabled successfully.',
        )

        return _complete_login(
            request,
            user,
            confirmed_device,
        )

    return render(
        request,
        'accounts/two_factor_recovery_codes.html',
        {
            'recovery_codes': recovery_codes,
        },
    )


def two_factor_verify(request):
    """
    Verify an authenticator code or a single-use recovery code.
    """

    user = _get_pending_user(request)

    if user is None:
        messages.error(
            request,
            'Your login session expired. Please sign in again.',
        )
        return redirect('login')

    device = TOTPDevice.objects.filter(
        user=user,
        confirmed=True,
    ).first()

    if device is None:
        return redirect('two_factor_setup')

    if request.method == 'POST':
        token = request.POST.get(
            'token',
            '',
        ).replace(' ', '').lower()

        verified_device = None

        if token.isdigit() and len(token) == 6:
            if device.verify_token(token):
                verified_device = device

        else:
            recovery_device = StaticDevice.objects.filter(
                user=user,
                name='Deep Ink Recovery Codes',
            ).first()

            if (
                recovery_device
                and recovery_device.verify_token(token)
            ):
                verified_device = recovery_device

        if verified_device:
            return _complete_login(
                request,
                user,
                verified_device,
            )

        messages.error(
            request,
            'The authentication or recovery code is incorrect or has expired.',
        )

    recovery_codes_remaining = StaticToken.objects.filter(
        device__user=user,
        device__name='Deep Ink Recovery Codes',
    ).count()

    return render(
        request,
        'accounts/two_factor_verify.html',
        {
            'pending_user': user,
            'recovery_codes_remaining': recovery_codes_remaining,
        },
    )