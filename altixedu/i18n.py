"""
Internationalization (i18n) Support for Multi-language API Responses
"""

from django.utils import translation
from rest_framework.request import Request


# Supported languages - Prioritized for African schools
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'sw': 'Swahili (Kiswahili)',  # Kenya, Tanzania, Uganda
    'ha': 'Hausa (Hausa)',  # Nigeria, Niger
    'yo': 'Yoruba',  # Nigeria
    'fr': 'French (Français)',  # West Africa (Côte d'Ivoire, Cameroon, etc.)
    'am': 'Amharic (አማርኛ)',  # Ethiopia
    'zu': 'Zulu',  # South Africa
    'es': 'Spanish (Español)',
    'pt': 'Portuguese (Português)',
}

# Translation strings - Comprehensive for African schools
TRANSLATIONS = {
    # Authentication errors
    'error_invalid_credentials': {
        'en': 'Invalid username or password',
        'es': 'Nombre de usuario o contraseña inválidos',
        'fr': 'Nom d\'utilisateur ou mot de passe invalide',
        'sw': 'Jina la mtumiaji au neno la siri batili',
        'ha': 'Sunan mai amfani ko kalmar siri bai dace',
        'yo': 'Orile eniyan tabi iyalenu alainidun',
        'am': 'ስም ወይም ይለፍ ቃል ትክክል አይደለም',
        'zu': 'Igama nomuntu noma iphasiwedi ayilungile',
        'pt': 'Nome de usuário ou senha inválido',
    },
    'error_unauthorized': {
        'en': 'You do not have permission to access this resource',
        'es': 'No tiene permiso para acceder a este recurso',
        'fr': 'Vous n\'avez pas la permission d\'accéder à cette ressource',
        'sw': 'Huna ruhusa ya kupata rasilimali hii',
        'ha': 'Ba ka da izini da ka shiga abin da ke aiki',
        'yo': 'Ò kò ní àalù láti wọ ohun ìjinlẹ̀ yìi',
        'am': 'ይህን ሀብት ለመድረስ ተገቢ ፈቃድ የለዎትም',
        'zu': 'Awukho imvume yakho ukufinyelela ingcebo elingu',
        'pt': 'Você não tem permissão para acessar este recurso',
    },
    'error_not_found': {
        'en': 'Resource not found',
        'es': 'Recurso no encontrado',
        'fr': 'Ressource non trouvée',
        'sw': 'Rasilimali haijagundulika',
        'ha': 'Ba a sami abin da kuke nema',
        'yo': 'Ohun ti o wa ko ti a rii',
        'am': 'ሀብተ ምንዛሪነት አልተገኘም',
        'zu': 'Ingcebo ethunyelwe ayikhona',
        'pt': 'Recurso não encontrado',
    },
    
    # Success messages
    'success_login': {
        'en': 'Login successful',
        'es': 'Inicio de sesión exitoso',
        'fr': 'Connexion réussie',
        'sw': 'Kuingia kumefaulu',
        'ha': 'Shiga yampe',
        'yo': 'Wiwọlọ le jade si ẹbẹ',
        'am': 'መግቢያ ተስኖአል',
        'zu': 'Ukungenisa kulwelile',
        'pt': 'Login bem-sucedido',
    },
    'success_logout': {
        'en': 'Logout successful',
        'es': 'Cierre de sesión exitoso',
        'fr': 'Déconnexion réussie',
        'sw': 'Kuondoka kumefaulu',
        'ha': 'Fita yampe',
        'yo': 'Ìjẹ́ kúrò dá tẹ̀lẹ̀',
        'am': 'መውጣት ተስኖአል',
        'zu': 'Ukuphumula kulwelile',
        'pt': 'Logout bem-sucedido',
    },
    'success_created': {
        'en': 'Resource created successfully',
        'es': 'Recurso creado exitosamente',
        'fr': 'Ressource créée avec succès',
        'sw': 'Rasilimali imeundwa kwa matagumpay',
        'ha': 'Abin ya samu da nasamu',
        'yo': 'Ohun wa pese si baba',
        'am': 'ሀብተ በተሳካ መልኩ ተፈጠረ',
        'zu': 'Ingcebo yenziwe ngempumelelo',
        'pt': 'Recurso criado com sucesso',
    },
    'success_updated': {
        'en': 'Resource updated successfully',
        'es': 'Recurso actualizado exitosamente',
        'fr': 'Ressource mise à jour avec succès',
        'sw': 'Rasilimali imebadilishwa kwa matagumpay',
        'ha': 'Abin ya sabuntawa da nasamu',
        'yo': 'Ohun wa tunsi si ẹbẹ',
        'am': 'ሀብተ በተሳካ መልኩ ታዘበ',
        'zu': 'Ingcebo ibuyisiwe ngempumelelo',
        'pt': 'Recurso atualizado com sucesso',
    },
    'success_deleted': {
        'en': 'Resource deleted successfully',
        'es': 'Recurso eliminado exitosamente',
        'fr': 'Ressource supprimée avec succès',
        'sw': 'Rasilimali imefutwa kwa matagumpay',
        'ha': 'Abin ya goge da nasamu',
        'yo': 'Ohun wa parun ni yoo',
        'am': 'ሀብተ በተሳካ መልኩ ተሰወረ',
        'zu': 'Ingcebo isusiwe ngempumelelo',
        'pt': 'Recurso deletado com sucesso',
    },
    
    # School-specific messages
    'attendance_marked': {
        'en': 'Attendance marked successfully',
        'sw': 'Mahudhurio yameandikwa kwa matagumpay',
        'ha': 'Haihuwa ya akoya yampe',
        'yo': 'Ifipesẹ ti di ipile ni aaye',
        'am': 'ስታትስ በተሳካ መልኩ ተቆጥሮ ነበር',
        'zu': 'Okuhambi kwarekhodiwe ngempumelelo',
        'fr': 'Présence marquée avec succès',
    },
    'fee_payment_recorded': {
        'en': 'Fee payment recorded successfully',
        'sw': 'Malipo ya ada yameandikwa kwa matagumpay',
        'ha': 'Sadarwa jiya ya da ta kora',
        'yo': 'Owo aye ti di ipile ni aaye',
        'am': 'ክፍያ በተሳካ መልኩ ተመዝግቦ ነበር',
        'zu': 'Isambulo solu irekhodiwe ngempumelelo',
        'fr': 'Paiement des frais enregistré avec succès',
    },
    'grade_recorded': {
        'en': 'Grade recorded successfully',
        'sw': 'Daraja limeandikwa kwa matagumpay',
        'ha': 'Jaji ya da samu',
        'yo': 'Iye ti di ipile ni aaye',
        'am': 'ደረጃ በተሳካ መልኩ ተመዝግቦ ነበር',
        'zu': 'Imalusi irekhodiwe ngempumelelo',
        'fr': 'Note enregistrée avec succès',
    },
    
    # Errors
    'error_rate_limit': {
        'en': 'Too many requests. Please try again later.',
        'es': 'Demasiadas solicitudes. Por favor, inténtelo más tarde.',
        'fr': 'Trop de demandes. Veuillez réessayer plus tard.',
        'sw': 'Mabaki mengi sana. Tafadhali jaribu tena baadaye.',
        'ha': 'Ƙarin bukatu da yawa. Da fatan za ku sake yunƙuri jiya.',
        'yo': 'Ebe didara po. Jẹ́ kí àwa gbìyànjú lẹ̀ẹ̀kan ẹlẹ́kan.',
        'am': 'በጣም ብዙ ጥያቄዎች። እባክሙ ከላይ እንደገና ይሞክሩ።',
        'zu': 'Iziselo eziningi kakhulu. Ngiyabingelela uzame futhi kamuva.',
        'pt': 'Muitas solicitações. Por favor, tente novamente mais tarde.',
    },
    'error_invalid_role': {
        'en': 'Invalid user role',
        'es': 'Rol de usuario inválido',
        'fr': 'Rôle d\'utilisateur invalide',
        'sw': 'Jukumu la mtumiaji batili',
        'ha': 'Jaki mai amfani ba shi da inganci',
        'yo': 'Ẹ̀ kọ́ mẹ́ẹ́gá onítìmúlú',
        'am': 'ዋናው ሚና ይህ አይደለም',
        'zu': 'Iqhaza lomsebenzisi alibali',
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
