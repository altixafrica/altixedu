"""
African Language Translation Pack
Expands i18n.TRANSLATIONS with comprehensive African language support.

Languages included:
- Swahili (sw): Kenya, Tanzania, Uganda, Rwanda
- Hausa (ha): Nigeria, Niger
- Yoruba (yo): Nigeria, Benin
- Amharic (am): Ethiopia, Eritrea
- Zulu (zu): South Africa, Lesotho

Add to your i18n.py TRANSLATIONS dict:
    from altixedu.african_i18n import AFRICAN_TRANSLATIONS
    TRANSLATIONS.update(AFRICAN_TRANSLATIONS)
"""

AFRICAN_TRANSLATIONS = {
    'error_invalid_credentials': {
        'sw': 'Jina la mtumiaji au neno la siri batili',
        'ha': 'Sunan mai amfani ba shi daidai ko kalmar siri ba',
        'yo': 'Ainú alabájọ̀ tàbí ọ̀rọ̀ aṣínwọ̀ tẹ̀',
        'am': 'ስም ወይም ይለፍ ቃል ልክ ያልሆነ ነው',
        'zu': 'Igama lomusebenzisi noma iphasiwedi engalungile',
    },
    'error_unauthorized': {
        'sw': 'Huna ruhusa ya kupata rasilimali hii',
        'ha': 'Ba ka da izini na samun wannan alhallar ba',
        'yo': 'Ò kò ní oye láti lọ sí ti alábáy yìí',
        'am': 'ለዚህ ሃብት መድረስ ፍቃድ የለብዎም',
        'zu': 'Anayo izimali yokungena le nkomo',
    },
    'error_not_found': {
        'sw': 'Rasilimali haijagundulika',
        'ha': 'Ba a tarar alhallar ba',
        'yo': 'Ohun tó wá kò rí',
        'am': 'ሃብት አልተገኘም',
        'zu': 'Nkomo ayitholakalanga',
    },
    'success_login': {
        'sw': 'Kuingia kwa mwanzo kumefaulu',
        'ha': 'Shiga kumato da nasara',
        'yo': 'Wíwọ ọ̀sán jẹ́ dídí',
        'am': 'ወደ ውስጥ መግባት ተሳክቷል',
        'zu': 'Ukungena kwaluhlile',
    },
    'success_logout': {
        'sw': 'Kuondoka kwa mwanzo kumefaulu',
        'ha': 'Fita kumato da nasara',
        'yo': 'Lọ ọ̀sán ti tẹ́jú dídí',
        'am': 'ከውስጥ ውጣት ተሳክቷል',
        'zu': 'Ukuphuma kwaluhlile',
    },
    'success_created': {
        'sw': 'Rasilimali imeundwa kwa mwanzo',
        'ha': 'Alhallar ya samar da nasara',
        'yo': 'Ọ̀rọ̀ tó ẹrọ jẹ́ dídí',
        'am': 'ሃብት በተሳክ ተፈጠረ',
        'zu': 'I-resource icreated ngempumelelo',
    },
    'success_updated': {
        'sw': 'Rasilimali imesasishwa kwa mwanzo',
        'ha': 'Alhallar an sabunta da nasara',
        'yo': 'Ọ̀rọ̀ tó ẹrọ tútù dídí',
        'am': 'ሃብት በተሳክ ተዘምነ',
        'zu': 'I-resource ibuyisiwe ngempumelelo',
    },
    'success_deleted': {
        'sw': 'Rasilimali imefutwa kwa mwanzo',
        'ha': 'Alhallar ya goge da nasara',
        'yo': 'Ọ̀rọ̀ tó ẹrọ paarẹ dídí',
        'am': 'ሃብት በተሳክ ተሰረዘ',
        'zu': 'I-resource ikhishiwe ngempumelelo',
    },
    'error_rate_limit': {
        'sw': 'Mabaki mengi sana. Tafadhali jaribu tena baadaye.',
        'ha': 'Alamomi da yawa. Tafiya gida da sake jiya.',
        'yo': 'Ìbéèrè pọ̀ jù. E jọ̀wọ́ dá ìgbà kan lọ́tọ́.',
        'am': 'በጣም ብዙ ጥያቄዎች። እባክዎ ቀስ ብለው ይሞክሩ።',
        'zu': 'Izicelo eziningi. Ngiyacela zama kamuva.',
    },
    'error_invalid_role': {
        'sw': 'Jukumu batili',
        'ha': 'Matsayin mai amfani ba shi daidai ba',
        'yo': 'Iṣẹ́ olùmáa tẹ̀',
        'am': 'ልክ ያልሆነ ተጠቃሚ ሚና',
        'zu': 'Iqhaza lomusebenzisi ingalungile',
    },
    'payment_received': {
        'en': 'Payment received successfully',
        'sw': 'Malipo yamokokuwa na mwanzo',
        'ha': 'An karɓo kuɗi da nasara',
        'yo': 'Owó sanwọ́ dídí',
        'am': 'ክፍያ በተሳክ ተቀብሏል',
        'zu': 'Okukhokha kwakwamukele ngempumelelo',
    },
    'attendance_marked': {
        'en': 'Attendance marked successfully',
        'sw': 'Mahudhurio yamejinasaba kwa mwanzo',
        'ha': 'An ninkaya kasuwanci da nasara',
        'yo': 'Ifitumọ̀ ti wá dídí',
        'am': 'ገበታ በተሳክ ምልክት ተደርጓለች',
        'zu': 'Ikhonakhona imakwe ngempumelelo',
    },
    'term_started': {
        'en': 'Academic term started',
        'sw': 'Mudumu wa masomo umeanza',
        'ha': 'An fara suna na karatu',
        'yo': 'Osu ẹ̀kọ́ ti yọ̀',
        'am': 'የአካዳሚክ ቃል ጀመረ',
        'zu': 'I-academic term iqale',
    },
    'fee_payment_due': {
        'en': 'School fee payment is due',
        'sw': 'Malipo ya shule yanakomea',
        'ha': 'Kuɗin sukela yana jiya',
        'yo': 'Owó ile-ẹ̀kọ́ ń kò',
        'am': 'የትምህርት ቤት ክፍያ ሊክፈል ነው',
        'zu': 'Okukhokha i-school fee kufanele',
    },
    'attendance_warning': {
        'en': 'Low attendance warning',
        'sw': 'Onyo wa mahudhurio machache',
        'ha': 'Gargadi kaɗai kaɗai',
        'yo': 'Ìkìlọ ti bá la',
        'am': 'ዝቅተኛ ክፍለ-ጊዜ ጥንቋት',
        'zu': 'Ikhonakhona elimisiwe eliphansi',
    },
}
