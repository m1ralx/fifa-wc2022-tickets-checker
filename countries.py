from dataclasses import dataclass

@dataclass(frozen=True)
class Country:
    icon: str
    short: str


COUNTRIES = {
    'Argentina': Country('🇦🇷', 'ARG'),
    'Brazil': Country('🇧🇷', 'BRA'),
    'England': Country('🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'ENG'),
    'France': Country('🇫🇷', 'FRA'),
    'Spain': Country('🇪🇸', 'ESP'),
    'Belgium': Country('🇧🇪', 'BEL'),
    'Portugal': Country('🇵🇹', 'POR'),
    'Germany': Country('🇩🇪', 'GER'),
    'Netherlands': Country('🇳🇱', 'NED'),
    'Uruguay': Country('🇺🇾', 'URU'),
    'Croatia': Country('🇭🇷', 'CRO'),
    'Denmark': Country('🇩🇰', 'DEN'),
    'Mexico': Country('🇲🇽', 'MEX'),
    'USA': Country('🇺🇸', 'USA'),
    'Senegal': Country('🇸🇳', 'SEN'),
    'Wales': Country('🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'WAL'),
    'Poland': Country('🇵🇱', 'POL'),
    'Australia': Country('🇦🇺', 'AUS'),
    'Japan': Country('🇯🇵', 'JPN'),
    'Morocco': Country('🇲🇦', 'MAR'),
    'Switzerland': Country('🇨🇭', 'SUI'),
    'Ghana': Country('🇬🇭', 'GHA'),
    'Korea Republic': Country('🇰🇷', 'KOR'),
    'Cameroon': Country('🇨🇲', 'CMR'),
    'Serbia': Country('🇷🇸', 'SRB'),
    'Canada': Country('🇨🇦', 'CAN'),
    'Costa Rica': Country('🇨🇷', 'CRC'),
    'Tunisia': Country('🇹🇳', 'TUN'),
    'Saudi Arabia': Country('🇸🇦', 'KSA'),
    'Iran': Country('🇮🇷', 'IRN'),
    'Ecuador': Country('🇪🇨', 'ECU'),
    'Qatar': Country('🇶🇦', 'QAT'),
}
