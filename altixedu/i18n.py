"""
Internationalization (i18n) Support for Multi-language API Responses
"""

from django.utils import translation
from rest_framework.request import Request


# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish (Español)',
    'fr': 'French (Français)',
    'sw': 'Swahili',
    'pt': 'Portuguese',
}

# Translation strings
TRANSLATIONS = {
    'error_invalid_credentials': {
        'en': 'Invalid username or password',
        'es': 'Nombre de usuario o contraseña inválidos',
        'fr': 'Nom d\'utilisateur ou mot de passe invalide',
        'sw': 'Jina la mtumiaji au neno la siri batili',
        'pt': 'Nome de usuário ou senha inválido',
    },
    'error_unauthorized': {
        'en': 'You do not have permission to access this resource',
        'es': 'No tiene permiso para acceder a este recurso',
        'fr': 'Vous n\'avez pas la permission d\'accéder à cette ressource',
        'sw': 'Huna ruhusa ya kupata rasilimali hii',
        'pt': 'Você não tem permissão para acessar este recurso',
    },
    'error_not_found': {
        'en': 'Resource not found',
        'es': 'Recurso no encontrado',
        'fr': 'Ressource non trouvée',
        'sw': 'Rasilimali haijagundulika',
        'pt': 'Recurso não encontrado',
    },
    'success_login': {
        'en': 'Login successful',
        'es': 'Inicio de sesión exitoso',
        'fr': 'Connexion réussie',
        'sw': 'Kuingia kwa mwanzo kumefaulu',
        'pt': 'Login bem-sucedido',
    },
    'success_logout': {
        'en': 'Logout successful',
        'es': 'Cierre de sesión exitoso',
        'fr': 'Déconnexion réussie',
        'sw': 'Kuondoka kwa mwanzo kumefaulu',
        'pt': 'Logout bem-sucedido',
    },
    'success_created': {
        'en': 'Resource created successfully',
        'es': 'Recurso creado exitosamente',
        'fr': 'Ressource créée avec succès',
        'sw': 'Rasilimali imeundwa kwa mwanzo',
        'pt': 'Recurso criado com sucesso',
    },
    'success_updated': {
        'en': 'Resource updated successfully',
        'es': 'Recurso actualizado exitosamente',
        'fr': 'Ressource mise à jour avec succès',
        'sw': 'Rasilimali imesasishwa kwa mwanzo',
        'pt': 'Recurso atualizado com sucesso',
    },
    'success_deleted': {
        'en': 'Resource deleted successfully',
        'es': 'Recurso eliminado exitosamente',
        'fr': 'Ressource supprimée avec succès',
        'sw': 'Rasilimali imefutwa kwa mwanzo',
        'pt': 'Recurso deletado com sucesso',
    },
    'error_rate_limit': {
        'en': 'Too many requests. Please try again later.',
        'es': 'Demasiadas solicitudes. Por favor, inténtelo más tarde.',
        'fr': 'Trop de demandes. Veuillez réessayer plus tard.',
        'sw': 'Mabaki mengi sana. Tafadhali jaribu tena baadaye.',
        'pt': 'Muitas solicitações. Por favor, tente novamente mais tarde.',
    },
    'error_invalid_role': {
        'en': 'Invalid user role',
        'es': 'Rol de usuario inválido',
        'fr': 'Rôle d\'utilisateur invalide',
        'sw': 'Jukumu batili',
        'pt': 'Função de usuário inválida',
    },
}


def get_language_from_request(request):
    """
    Get preferred language from request.
    Priority:
    1. Accept-Language header
    2. User profile language preference
    3. Default to English
    """
    # Check Accept-Language header
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if accept_language:
        # Extract first preferred language
        lang_code = accept_language.split(',')[0].split('-')[0].lower()
        if lang_code in SUPPORTED_LANGUAGES:
            return lang_code
    
    # Check user profile (if authenticated)
    if request.user and request.user.is_authenticated:
        if hasattr(request.user, 'language_preference'):
            return request.user.language_preference
    
    # Default to English
    return 'en'


def translate(key, language='en', **kwargs):
    """
    Translate a string key to the specified language.
    
    Args:
        key: Translation key (e.g., 'error_invalid_credentials')
        language: Language code (default: 'en')
        **kwargs: Format string parameters
    
    Returns:
        Translated string
    """
    if key not in TRANSLATIONS:
        return key
    
    translation_dict = TRANSLATIONS[key]
    message = translation_dict.get(language, translation_dict.get('en', key))
    
    # Format if kwargs provided
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return message


def translate_request(key, request, **kwargs):
    """
    Translate using language from request.
    
    Args:
        key: Translation key
        request: Django request object
        **kwargs: Format string parameters
    
    Returns:
        Translated string
    """
    language = get_language_from_request(request)
    return translate(key, language, **kwargs)


class I18nMiddleware:
    """
    Middleware to handle internationalization.
    Sets Django's translation language based on request.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get preferred language
        language = get_language_from_request(request)
        
        # Activate translation
        translation.activate(language)
        request.language = language
        
        response = self.get_response(request)
        
        # Set language header in response
        response['Content-Language'] = language
        
        return response


def get_supported_languages():
    """Return list of supported languages"""
    return [
        {'code': code, 'name': name}
        for code, name in SUPPORTED_LANGUAGES.items()
    ]
