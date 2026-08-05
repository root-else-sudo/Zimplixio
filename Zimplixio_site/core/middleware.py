from django.conf import settings


class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
            f"img-src 'self' data:{self._media_source()}; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "frame-src https:; "
            "frame-ancestors 'none';"
        )
        return response

    @staticmethod
    def _media_source():
        # Media is served from Cloudflare R2 in production, where AWS_S3_CUSTOM_DOMAIN is set
        # from R2_PUBLIC_DOMAIN. Unset in dev, where media is served locally from MEDIA_URL.
        # Tolerates the value being configured with or without a scheme.
        domain = (getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', '') or '').strip()
        if not domain:
            return ''
        return f" https://{domain.split('://', 1)[-1].rstrip('/')}"
