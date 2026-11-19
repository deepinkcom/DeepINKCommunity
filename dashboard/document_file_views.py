from pathlib import PurePosixPath
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe
from .decorators import dashboard_access_required
from .models import Document

PREVIEW_TYPES = {
    '.pdf': 'application/pdf', '.png': 'image/png',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.webp': 'image/webp',
}

def can_access(user):
    if not user.has_perm('dashboard.manage_documents'):
        raise PermissionDenied('Document access is not authorised.')

def serve_document(request, pk, download=False):
    can_access(request.user)
    document = get_object_or_404(Document, pk=pk)
    if not document.file:
        raise Http404('File unavailable.')
    filename = PurePosixPath(document.file.name).name
    suffix = PurePosixPath(filename).suffix.lower()
    try:
        stream = document.file.open('rb')
    except (OSError, ValueError):
        raise Http404('File unavailable.')
    if not download and suffix not in PREVIEW_TYPES:
        stream.close()
        return render(request, 'dashboard/document_preview_unavailable.html', {
            'document': document, 'role': request.staff_role,
            'active_nav': 'documents', 'page_title': 'Document Preview',
        })
    response = FileResponse(stream, as_attachment=download, filename=filename,
                            content_type='application/octet-stream' if download else PREVIEW_TYPES[suffix])
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "sandbox; default-src 'none'"
    return response

@dashboard_access_required
@require_safe
def document_preview(request, pk):
    return serve_document(request, pk)

@dashboard_access_required
@require_safe
def document_download(request, pk):
    return serve_document(request, pk, download=True)

# Prevent bypassing permission checks through Django's development media route.
def blocked_document_media(request, file_path):
    raise Http404('Use the authorised Documents page.')
