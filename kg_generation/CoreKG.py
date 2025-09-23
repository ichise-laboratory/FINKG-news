import csv
import requests

import json
import os

from neo4j_graph import Neo4jGraph
from bs4 import BeautifulSoup
from os.path import exists

from collections import defaultdict


# https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=0001500217
class CoreKG:

    # init method
    def __init__(self) -> None:

        # news mentions company csv path
        self.csv_news_mentions_company_path = "csvTriples/MENTIONS-COMPANY.csv"

        # news mentions event csv path
        self.csv_news_mentions_event_path = "csvTriples/MENTIONS-EVENT.csv"

        # news metadata path
        self.NewsMetadataPath = "data/NEWS-METADATA.jsonl"

        # events json path
        self.eventJsonPath = "data/new_events_with_ids.json"

        # csv triples path
        self.csvTriplesPath = "csvTriples/"

        # use this for having more events (confidene threshold is more lax, 0.9)
        self.csv_event_impacts_path = self.csvTriplesPath + "IMPACTS-CORRECT.csv"
        # use this other file for using less events but more accurate (confidence threshold is 0.91)
        # self.csv_event_impacts_path = self.csvTriplesPath + "IMPACTS-91percThreshold-CORRECT.csv"

        # entity company path
        self.entityCompanyPath = r"entity/Company/"
        # entity company cik path
        self.entityCompanyCikPath = ""

        # entity SecFilings path
        self.entitySecFilingsPath = r"entity/SecFilings/secFilings_"

        # company cik json file path
        self.companyCikJsonPath = "json/submissions/"

        # company 10k file path
        self.company10kFilePath = "10k/"

        # get html company owner files
        self.companyOwnerHtmlFilePath = "html/company/owner/"

        # get html company issuer files
        self.companyIssuerHtmlFilePath = "html/company/issuer/"

        # get html person files
        self.personHtmlFilePath = "html/person/"

        # get json extension name
        self.jsonExtensionName = ".json"

        # get json extension name
        self.jsonSubCompanyExtensionName = "_sub.json"

        # get json extension name
        self.jsonHasPersonExtensionName = "_hasPerson.json"

        # get html extension name
        self.htmlExtensionName = ".html"

        # https://en.wikipedia.org/wiki/Jeff_Bezos
        # wikipedia url
        self.wikiurl = r"https://en.wikipedia.org/wiki/"

        # google personal name
        self.googleSearchEndpoint = r"https://www.google.com/search?q="

        # sec url
        self.secUrl = r"https://www.sec.gov"

        # company owner url
        # https://www.sec.gov/cgi-bin/own-disp?action=getowner&CIK=0001018724
        self.companyOwnerUrl = r"https://www.sec.gov/cgi-bin/own-disp?action=getowner&CIK="

        # company issuer url
        # https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=0001018724
        # https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=0001018724&type=&dateb=&owner=include&start=0&count=10000
        self.companyIssuerUrl = r"https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK="
        self.companyStockRecords = r"&type=&dateb=&owner=include&start=0&count=1000"

        # txt 10k filename
        self.txt10kfilename = r"10k/0000002488-16-000111.txt"

        # sec edgar data url
        self.edgar_data_endpoint = r"https://www.sec.gov/Archives/edgar/data/"

        # company 10k filename url: https://www.sec.gov/Archives/edgar/data/0001018724/0001018724-14-000006.txt
        self.sec_company_10k_filename_url = None

        # sec company home page base url https://www.sec.gov/edgar/browse/?CIK=0001018724&owner=include
        self.sec_company_homepage_base_url = r"https://www.sec.gov/edgar/browse/?CIK="

        # sec company home page url
        self.sec_company_homepage_param_owner_url = r"&owner=include"

        # company CIK and 10k file name
        self.company_cik_10kfilename = r"data/CompanyCik10kFilename.csv"

        # company CIK, ticker and 10k file name
        # self.company_cik_ticker_10kfilename = r"data/CompanyCikTicker10kFilename.csv"
        # self.company_cik_ticker_10kfilename ="data\CompanyCikTicker10kFilename_testing.csv"
        # self.company_cik_ticker_10kfilename = r"data/test.csv"
        self.company_cik_ticker_10kfilename = r"data/CompanyCikTicker10kFilename_2000to2025_SP500_400_600.csv"
        # self.company_cik_ticker_10kfilename = r"data\CompanyCikTicker10kFilename_2000to2025_SP500_400_600-REDUCED.csv"

        # company ticker, CIK and title json file name
        self.company_ticker_cik_file = r"data/company_tickers.json"

        # security exchange name path
        self.securityExchangeNamePath = r"data/SecurityExchangeName/SecurityExchangeName.txt"

        # security exchange name path
        self.exchangeEntityFilename = r"data/exchangeEntity.csv"

        # security exchange ticker
        self.securityExchangeTickers = ['NYSE','NASDAQ','CHX','BOX','BX','C2','CBOE','CboeBYX','CboeBZX','CboeEDGA','CboeEDGX','GEMX','IEX','ISE','MIAX','MRX','NYSEAMER','NYSEArca','NYSENAT','PEARL','Phlx']

        # sec country code 246
        # self.secCountryCode = ['B2','Y6','B3','B4','B5','B6','B7','1A','B8','B9','C1','1B','1C','C3','C4','1D','C5','C6','C7','C8','1F','C9','D1','G6','D0','D2','D3','1E','B1','D4','D5','D6','D9','E0','X2','E2','E3','E4','Z4','E8','E9','F0','F2','F3','F4','F6','F7','F8','F9','G0','Y3','G1','G2','L7','1M','G3','G4','2N','G7','1G','G9','G8','H1','H2','H3','H4','1J','1H','H5','H7','H6','H8','H9','I0','I3','I4','2C','I5','I6','2Q','2M','J0','J1','J3','J4','J5','J6','GU','J8','Y7','J9','S0','K0','K1','K4','X4','K2','K3','K5','K6','K7','K8','K9','L0','L2','Y8','L3','L6','L8','M0','Y9','M2','1P','M3','J2','M4','M5','M6','1N','M7','1R','M8','M9','N0','N1','N2','1Q','N4','N5','1U','N6','N7','N8','N9','O0','O1','1T','O2','O3','O4','2P','O5','1K','1S','O9','P0','Z5','P1','P2','P3','E1','T6','P5','P6','P7','P8','1W','Q2','Q3','Q4','Q5','Q6','Q7','1V','Q8','P4','R0','1Y','1X','R1','R2','R4','R5','R6','R8','R9','S1','PR','S3','S4','S5','1Z','S6','Z0','U8','U7','U9','Z1','V0','V1','Y0','S8','S9','T0','T1','Z2','T2','T8','U0','2B','2A','D7','U1','T3','1L','U3','F1','V2','V3','L9','V6','V7','V8','V9','F5','2D','W0','W1','Z3','W2','W3','W4','W5','W6','W8','2E','W7','2G','W9','2H','C0','X0','2J','X3','2K','2L','X5','Q1','D8','VI','X8','U5','T7','Y4','Y5','XX']

        # sec country name 246
        # self.secCountryName = ["AFGHANISTAN","ALAND ISLANDS","ALBANIA","ALGERIA","AMERICAN SAMOA","ANDORRA","ANGOLA","ANGUILLA","ANTARCTICA","ANTIGUA AND BARBUDA","ARGENTINA","ARMENIA","ARUBA","AUSTRALIA","AUSTRIA","AZERBAIJAN","BAHAMAS","BAHRAIN","BANGLADESH","BARBADOS","BELARUS","BELGIUM","BELIZE","BENIN","BERMUDA","BHUTAN","BOLIVIA","BOSNIA AND HERZEGOVINA","BOTSWANA","BOUVET ISLAND","BRAZIL","BRITISH INDIAN OCEAN TERRITORY","BRUNEI DARUSSALAM","BULGARIA","BURKINA FASO","BURUNDI","CAMBODIA","CAMEROON","CANADA (Federal Level)","CAPE VERDE","CAYMAN ISLANDS","CENTRAL AFRICAN REPUBLIC","CHAD","CHILE","CHINA","CHRISTMAS ISLAND","COCOS (KEELING) ISLANDS","COLOMBIA","COMOROS","CONGO","CONGO, THE DEMOCRATIC REPUBLIC OF THE","COOK ISLANDS","COSTA RICA","COTE D'IVOIRE","CROATIA","CUBA","CYPRUS","CZECH REPUBLIC","DENMARK","DJIBOUTI","DOMINICA","DOMINICAN REPUBLIC","ECUADOR","EGYPT","EL SALVADOR","EQUATORIAL GUINEA","ERITREA","ESTONIA","ETHIOPIA","FALKLAND ISLANDS (MALVINAS)","FAROE ISLANDS","FIJI","FINLAND","FRANCE","FRENCH GUIANA","FRENCH POLYNESIA","FRENCH SOUTHERN TERRITORIES","GABON","GAMBIA","GEORGIA","GERMANY","GHANA","GIBRALTAR","GREECE","GREENLAND","GRENADA","GUADELOUPE","GUAM","GUATEMALA","GUERNSEY","GUINEA","GUINEA-BISSAU","GUYANA","HAITI","HEARD ISLAND AND MCDONALD ISLANDS","HOLY SEE (VATICAN CITY STATE)","HONDURAS","HONG KONG","HUNGARY","ICELAND","INDIA","INDONESIA","IRAN, ISLAMIC REPUBLIC OF","IRAQ","IRELAND","ISLE OF MAN","ISRAEL","ITALY","JAMAICA","JAPAN","JERSEY","JORDAN","KAZAKSTAN","KENYA","KIRIBATI","KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF","KOREA, REPUBLIC OF","KUWAIT","KYRGYZSTAN","LAO PEOPLE'S DEMOCRATIC REPUBLIC","LATVIA","LEBANON","LESOTHO","LIBERIA","LIBYAN ARAB JAMAHIRIYA","LIECHTENSTEIN","LITHUANIA","LUXEMBOURG","MACAU","MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF","MADAGASCAR","MALAWI","MALAYSIA","MALDIVES","MALI","MALTA","MARSHALL ISLANDS","MARTINIQUE","MAURITANIA","MAURITIUS","MAYOTTE","MEXICO","MICRONESIA, FEDERATED STATES OF","MOLDOVA, REPUBLIC OF","MONACO","MONGOLIA","MONTENEGRO","MONTSERRAT","MOROCCO","MOZAMBIQUE","MYANMAR","NAMIBIA","NAURU","NEPAL","NETHERLANDS","NETHERLANDS ANTILLES","NEW CALEDONIA","NEW ZEALAND","NICARAGUA","NIGER","NIGERIA","NIUE","NORFOLK ISLAND","NORTHERN MARIANA ISLANDS","NORWAY","OMAN","PAKISTAN","PALAU","PALESTINIAN TERRITORY, OCCUPIED","PANAMA","PAPUA NEW GUINEA","PARAGUAY","PERU","PHILIPPINES","PITCAIRN","POLAND","PORTUGAL","PUERTO RICO","QATAR","REUNION","ROMANIA","RUSSIAN FEDERATION","RWANDA","SAINT BARTHELEMY","SAINT HELENA","SAINT KITTS AND NEVIS","SAINT LUCIA","SAINT MARTIN","SAINT PIERRE AND MIQUELON","SAINT VINCENT AND THE GRENADINES","SAMOA","SAN MARINO","SAO TOME AND PRINCIPE","SAUDI ARABIA","SENEGAL","SERBIA","SEYCHELLES","SIERRA LEONE","SINGAPORE","SLOVAKIA","SLOVENIA","SOLOMON ISLANDS","SOMALIA","SOUTH AFRICA","SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS","SPAIN","SRI LANKA","SUDAN","SURINAME","SVALBARD AND JAN MAYEN","SWAZILAND","SWEDEN","SWITZERLAND","SYRIAN ARAB REPUBLIC","TAIWAN","TAJIKISTAN","TANZANIA, UNITED REPUBLIC OF","THAILAND","TIMOR-LESTE","TOGO","TOKELAU","TONGA","TRINIDAD AND TOBAGO","TUNISIA","TURKEY","TURKMENISTAN","TURKS AND CAICOS ISLANDS","TUVALU","UGANDA","UKRAINE","UNITED ARAB EMIRATES","UNITED KINGDOM","UNITED STATES MINOR OUTLYING ISLANDS","URUGUAY","UZBEKISTAN","VANUATU","VENEZUELA","VIET NAM","VIRGIN ISLANDS, BRITISH","VIRGIN ISLANDS, U.S.","WALLIS AND FUTUNA","WESTERN SAHARA","YEMEN","ZAMBIA","ZIMBABWE","UNKNOWN"]

        self.isoAlpha2Code = ['AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ', 'BA', 'BW', 'BV', 'BR', 'IO', 'VG', 'BN', 'BG', 'BF', 'BI', 'CV', 'KH', 'CM', 'CA', 'KY', 'CF', 'TD', 'CL', 'CN', 'HK', 'MO', 'CX', 'CC', 'CO', 'KM', 'CG', 'CK', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'KP', 'CD', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'SZ', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'TF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT', 'HM', 'VA', 'HN', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP', 'JE', 'JO', 'KZ', 'KE', 'KI', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'MK', 'MP', 'NO', 'OM', 'PK', 'PW', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'KR', 'MD', 'RE', 'RO', 'RU', 'RW', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'SS', 'ES', 'LK', 'PS', 'SD', 'SR', 'SJ', 'SE', 'CH', 'SY', 'TJ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'GB', 'TZ', 'UM', 'US', 'VI', 'UY', 'UZ', 'VU', 'VE', 'VN', 'WF', 'EH', 'YE', 'ZM', 'ZW']

        self.isoAlpha3Code = ['AFG','ALA','ALB','DZA','ASM','AND','AGO','AIA','ATA','ATG','ARG','ARM','ABW','AUS','AUT','AZE','BHS','BHR','BGD','BRB','BLR','BEL','BLZ','BEN','BMU','BTN','BOL','BES','BIH','BWA','BVT','BRA','IOT','VGB','BRN','BGR','BFA','BDI','CPV','KHM','CMR','CAN','CYM','CAF','TCD','CHL','CHN','HKG','MAC','CXR','CCK','COL','COM','COG','COK','CRI','CIV','HRV','CUB','CUW','CYP','CZE','PRK','COD','DNK','DJI','DMA','DOM','ECU','EGY','SLV','GNQ','ERI','EST','SWZ','ETH','FLK','FRO','FJI','FIN','FRA','GUF','PYF','ATF','GAB','GMB','GEO','DEU','GHA','GIB','GRC','GRL','GRD','GLP','GUM','GTM','GGY','GIN','GNB','GUY','HTI','HMD','VAT','HND','HUN','ISL','IND','IDN','IRN','IRQ','IRL','IMN','ISR','ITA','JAM','JPN','JEY','JOR','KAZ','KEN','KIR','KWT','KGZ','LAO','LVA','LBN','LSO','LBR','LBY','LIE','LTU','LUX','MDG','MWI','MYS','MDV','MLI','MLT','MHL','MTQ','MRT','MUS','MYT','MEX','FSM','MCO','MNG','MNE','MSR','MAR','MOZ','MMR','NAM','NRU','NPL','NLD','NCL','NZL','NIC','NER','NGA','NIU','NFK','MKD','MNP','NOR','OMN','PAK','PLW','PAN','PNG','PRY','PER','PHL','PCN','POL','PRT','PRI','QAT','KOR','MDA','REU','ROU','RUS','RWA','BLM','SHN','KNA','LCA','MAF','SPM','VCT','WSM','SMR','STP','','SAU','SEN','SRB','SYC','SLE','SGP','SXM','SVK','SVN','SLB','SOM','ZAF','SGS','SSD','ESP','LKA','PSE','SDN','SUR','SJM','SWE','CHE','SYR','TJK','THA','TLS','TGO','TKL','TON','TTO','TUN','TUR','TKM','TCA','TUV','UGA','UKR','ARE','GBR','TZA','UMI','USA','VIR','URY','UZB','VUT','VEN','VNM','WLF','ESH','YEM','ZMB','ZWE']

        self.isoM49Code = ['004','248','008','012','016','020','024','660','010','028','032','051','533','036','040','031','044','048','050','052','112','056','084','204','060','064','068','535','070','072','074','076','086','092','096','100','854','108','132','116','120','124','136','140','148','152','156','344','446','162','166','170','174','178','184','188','384','191','192','531','196','203','408','180','208','262','212','214','218','818','222','226','232','233','748','231','238','234','242','246','250','254','258','260','266','270','268','276','288','292','300','304','308','312','316','320','831','324','624','328','332','334','336','340','348','352','356','360','364','368','372','833','376','380','388','392','832','400','398','404','296','414','417','418','428','422','426','430','434','438','440','442','450','454','458','462','466','470','584','474','478','480','175','484','583','492','496','499','500','504','508','104','516','520','524','528','540','554','558','562','566','570','574','807','580','578','512','586','585','591','598','600','604','608','612','616','620','630','634','410','498','638','642','643','646','652','654','659','662','663','666','670','882','674','678','680','682','686','688','690','694','702','534','703','705','090','706','710','239','728','724','144','275','729','740','744','752','756','760','762','764','626','768','772','776','780','788','792','795','796','798','800','804','784','826','834','581','840','850','858','860','548','862','704','876','732','887','894','716']

        self.isoName = ["Afghanistan","Åland Islands","Albania","Algeria","American Samoa","Andorra","Angola","Anguilla","Antarctica","Antigua and Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia (Plurinational State of)","Bonaire, Sint Eustatius and Saba","Bosnia and Herzegovina","Botswana","Bouvet Island","Brazil","British Indian Ocean Territory","British Virgin Islands","Brunei Darussalam","Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada","Cayman Islands","Central African Republic","Chad","Chile","China","China, Hong Kong Special Administrative Region","China, Macao Special Administrative Region","Christmas Island","Cocos (Keeling) Islands","Colombia","Comoros","Congo","Cook Islands","Costa Rica","Côte d’Ivoire","Croatia","Cuba","Curaçao","Cyprus","Czechia","Democratic People's Republic of Korea","Democratic Republic of the Congo","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Falkland Islands (Malvinas)","Faroe Islands","Fiji","Finland","France","French Guiana","French Polynesia","French Southern Territories","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guadeloupe","Guam","Guatemala","Guernsey","Guinea","Guinea-Bissau","Guyana","Haiti","Heard Island and McDonald Islands","Holy See","Honduras","Hungary","Iceland","India","Indonesia","Iran (Islamic Republic of)","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan","Lao People's Democratic Republic","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Martinique","Mauritania","Mauritius","Mayotte","Mexico","Micronesia (Federated States of)","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal","Netherlands","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","Niue","Norfolk Island","North Macedonia","Northern Mariana Islands","Norway","Oman","Pakistan","Palau","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Pitcairn","Poland","Portugal","Puerto Rico","Qatar","Republic of Korea","Republic of Moldova","Réunion","Romania","Russian Federation","Rwanda","Saint Barthélemy","Saint Helena","Saint Kitts and Nevis","Saint Lucia","Saint Martin (French Part)","Saint Pierre and Miquelon","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Sark","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Sint Maarten (Dutch part)","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Georgia and the South Sandwich Islands","South Sudan","Spain","Sri Lanka","State of Palestine","Sudan","Suriname","Svalbard and Jan Mayen Islands","Sweden","Switzerland","Syrian Arab Republic","Tajikistan","Thailand","Timor-Leste","Togo","Tokelau","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Turks and Caicos Islands","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom of Great Britain and Northern Ireland","United Republic of Tanzania","United States Minor Outlying Islands","United States of America","United States Virgin Islands","Uruguay","Uzbekistan","Vanuatu","Venezuela (Bolivarian Republic of)","Viet Nam","Wallis and Futuna Islands","Western Sahara","Yemen","Zambia","Zimbabwe"]

        # state code
        self.stateCode = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','X1','UT','VT','VA','WA','WV','WI','WY']

        # state name
        self.stateName = ['ALABAMA','ALASKA','ARIZONA','ARKANSAS','CALIFORNIA','COLORADO','CONNECTICUT','DELAWARE','DISTRICT OF COLUMB','FLORIDA','GEORGIA','HAWAII','IDAHO','ILLINOIS','INDIANA','IOWA','KANSAS','KENTUCKY','LOUISIANA','MAINE','MARYLAND','MASSACHUSETTS','MICHIGAN','MINNESOTA','MISSISSIPPI','MISSOURI','MONTANA','NEBRASKA','NEVADA','NEW HAMPSHIRE','NEW JERSEY','NEW MEXICO','NEW YORK','NORTH CAROLINA','NORTH DAKOTA','OHIO','OKLAHOMA','OREGON','PENNSYLVANIA','RHODE ISLAND','SOUTH CAROLINA','SOUTH DAKOTA','TENNESSEE','TEXAS','UNITED STATES','UTAH','VERMONT','VIRGINIA','WASHINGTON','WEST VIRGINIA','WISCONSIN','WYOMING']

        # sic Code
        self.sicCode = ['100','200','700','800','900','1000','1040','1090','1220','1221','1311','1381','1382','1389','1400','1520','1531','1540','1600','1623','1700','1731','2000','2011','2013','2015','2020','2024','2030','2033','2040','2050','2052','2060','2070','2080','2082','2086','2090','2092','2100','2111','2200','2211','2221','2250','2253','2273','2300','2320','2330','2340','2390','2400','2421','2430','2451','2452','2510','2511','2520','2522','2531','2540','2590','2600','2611','2621','2631','2650','2670','2673','2711','2721','2731','2732','2741','2750','2761','2771','2780','2790','2800','2810','2820','2821','2833','2834','2835','2836','2840','2842','2844','2851','2860','2870','2890','2891','2911','2950','2990','3011','3021','3050','3060','3080','3081','3086','3089','3100','3140','3211','3220','3221','3231','3241','3250','3260','3270','3272','3281','3290','3310','3312','3317','3320','3330','3334','3341','3350','3357','3360','3390','3411','3412','3420','3430','3433','3440','3442','3443','3444','3448','3451','3452','3460','3470','3480','3490','3510','3523','3524','3530','3531','3532','3533','3537','3540','3541','3550','3555','3559','3560','3561','3562','3564','3567','3569','3570','3571','3572','3575','3576','3577','3578','3579','3580','3585','3590','3600','3612','3613','3620','3621','3630','3634','3640','3651','3652','3661','3663','3669','3670','3672','3674','3677','3678','3679','3690','3695','3711','3713','3714','3715','3716','3720','3721','3724','3728','3730','3743','3751','3760','3790','3812','3821','3822','3823','3824','3825','3826','3827','3829','3841','3842','3843','3844','3845','3851','3861','3873','3910','3911','3931','3942','3944','3949','3950','3960','3990','4011','4013','4100','4210','4213','4220','4231','4400','4412','4512','4513','4522','4581','4610','4700','4731','4812','4813','4822','4832','4833','4841','4899','4900','4911','4922','4923','4924','4931','4932','4941','4950','4953','4955','4961','4991','5000','5010','5013','5020','5030','5031','5040','5045','5047','5050','5051','5063','5064','5065','5070','5072','5080','5082','5084','5090','5094','5099','5110','5122','5130','5140','5141','5150','5160','5171','5172','5180','5190','5200','5211','5271','5311','5331','5399','5400','5411','5412','5500','5531','5600','5621','5651','5661','5700','5712','5731','5734','5735','5810','5812','5900','5912','5940','5944','5945','5960','5961','5990','6021','6022','6029','6035','6036','6099','6111','6141','6153','6159','6162','6163','6172','6189','6199','6200','6211','6221','6282','6311','6321','6324','6331','6351','6361','6399','6411','6500','6510','6512','6513','6519','6531','6532','6552','6770','6792','6794','6795','6798','6799','7000','7011','7200','7310','7311','7320','7330','7331','7340','7350','7359','7361','7363','7370','7371','7372','7373','7374','7377','7380','7381','7384','7385','7389','7500','7510','7600','7812','7819','7822','7829','7830','7841','7900','7948','7990','7997','8000','8011','8050','8051','8060','8062','8071','8082','8090','8093','8111','8200','8300','8351','8600','8700','8711','8731','8734','8741','8742','8744','8880','8888','8900','9721','9995']

        # sic office
        self.sicOffice = ["Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Manufacturing","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Energy & Transportation","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Structured Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Finance","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Real Estate & Construction","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Technology","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Life Sciences","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of Trade & Services","Office of International Corp Fin","Office of International Corp Fin","Office of Trade & Services","Office of International Corp Fin","Office of Real Estate & Construction"]

        # sic name
        self.sicName = ["AGRICULTURAL PRODUCTION-CROPS","AGRICULTURAL PROD-LIVESTOCK & ANIMAL SPECIALTIES","AGRICULTURAL SERVICES","FORESTRY","FISHING, HUNTING AND TRAPPING","METAL MINING","GOLD AND SILVER ORES","MISCELLANEOUS METAL ORES","BITUMINOUS COAL & LIGNITE MINING","BITUMINOUS COAL & LIGNITE SURFACE MINING","CRUDE PETROLEUM & NATURAL GAS","DRILLING OIL & GAS WELLS","OIL & GAS FIELD EXPLORATION SERVICES","OIL & GAS FIELD SERVICES, NEC","MINING & QUARRYING OF NONMETALLIC MINERALS (NO FUELS)","GENERAL BLDG CONTRACTORS - RESIDENTIAL BLDGS","OPERATIVE BUILDERS","GENERAL BLDG CONTRACTORS - NONRESIDENTIAL BLDGS","HEAVY CONSTRUCTION OTHER THAN BLDG CONST - CONTRACTORS","WATER, SEWER, PIPELINE, COMM & POWER LINE CONSTRUCTION","CONSTRUCTION - SPECIAL TRADE CONTRACTORS","ELECTRICAL WORK","FOOD AND KINDRED PRODUCTS","MEAT PACKING PLANTS","SAUSAGES & OTHER PREPARED MEAT PRODUCTS","POULTRY SLAUGHTERING AND PROCESSING","DAIRY PRODUCTS","ICE CREAM & FROZEN DESSERTS","CANNED, FROZEN & PRESERVD FRUIT, VEG & FOOD SPECIALTIES","CANNED, FRUITS, VEG, PRESERVES, JAMS & JELLIES","GRAIN MILL PRODUCTS","BAKERY PRODUCTS","COOKIES & CRACKERS","SUGAR & CONFECTIONERY PRODUCTS","FATS & OILS","BEVERAGES","MALT BEVERAGES","BOTTLED & CANNED SOFT DRINKS & CARBONATED WATERS","MISCELLANEOUS FOOD PREPARATIONS & KINDRED PRODUCTS","PREPARED FRESH OR FROZEN FISH & SEAFOODS","TOBACCO PRODUCTS","CIGARETTES","TEXTILE MILL PRODUCTS","BROADWOVEN FABRIC MILLS, COTTON","BROADWOVEN FABRIC MILLS, MAN MADE FIBER & SILK","KNITTING MILLS","KNIT OUTERWEAR MILLS","CARPETS & RUGS","APPAREL & OTHER FINISHD PRODS OF FABRICS & SIMILAR MATL","MEN'S & BOYS' FURNISHGS, WORK CLOTHG, & ALLIED GARMENTS","WOMEN'S, MISSES', AND JUNIORS OUTERWEAR","WOMEN'S, MISSES', CHILDREN'S & INFANTS' UNDERGARMENTS","MISCELLANEOUS FABRICATED TEXTILE PRODUCTS","LUMBER & WOOD PRODUCTS (NO FURNITURE)","SAWMILLS & PLANTING MILLS, GENERAL","MILLWOOD, VENEER, PLYWOOD, & STRUCTURAL WOOD MEMBERS","MOBILE HOMES","PREFABRICATED WOOD BLDGS & COMPONENTS","HOUSEHOLD FURNITURE","WOOD HOUSEHOLD FURNITURE, (NO UPHOLSTERED)","OFFICE FURNITURE","OFFICE FURNITURE (NO WOOD)","PUBLIC BLDG & RELATED FURNITURE","PARTITIONS, SHELVG, LOCKERS, & OFFICE & STORE FIXTURES","MISCELLANEOUS FURNITURE & FIXTURES","PAPERS & ALLIED PRODUCTS","PULP MILLS","PAPER MILLS","PAPERBOARD MILLS","PAPERBOARD CONTAINERS & BOXES","CONVERTED PAPER & PAPERBOARD PRODS (NO CONTANERS/BOXES)","PLASTICS, FOIL & COATED PAPER BAGS","NEWSPAPERS: PUBLISHING OR PUBLISHING & PRINTING","PERIODICALS: PUBLISHING OR PUBLISHING & PRINTING","BOOKS: PUBLISHING OR PUBLISHING & PRINTING","BOOK PRINTING","MISCELLANEOUS PUBLISHING","COMMERCIAL PRINTING","MANIFOLD BUSINESS FORMS","GREETING CARDS","BLANKBOOKS, LOOSELEAF BINDERS & BOOKBINDG & RELATD WORK","SERVICE INDUSTRIES FOR THE PRINTING TRADE","CHEMICALS & ALLIED PRODUCTS","INDUSTRIAL INORGANIC CHEMICALS","PLASTIC MATERIAL, SYNTH RESIN/RUBBER, CELLULOS (NO GLASS)","PLASTIC MATERIALS, SYNTH RESINS & NONVULCAN ELASTOMERS","MEDICINAL CHEMICALS & BOTANICAL PRODUCTS","PHARMACEUTICAL PREPARATIONS","IN VITRO & IN VIVO DIAGNOSTIC SUBSTANCES","BIOLOGICAL PRODUCTS, (NO DISGNOSTIC SUBSTANCES)","SOAP, DETERGENTS, CLEANG PREPARATIONS, PERFUMES, COSMETICS","SPECIALTY CLEANING, POLISHING AND SANITATION PREPARATIONS","PERFUMES, COSMETICS & OTHER TOILET PREPARATIONS","PAINTS, VARNISHES, LACQUERS, ENAMELS & ALLIED PRODS","INDUSTRIAL ORGANIC CHEMICALS","AGRICULTURAL CHEMICALS","MISCELLANEOUS CHEMICAL PRODUCTS","ADHESIVES & SEALANTS","PETROLEUM REFINING","ASPHALT PAVING & ROOFING MATERIALS","MISCELLANEOUS PRODUCTS OF PETROLEUM & COAL","TIRES & INNER TUBES","RUBBER & PLASTICS FOOTWEAR","GASKETS, PACKG & SEALG DEVICES & RUBBER & PLASTICS HOSE","FABRICATED RUBBER PRODUCTS, NEC","MISCELLANEOUS PLASTICS PRODUCTS","UNSUPPORTED PLASTICS FILM & SHEET","PLASTICS FOAM PRODUCTS","PLASTICS PRODUCTS, NEC","LEATHER & LEATHER PRODUCTS","FOOTWEAR, (NO RUBBER)","FLAT GLASS","GLASS & GLASSWARE, PRESSED OR BLOWN","GLASS CONTAINERS","GLASS PRODUCTS, MADE OF PURCHASED GLASS","CEMENT, HYDRAULIC","STRUCTURAL CLAY PRODUCTS","POTTERY & RELATED PRODUCTS","CONCRETE, GYPSUM & PLASTER PRODUCTS","CONCRETE PRODUCTS, EXCEPT BLOCK & BRICK","CUT STONE & STONE PRODUCTS","ABRASIVE, ASBESTOS & MISC NONMETALLIC MINERAL PRODS","STEEL WORKS, BLAST FURNACES & ROLLING & FINISHING MILLS","STEEL WORKS, BLAST FURNACES & ROLLING MILLS (COKE OVENS)","STEEL PIPE & TUBES","IRON & STEEL FOUNDRIES","PRIMARY SMELTING & REFINING OF NONFERROUS METALS","PRIMARY PRODUCTION OF ALUMINUM","SECONDARY SMELTING & REFINING OF NONFERROUS METALS","ROLLING DRAWING & EXTRUDING OF NONFERROUS METALS","DRAWING & INSULATING OF NONFERROUS WIRE","NONFERROUS FOUNDRIES (CASTINGS)","MISCELLANEOUS PRIMARY METAL PRODUCTS","METAL CANS","METAL SHIPPING BARRELS, DRUMS, KEGS & PAILS","CUTLERY, HANDTOOLS & GENERAL HARDWARE","HEATING EQUIP, EXCEPT ELEC & WARM AIR; & PLUMBING FIXTURES","HEATING EQUIPMENT, EXCEPT ELECTRIC & WARM AIR FURNACES","FABRICATED STRUCTURAL METAL PRODUCTS","METAL DOORS, SASH, FRAMES, MOLDINGS & TRIM","FABRICATED PLATE WORK (BOILER SHOPS)","SHEET METAL WORK","PREFABRICATED METAL BUILDINGS & COMPONENTS","SCREW MACHINE PRODUCTS","BOLTS, NUTS, SCREWS, RIVETS & WASHERS","METAL FORGINGS & STAMPINGS","COATING, ENGRAVING & ALLIED SERVICES","ORDNANCE & ACCESSORIES, (NO VEHICLES/GUIDED MISSILES)","MISCELLANEOUS FABRICATED METAL PRODUCTS","ENGINES & TURBINES","FARM MACHINERY & EQUIPMENT","LAWN & GARDEN TRACTORS & HOME LAWN & GARDENS EQUIP","CONSTRUCTION, MINING & MATERIALS HANDLING MACHINERY & EQUIP","CONSTRUCTION MACHINERY & EQUIP","MINING MACHINERY & EQUIP (NO OIL & GAS FIELD MACH & EQUIP)","OIL & GAS FIELD MACHINERY & EQUIPMENT","INDUSTRIAL TRUCKS, TRACTORS, TRAILORS & STACKERS","METALWORKG MACHINERY & EQUIPMENT","MACHINE TOOLS, METAL CUTTING TYPES","SPECIAL INDUSTRY MACHINERY (NO METALWORKING MACHINERY)","PRINTING TRADES MACHINERY & EQUIPMENT","SPECIAL INDUSTRY MACHINERY, NEC","GENERAL INDUSTRIAL MACHINERY & EQUIPMENT","PUMPS & PUMPING EQUIPMENT","BALL & ROLLER BEARINGS","INDUSTRIAL & COMMERCIAL FANS & BLOWERS & AIR PURIFING EQUIP","INDUSTRIAL PROCESS FURNACES & OVENS","GENERAL INDUSTRIAL MACHINERY & EQUIPMENT, NEC","COMPUTER & OFFICE EQUIPMENT","ELECTRONIC COMPUTERS","COMPUTER STORAGE DEVICES","COMPUTER TERMINALS","COMPUTER COMMUNICATIONS EQUIPMENT","COMPUTER PERIPHERAL EQUIPMENT, NEC","CALCULATING & ACCOUNTING MACHINES (NO ELECTRONIC COMPUTERS)","OFFICE MACHINES, NEC","REFRIGERATION & SERVICE INDUSTRY MACHINERY","AIR-COND & WARM AIR HEATG EQUIP & COMM & INDL REFRIG EQUIP","MISC INDUSTRIAL & COMMERCIAL MACHINERY & EQUIPMENT","ELECTRONIC & OTHER ELECTRICAL EQUIPMENT (NO COMPUTER EQUIP)","POWER, DISTRIBUTION & SPECIALTY TRANSFORMERS","SWITCHGEAR & SWITCHBOARD APPARATUS","ELECTRICAL INDUSTRIAL APPARATUS","MOTORS & GENERATORS","HOUSEHOLD APPLIANCES","ELECTRIC HOUSEWARES & FANS","ELECTRIC LIGHTING & WIRING EQUIPMENT","HOUSEHOLD AUDIO & VIDEO EQUIPMENT","PHONOGRAPH RECORDS & PRERECORDED AUDIO TAPES & DISKS","TELEPHONE & TELEGRAPH APPARATUS","RADIO & TV BROADCASTING & COMMUNICATIONS EQUIPMENT","COMMUNICATIONS EQUIPMENT, NEC","ELECTRONIC COMPONENTS & ACCESSORIES","PRINTED CIRCUIT BOARDS","SEMICONDUCTORS & RELATED DEVICES","ELECTRONIC COILS, TRANSFORMERS & OTHER INDUCTORS","ELECTRONIC CONNECTORS","ELECTRONIC COMPONENTS, NEC","MISCELLANEOUS ELECTRICAL MACHINERY, EQUIPMENT & SUPPLIES","MAGNETIC & OPTICAL RECORDING MEDIA","MOTOR VEHICLES & PASSENGER CAR BODIES","TRUCK & BUS BODIES","MOTOR VEHICLE PARTS & ACCESSORIES","TRUCK TRAILERS","MOTOR HOMES","AIRCRAFT & PARTS","AIRCRAFT","AIRCRAFT ENGINES & ENGINE PARTS","AIRCRAFT PARTS & AUXILIARY EQUIPMENT, NEC","SHIP & BOAT BUILDING & REPAIRING","RAILROAD EQUIPMENT","MOTORCYCLES, BICYCLES & PARTS","GUIDED MISSILES & SPACE VEHICLES & PARTS","MISCELLANEOUS TRANSPORTATION EQUIPMENT","SEARCH, DETECTION, NAVAGATION, GUIDANCE, AERONAUTICAL SYS","LABORATORY APPARATUS & FURNITURE","AUTO CONTROLS FOR REGULATING RESIDENTIAL & COMML ENVIRONMENTS","INDUSTRIAL INSTRUMENTS FOR MEASUREMENT, DISPLAY, AND CONTROL","TOTALIZING FLUID METERS & COUNTING DEVICES","INSTRUMENTS FOR MEAS & TESTING OF ELECTRICITY & ELEC SIGNALS","LABORATORY ANALYTICAL INSTRUMENTS","OPTICAL INSTRUMENTS & LENSES","MEASURING & CONTROLLING DEVICES, NEC","SURGICAL & MEDICAL INSTRUMENTS & APPARATUS","ORTHOPEDIC, PROSTHETIC & SURGICAL APPLIANCES & SUPPLIES","DENTAL EQUIPMENT & SUPPLIES","X-RAY APPARATUS & TUBES & RELATED IRRADIATION APPARATUS","ELECTROMEDICAL & ELECTROTHERAPEUTIC APPARATUS","OPHTHALMIC GOODS","PHOTOGRAPHIC EQUIPMENT & SUPPLIES","WATCHES, CLOCKS, CLOCKWORK OPERATED DEVICES/PARTS","JEWELRY, SILVERWARE & PLATED WARE","JEWELRY, PRECIOUS METAL","MUSICAL INSTRUMENTS","DOLLS & STUFFED TOYS","GAMES, TOYS & CHILDREN'S VEHICLES (NO DOLLS & BICYCLES)","SPORTING & ATHLETIC GOODS, NEC","PENS, PENCILS & OTHER ARTISTS' MATERIALS","COSTUME JEWELRY & NOVELTIES","MISCELLANEOUS MANUFACTURING INDUSTRIES","RAILROADS, LINE-HAUL OPERATING","RAILROAD SWITCHING & TERMINAL ESTABLISHMENTS","LOCAL & SUBURBAN TRANSIT & INTERURBAN HWY PASSENGER TRANS","TRUCKING & COURIER SERVICES (NO AIR)","TRUCKING (NO LOCAL)","PUBLIC WAREHOUSING & STORAGE","TERMINAL MAINTENANCE FACILITIES FOR MOTOR FREIGHT TRANSPORT","WATER TRANSPORTATION","DEEP SEA FOREIGN TRANSPORTATION OF FREIGHT","AIR TRANSPORTATION, SCHEDULED","AIR COURIER SERVICES","AIR TRANSPORTATION, NONSCHEDULED","AIRPORTS, FLYING FIELDS & AIRPORT TERMINAL SERVICES","PIPE LINES (NO NATURAL GAS)","TRANSPORTATION SERVICES","ARRANGEMENT OF TRANSPORTATION OF FREIGHT & CARGO","RADIOTELEPHONE COMMUNICATIONS","TELEPHONE COMMUNICATIONS (NO RADIOTELEPHONE)","TELEGRAPH & OTHER MESSAGE COMMUNICATIONS","RADIO BROADCASTING STATIONS","TELEVISION BROADCASTING STATIONS","CABLE & OTHER PAY TELEVISION SERVICES","COMMUNICATIONS SERVICES, NEC","ELECTRIC, GAS & SANITARY SERVICES","ELECTRIC SERVICES","NATURAL GAS TRANSMISSION","NATURAL GAS TRANSMISISON & DISTRIBUTION","NATURAL GAS DISTRIBUTION","ELECTRIC & OTHER SERVICES COMBINED","GAS & OTHER SERVICES COMBINED","WATER SUPPLY","SANITARY SERVICES","REFUSE SYSTEMS","HAZARDOUS WASTE MANAGEMENT","STEAM & AIR-CONDITIONING SUPPLY","COGENERATION SERVICES & SMALL POWER PRODUCERS","WHOLESALE-DURABLE GOODS","WHOLESALE-MOTOR VEHICLES & MOTOR VEHICLE PARTS & SUPPLIES","WHOLESALE-MOTOR VEHICLE SUPPLIES & NEW PARTS","WHOLESALE-FURNITURE & HOME FURNISHINGS","WHOLESALE-LUMBER & OTHER CONSTRUCTION MATERIALS","WHOLESALE-LUMBER, PLYWOOD, MILLWORK & WOOD PANELS","WHOLESALE-PROFESSIONAL & COMMERCIAL EQUIPMENT & SUPPLIES","WHOLESALE-COMPUTERS & PERIPHERAL EQUIPMENT & SOFTWARE","WHOLESALE-MEDICAL, DENTAL & HOSPITAL EQUIPMENT & SUPPLIES","WHOLESALE-METALS & MINERALS (NO PETROLEUM)","WHOLESALE-METALS SERVICE CENTERS & OFFICES","WHOLESALE-ELECTRICAL APPARATUS & EQUIPMENT, WIRING SUPPLIES","WHOLESALE-ELECTRICAL APPLIANCES, TV & RADIO SETS","WHOLESALE-ELECTRONIC PARTS & EQUIPMENT, NEC","WHOLESALE-HARDWARE & PLUMBING & HEATING EQUIPMENT & SUPPLIES","WHOLESALE-HARDWARE","WHOLESALE-MACHINERY, EQUIPMENT & SUPPLIES","WHOLESALE-CONSTRUCTION & MINING (NO PETRO) MACHINERY & EQUIP","WHOLESALE-INDUSTRIAL MACHINERY & EQUIPMENT","WHOLESALE-MISC DURABLE GOODS","WHOLESALE-JEWELRY, WATCHES, PRECIOUS STONES & METALS","WHOLESALE-DURABLE GOODS, NEC","WHOLESALE-PAPER & PAPER PRODUCTS","WHOLESALE-DRUGS, PROPRIETARIES & DRUGGISTS' SUNDRIES","WHOLESALE-APPAREL, PIECE GOODS & NOTIONS","WHOLESALE-GROCERIES & RELATED PRODUCTS","WHOLESALE-GROCERIES, GENERAL LINE","WHOLESALE-FARM PRODUCT RAW MATERIALS","WHOLESALE-CHEMICALS & ALLIED PRODUCTS","WHOLESALE-PETROLEUM BULK STATIONS & TERMINALS","WHOLESALE-PETROLEUM & PETROLEUM PRODUCTS (NO BULK STATIONS)","WHOLESALE-BEER, WINE & DISTILLED ALCOHOLIC BEVERAGES","WHOLESALE-MISCELLANEOUS NONDURABLE GOODS","RETAIL-BUILDING MATERIALS, HARDWARE, GARDEN SUPPLY","RETAIL-LUMBER & OTHER BUILDING MATERIALS DEALERS","RETAIL-MOBILE HOME DEALERS","RETAIL-DEPARTMENT STORES","RETAIL-VARIETY STORES","RETAIL-MISC GENERAL MERCHANDISE STORES","RETAIL-FOOD STORES","RETAIL-GROCERY STORES","RETAIL-CONVENIENCE STORES","RETAIL-AUTO DEALERS & GASOLINE STATIONS","RETAIL-AUTO & HOME SUPPLY STORES","RETAIL-APPAREL & ACCESSORY STORES","RETAIL-WOMEN'S CLOTHING STORES","RETAIL-FAMILY CLOTHING STORES","RETAIL-SHOE STORES","RETAIL-HOME FURNITURE, FURNISHINGS & EQUIPMENT STORES","RETAIL-FURNITURE STORES","RETAIL-RADIO, TV & CONSUMER ELECTRONICS STORES","RETAIL-COMPUTER & COMPUTER SOFTWARE STORES","RETAIL-RECORD & PRERECORDED TAPE STORES","RETAIL-EATING & DRINKING PLACES","RETAIL-EATING PLACES","RETAIL-MISCELLANEOUS RETAIL","RETAIL-DRUG STORES AND PROPRIETARY STORES","RETAIL-MISCELLANEOUS SHOPPING GOODS STORES","RETAIL-JEWELRY STORES","RETAIL-HOBBY, TOY & GAME SHOPS","RETAIL-NONSTORE RETAILERS","RETAIL-CATALOG & MAIL-ORDER HOUSES","RETAIL-RETAIL STORES, NEC","NATIONAL COMMERCIAL BANKS","STATE COMMERCIAL BANKS","COMMERCIAL BANKS, NEC","SAVINGS INSTITUTION, FEDERALLY CHARTERED","SAVINGS INSTITUTIONS, NOT FEDERALLY CHARTERED","FUNCTIONS RELATED TO DEPOSITORY BANKING, NEC","FEDERAL & FEDERALLY-SPONSORED CREDIT AGENCIES","PERSONAL CREDIT INSTITUTIONS","SHORT-TERM BUSINESS CREDIT INSTITUTIONS","MISCELLANEOUS BUSINESS CREDIT INSTITUTION","MORTGAGE BANKERS & LOAN CORRESPONDENTS","LOAN BROKERS","FINANCE LESSORS","ASSET-BACKED SECURITIES","FINANCE SERVICES","SECURITY & COMMODITY BROKERS, DEALERS, EXCHANGES & SERVICES","SECURITY BROKERS, DEALERS & FLOTATION COMPANIES","COMMODITY CONTRACTS BROKERS & DEALERS","INVESTMENT ADVICE","LIFE INSURANCE","ACCIDENT & HEALTH INSURANCE","HOSPITAL & MEDICAL SERVICE PLANS","FIRE, MARINE & CASUALTY INSURANCE","SURETY INSURANCE","TITLE INSURANCE","INSURANCE CARRIERS, NEC","INSURANCE AGENTS, BROKERS & SERVICE","REAL ESTATE","REAL ESTATE OPERATORS (NO DEVELOPERS) & LESSORS","OPERATORS OF NONRESIDENTIAL BUILDINGS","OPERATORS OF APARTMENT BUILDINGS","LESSORS OF REAL PROPERTY, NEC","REAL ESTATE AGENTS & MANAGERS (FOR OTHERS)","REAL ESTATE DEALERS (FOR THEIR OWN ACCOUNT)","LAND SUBDIVIDERS & DEVELOPERS (NO CEMETERIES)","BLANK CHECKS","OIL ROYALTY TRADERS","PATENT OWNERS & LESSORS","MINERAL ROYALTY TRADERS","REAL ESTATE INVESTMENT TRUSTS","INVESTORS, NEC","HOTELS, ROOMING HOUSES, CAMPS & OTHER LODGING PLACES","HOTELS & MOTELS","SERVICES-PERSONAL SERVICES","SERVICES-ADVERTISING","SERVICES-ADVERTISING AGENCIES","SERVICES-CONSUMER CREDIT REPORTING, COLLECTION AGENCIES","SERVICES-MAILING, REPRODUCTION, COMMERCIAL ART & PHOTOGRAPHY","SERVICES-DIRECT MAIL ADVERTISING SERVICES","SERVICES-TO DWELLINGS & OTHER BUILDINGS","SERVICES-MISCELLANEOUS EQUIPMENT RENTAL & LEASING","SERVICES-EQUIPMENT RENTAL & LEASING, NEC","SERVICES-EMPLOYMENT AGENCIES","SERVICES-HELP SUPPLY SERVICES","SERVICES-COMPUTER PROGRAMMING, DATA PROCESSING, ETC.","SERVICES-COMPUTER PROGRAMMING SERVICES","SERVICES-PREPACKAGED SOFTWARE","SERVICES-COMPUTER INTEGRATED SYSTEMS DESIGN","SERVICES-COMPUTER PROCESSING & DATA PREPARATION","SERVICES-COMPUTER RENTAL & LEASING","SERVICES-MISCELLANEOUS BUSINESS SERVICES","SERVICES-DETECTIVE, GUARD & ARMORED CAR SERVICES","SERVICES-PHOTOFINISHING LABORATORIES","SERVICES-TELEPHONE INTERCONNECT SYSTEMS","SERVICES-BUSINESS SERVICES, NEC","SERVICES-AUTOMOTIVE REPAIR, SERVICES & PARKING","SERVICES-AUTO RENTAL & LEASING (NO DRIVERS)","SERVICES-MISCELLANEOUS REPAIR SERVICES","SERVICES-MOTION PICTURE & VIDEO TAPE PRODUCTION","SERVICES-ALLIED TO MOTION PICTURE PRODUCTION","SERVICES-MOTION PICTURE & VIDEO TAPE DISTRIBUTION","SERVICES-ALLIED TO MOTION PICTURE DISTRIBUTION","SERVICES-MOTION PICTURE THEATERS","SERVICES-VIDEO TAPE RENTAL","SERVICES-AMUSEMENT & RECREATION SERVICES","SERVICES-RACING, INCLUDING TRACK OPERATION","SERVICES-MISCELLANEOUS AMUSEMENT & RECREATION","SERVICES-MEMBERSHIP SPORTS & RECREATION CLUBS","SERVICES-HEALTH SERVICES","SERVICES-OFFICES & CLINICS OF DOCTORS OF MEDICINE","SERVICES-NURSING & PERSONAL CARE FACILITIES","SERVICES-SKILLED NURSING CARE FACILITIES","SERVICES-HOSPITALS","SERVICES-GENERAL MEDICAL & SURGICAL HOSPITALS, NEC","SERVICES-MEDICAL LABORATORIES","SERVICES-HOME HEALTH CARE SERVICES","SERVICES-MISC HEALTH & ALLIED SERVICES, NEC","SERVICES-SPECIALTY OUTPATIENT FACILITIES, NEC","SERVICES-LEGAL SERVICES","SERVICES-EDUCATIONAL SERVICES","SERVICES-SOCIAL SERVICES","SERVICES-CHILD DAY CARE SERVICES","SERVICES-MEMBERSHIP ORGANIZATIONS","SERVICES-ENGINEERING, ACCOUNTING, RESEARCH, MANAGEMENT","SERVICES-ENGINEERING SERVICES","SERVICES-COMMERCIAL PHYSICAL & BIOLOGICAL RESEARCH","SERVICES-TESTING LABORATORIES","SERVICES-MANAGEMENT SERVICES","SERVICES-MANAGEMENT CONSULTING SERVICES","SERVICES-FACILITIES SUPPORT MANAGEMENT SERVICES","AMERICAN DEPOSITARY RECEIPTS","FOREIGN GOVERNMENTS","SERVICES-SERVICES, NEC","INTERNATIONAL AFFAIRS","NON-OPERATING ESTABLISHMENTS"]

        self.major_industry_mapping = {
            "01": "Agricultural Production Crops",
            "02": "Agricultural Production Livestock And Animal Specialties",
            "07": "Agricultural Services",
            "08": "Forestry",
            "09": "Fishing, Hunting, And Trapping",
            "10": "Metal Mining",
            "12": "Coal Mining",
            "13": "Oil And Gas Extraction",
            "14": "Mining And Quarrying Of Nonmetallic Minerals, Except Fuels",
            "15": "Building Construction General Contractors And Operative Builders",
            "16": "Heavy Construction Other Than Building Construction Contractors",
            "17": "Construction Special Trade Contractors",
            "20": "Food And Kindred Products",
            "21": "Tobacco Products",
            "22": "Textile Mill Products",
            "23": "Apparel And Other Finished Products Made From Fabrics And Similar Materials",
            "24": "Lumber And Wood Products, Except Furniture",
            "25": "Furniture And Fixtures",
            "26": "Paper And Allied Products",
            "27": "Printing, Publishing, And Allied Industries",
            "28": "Chemicals And Allied Products",
            "29": "Petroleum Refining And Related Industries",
            "30": "Rubber And Miscellaneous Plastics Products",
            "31": "Leather And Leather Products",
            "32": "Stone, Clay, Glass, And Concrete Products",
            "33": "Primary Metal Industries",
            "34": "Fabricated Metal Products, Except Machinery And Transportation Equipment",
            "35": "Industrial And Commercial Machinery And Computer Equipment",
            "36": "Electronic And Other Electrical Equipment And Components, Except Computer Equipment",
            "37": "Transportation Equipment",
            "38": "Measuring, Analyzing, And Controlling Instruments; Photographic, Medical And Optical Goods; Watches And Clocks",
            "39": "Miscellaneous Manufacturing Industries",
            "40": "Railroad Transportation",
            "41": "Local And Suburban Transit And Interurban Highway Passenger Transportation",
            "42": "Motor Freight Transportation And Warehousing",
            "43": "United States Postal Service",
            "44": "Water Transportation",
            "45": "Transportation By Air",
            "46": "Pipelines, Except Natural Gas",
            "47": "Transportation Services",
            "48": "Communications",
            "49": "Electric, Gas, And Sanitary Services",
            "50": "Wholesale Trade-durable Goods",
            "51": "Wholesale Trade-non-durable Goods",
            "52": "Building Materials, Hardware, Garden Supply, And Mobile Home Dealers",
            "53": "General Merchandise Stores",
            "54": "Food Stores",
            "55": "Automotive Dealers And Gasoline Service Stations",
            "56": "Apparel And Accessory Stores",
            "57": "Home Furniture, Furnishings, And Equipment Stores",
            "58": "Eating And Drinking Places",
            "59": "Miscellaneous Retail",
            "60": "Depository Institutions",
            "61": "Non-depository Credit Institutions",
            "62": "Security And Commodity Brokers, Dealers, Exchanges, And Services",
            "63": "Insurance Carriers",
            "64": "Insurance Agents, Brokers, And Service",
            "65": "Real Estate",
            "67": "Holding And Other Investment Offices",
            "70": "Hotels, Rooming Houses, Camps, And Other Lodging Places",
            "72": "Personal Services",
            "73": "Business Services",
            "75": "Automotive Repair, Services, And Parking",
            "76": "Miscellaneous Repair Services",
            "78": "Motion Pictures",
            "79": "Amusement And Recreation Services",
            "80": "Health Services",
            "81": "Legal Services",
            "82": "Educational Services",
            "83": "Social Services",
            "84": "Museums, Art Galleries, And Botanical And Zoological Gardens",
            "86": "Membership Organizations",
            "87": "Engineering, Accounting, Research, Management, And Related Services",
            "88": "Private Households",
            "89": "Miscellaneous Services",
            "91": "Executive, Legislative, And General Government, Except Finance",
            "92": "Justice, Public Order, And Safety",
            "93": "Public Finance, Taxation, And Monetary Policy",
            "94": "Administration Of Human Resource Programs",
            "95": "Administration Of Environmental Quality And Housing Programs",
            "96": "Administration Of Economic Programs",
            "97": "National Security And International Affairs",
            "99": "Nonclassifiable Establishments"
            }

        # property name of IS_PARTIAL_OWNER_OF
        self.isPartialOwnerOfOwnerIssuerPropertyKeys = ['issuerName', 'issuerUrl', 'issuerCik', 'issuerCikUrl', 'transactionDate', 'ownershipValue']
        # property name of IS_PARTIAL_OWNER_OF
        self.personIsPartialOwnerOfPropertyKeys = ['issuerName', 'issuerUrl', 'issuerCik', 'issuerCikUrl', 'wikipediaPage', 'mailingAddress', 'transactionDate', 'ownershipValue']

        # property name of Person
        self.personalPropertyKeys = ['name', 'cik', 'wikipediaPage', 'mailingAddress']

        # property names of IS_DIRECTOR_OF
        self.personalIsDirectorOfPropertyKeys = ['transactionDate', 'positions']

        # personal realtionship keys
        self.personalRelationshipKeys = ['IS_DIRECTOR_OF', 'HAS_INSTRUMENTS_OF']

        # property name of HAS_INSTRUMENTS_OF
        self.hasInstrumentsOfOwnerIssuerPropertyKeys = ['securityName', 'numberOfSecuritiesOwned', 'directOrIndirectOwnership', 'transactionType', 'form', 'transactionDate', 'acquistionOrDisposition']

        # company Owner Issuer Info List keys
        self.companyIssuerInfoKeys = ['personalCompanyInfo', 'isDirectorOf', 'hasInstrumentsOf', 'personOwnCompany']

        # personal Info List keys
        self.personalInfoKeys = ['personalProperty', 'isDirectorOf', 'hasInstrumentsOf']

        # property names of IS_PARTIAL_OWNER_OF
        self.isPartialOwnerOfPropertyName = ['transactionDate', 'ownershipValue']

        # property names of HAS_INSTRUMENTS_OF
        self.hasInstrumentsOfPropertyName = ['securityName', 'numberOfSecuritiesOwned', 'directOrIndirectOwnership', 'transactionType', 'form', 'transactionDate', 'acquistionOrDisposition']

        # country property keys
        self.countryPropertyKeys = ['secCode', 'secName', 'isoAlpha2Code', 'isoAlpha3Code', 'isoM49Code', 'isoName']

        # exchange property keys
        self.exchangePropertyKeys = ['ticker', 'name', 'city', 'country', 'isoAlpha2Code']

        # secFilings property keys
        self.secFilingsPropertyKeys = ['cik', 'filingsCategory', 'filingsAmount', 'fiscalYear', 'secFileNumber']

        # sic property keys
        self.sicPropertyKeys = ['sicCode', 'office', 'name']

        # state property keys
        self.statePropertyKeys = ['code', 'name']

        # company property keys
        self.companyPropertyKeys = ['name', 'ticker', 'cik', 'irsNumber', 'fiscalYearEnd', 'businessAddress', 'mailingAddress', 'businessSegments', 'productServices']

        # company relationship keys
        self.companyRelationshipKeys = ['HAS_STATE_LOCATION', 'HAS_STATE_OF_INCORPORATION', 'HAS_SEC_FILINGS', 'HAS_EXCHANGE_MARKET', 'IS_PARTIAL_OWNER_OF', 'HAS_INSTRUMENTS_OF', 'BELONGS_TO_INDUSTRY_OF']
     
        # state code name pair
        self.statePairList = []

        # country code name pair
        self.countryPairList = []

        # sic code name pair
        self.sicPairList = []

        # init graph
        self.graph = Neo4jGraph()

    # get Sic code name pair list
    def getSicPairList(self):

        # loop through Sic code
        for j in range(len(self.sicCode)):

            # set sic property key value pair
            sicPair = {
                self.sicPropertyKeys[0] : self.sicCode[j], self.sicPropertyKeys[1] : self.sicOffice[j], self.sicPropertyKeys[2] : self.sicName[j]
            }
            # {
            #  'sicCode':   ,
            #  'office':    ,
            #  'name':
            # }


            # append to sic pair list
            self.sicPairList.append(sicPair)

        return self.sicPairList

    def getEventPairList(self):
        with open(self.eventJsonPath, 'r', encoding='utf-8') as jsonFile:
            events = json.load(jsonFile)
            # keep only the dates, geo, event type and text
            events = [{"id":event["event_id"], 
                       'description': event['text'], 
                       'date': str(event['date']), 
                       'geo': str(event['geo']), 
                       'event_type': event['event_type']} for event in events]
            return events

    def getNewsPairList(self):
        news_list = []
        with open(self.NewsMetadataPath, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                print(record["news_id"], record["Article_title"])
                entity = {
                    'news_id': str(record["news_id"]),
                    'title': record["Article_title"].replace('"', '\\"'),
                    'text': record["Article"].replace('"', '\\"'),
                    'date': record["Date"],
                    'url': record["Url"]}
                news_list.append(entity)
        return news_list

    # get contents from txt file
    def getContentsFromTxtFile(self, filename):

        # read security exchange name txt file
        with open(filename, encoding='utf-8') as txtReader: 

            # read contents
            return txtReader.readlines()

    # generate exchange name file
    def generateSecurityExchangeNameFile(self):
        # get security exchange name file
        securityExchangeNameList = self.getContentsFromTxtFile(self.securityExchangeNamePath)

        with open(self.exchangeEntityFilename, 'w', encoding='UTF8', newline='') as securityExchangeNameWrite:
            # create csv writer
            csvwriter = csv.writer(securityExchangeNameWrite)
            # write the header
            csvwriter.writerow(self.exchangePropertyKeys)
        
            # loop through contents
            for i, line in enumerate(securityExchangeNameList):
                line = line.strip()
                print(line)
                
                semiColonArray = line.split(';')
                commaArray = semiColonArray[1].split(',')
                bracketArray = commaArray[len(commaArray)-1].split('(')

                name = semiColonArray[0].strip()
                # print(name)

                city = ""
                for i in range(len(commaArray)-1):
                    city += commaArray[i]
                city = city.strip()
                # print(city)

                country = bracketArray[0].strip()
                # print(country)

                isoAlpha2Code = bracketArray[1].replace(')','').strip()
                # print(isoAlpha2Code)

                ticker = 'NONE'
                # get ticker
                for set in self.securityExchangeTickers:

                    if name.startswith(set):
                        if set == 'NYSE':
                            if name == 'NYSE ARCA'  and isoAlpha2Code == 'US':
                                ticker = set
                                break
                        elif set == 'NASDAQ':
                            if name == 'NASDAQ PSX' and isoAlpha2Code == 'US':
                                ticker = set
                                break
                        else:
                            ticker = set
                            break
                # exchange pair
                # exchangePair = {
                #                     self.exchangePropertyKeys[0] : ticker,
                #                     self.exchangePropertyKeys[1] : name,
                #                     self.exchangePropertyKeys[2] : city,
                #                     self.exchangePropertyKeys[3] : country,
                #                     self.exchangePropertyKeys[4] : isoAlpha2Code
                #                 }
                data = []
                pair = []
                pair.append(ticker)
                pair.append(name)
                pair.append(city)
                pair.append(country)
                pair.append(isoAlpha2Code)
                data.append(pair)
                # write the data
                csvwriter.writerows(data)

    # get exchange pair
    def getExchangePair(self, exchangeTicker):

        for exchangePair in self.exchangePairList:
            if exchangeTicker.upper() == exchangePair['ticker']:
                # exchange pair
                exchangePair = {
                                self.exchangePropertyKeys[0] : exchangePair[self.exchangePropertyKeys[0]],
                                self.exchangePropertyKeys[1] : exchangePair[self.exchangePropertyKeys[1]],
                                self.exchangePropertyKeys[2] : exchangePair[self.exchangePropertyKeys[2]],
                                self.exchangePropertyKeys[3] : exchangePair[self.exchangePropertyKeys[3]],
                                self.exchangePropertyKeys[4] : exchangePair[self.exchangePropertyKeys[4]]
                                }

                # return exchange pair list
                return exchangePair        

        # exchange pair
        exchangePair = {
                            self.exchangePropertyKeys[0] : exchangeTicker,
                            self.exchangePropertyKeys[1] : '',
                            self.exchangePropertyKeys[2] : '',
                            self.exchangePropertyKeys[3] : '',
                            self.exchangePropertyKeys[4] : ''
                        }
        return exchangePair

    # get country code name pair list
    def getCountryPairList(self):

        # loop through country code
        for j in range(len(self.isoAlpha2Code)):
            
            # set country property key value pair
            countryPair = {
                self.countryPropertyKeys[0] : self.isoAlpha2Code[j], self.countryPropertyKeys[1] : self.isoName[j],
                self.countryPropertyKeys[2] : self.isoAlpha2Code[j], self.countryPropertyKeys[3] : self.isoAlpha3Code[j],
                self.countryPropertyKeys[4] : self.isoM49Code[j], self.countryPropertyKeys[5] : self.isoName[j]
            }

            # append to country pair list
            self.countryPairList.append(countryPair)

        return self.countryPairList

    # get state code name pair
    def getStatePairList(self):

        # loop through country code
        for j in range(len(self.stateCode)):
            
            # set state property key value pair
            statePair = {
                self.statePropertyKeys[0] : self.stateCode[j], self.statePropertyKeys[1] : self.stateName[j]
            }

            # append to state pair list
            self.statePairList.append(statePair)

        return self.statePairList

    # get txt 10k file contents
    def get10kFileContents(self):

        # open 10k txt file
        with open(self.txt10kfilename) as txtReadFile:

            # read file contents
            return txtReadFile.readlines()

    # get txt 10k file
    def get10kFileText(self):

        # open 10k txt file
        with open(self.txt10kfilename) as txtReadFile:

            # read file contents
            contents = txtReadFile.readlines()
            
            # print(f"The encoding of txt file {self.txt10kfilename} is: {txtReadFile.encoding}")

            # define the text to store the text format of contents
            text = ""

            # loop through file contents
            for row in contents:

                # concatenate rows
                text += row

        # return text format of txt file
        return text

    # get url response from sec edgar
    def getUrlResponse(self, url, param=None):
        # get content
        return requests.get(url=url, params=param, allow_redirects=True, headers={"user-agent":"Rocio Jimenez jimenez.r.aa@m.titech.ac.jp"})

    # generate sec company home page url
    def generateCompanyHomepageUrl(self, cik):

        # sec home page url
        sechomepageUrl = self.sec_company_homepage_base_url + cik + self.sec_company_homepage_param_owner_url

        # show the url to user
        # print(f"company sec homepage url: {sechomepageUrl}")

        # return home page url
        return sechomepageUrl

    # generate sec company 10k filename url
    def generateCompany10kFilenameUrl(self, cik, txt10kfilename):

        # sec company 10k filename url
        self.sec_company_10k_filename_url = self.edgar_data_endpoint + cik + '/' + txt10kfilename

        # show the url to user
        print(f"company sec company 10k filename url: {self.sec_company_10k_filename_url}")

        # return sec company 10k filename url
        return self.sec_company_10k_filename_url

    # get wikipedia homepage of personal
    def getPersonWikipediaByGoogle(self, personalName):

        googelUrl = self.googleSearchEndpoint + personalName
        print(googelUrl)

        # get response from the web
        wikipediaResponse = self.getUrlResponse(googelUrl)

        # BeautifulSoup
        wikipediaSoup = BeautifulSoup(wikipediaResponse.content, 'lxml')
        print(wikipediaSoup)

        # wikipedia
        divGoogle = wikipediaSoup.find('div', attrs={"id": "search"})
        divResult = wikipediaSoup.find('div', attrs={"class": "yuRUbf"})

        divGoogle.find_all()

    # get company CIK and 10k filename
    def getCompanyCikAnd10kFilename(self):

        # read csv file
        with open(self.company_cik_ticker_10kfilename, encoding='utf-8') as csvReadFile:

            # csv reader
            csvReader = csv.reader(csvReadFile, delimiter=',')

            # define company cik 10k filename list
            cikTicker10kFilenameList = []

            # loop through the csv file
            for csvRowInd, row in enumerate(csvReader):

                # if it is the csv file header
                if csvRowInd == 0:

                    # print the header name
                    print(f'Csv file header names are: {", ".join(row)}')

                # if it is the csv content
                else:
                    # cik ticker 10k filename tuple
                    cikTicker10kFilenameTuple = (row[0], row[1], row[2])

                    # append tuple to list
                    cikTicker10kFilenameList.append(cikTicker10kFilenameTuple)

                    # print the company cik and 10k filename
                    # print(f"Csv file company cik and 10k filenames are: {row[0]}, {row[1]}")

        # return the company cik 10k filename dict
        return cikTicker10kFilenameList
        

    # create sub company entity json file
    def createCompanyHasCompanyJsonFile(self, cik):

        # sub company entity json file
        subCompanyFilename = self.entityCompanyCikPath + cik + self.jsonSubCompanyExtensionName

        if exists(subCompanyFilename):
            return

        entitySubCompanyIsPartialOwnerOfJsonDataList = []
        entitySubCompanyHasInstrumentsOfJsonDataList = []

        # get company owner html data
        ownerResponse = self.getCompanyOwnerHtmlData(cik)

        # BeautifulSoup
        ownerSoup = BeautifulSoup(ownerResponse, 'lxml')
        # print(ownerSoup)

        # owner company part
        tableCompany = ownerSoup.find('table', attrs={"border": "1"})
        # print(tableCompany)

        if not tableCompany:
            return

        # owner company tr
        tableOwnerCompanyTrs = tableCompany.find_all('tr')
        # print(tableCompanyTrs)

        # get company table
        if len(tableOwnerCompanyTrs) > 1:
            for tr_idx, tr in enumerate(tableOwnerCompanyTrs):
                if tr_idx > 0:
                    tableCompanyTds = tr.find_all('td')
                    # sub company name
                    subCompanyName = tableCompanyTds[0].find('a').text.strip()

                    subCompanyUrl = self.secUrl + tableCompanyTds[0].find('a')['href']
                    print(subCompanyUrl)
                    # sub company cik name
                    subCompanyCik = tableCompanyTds[1].find('a').text.strip()
                    # print(subCompanyCik)
                    # sub company cik url
                    subCompanyCikUrl = self.secUrl + tableCompanyTds[1].find('a')['href']
                    print(subCompanyCikUrl)
                    # sub company transaction date
                    subCompanyTransactionDate = tableCompanyTds[2].text.strip()
                    # print(subCompanyTransactionDate)
                    ownershipValue = tableCompanyTds[3].text.strip()
                    # print(ownershipValue)

                    # IS_PARTIAL_OWNER_OF json data
                    entitySubCompanyIsPartialOwnerOfJsonData = {
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[0] : subCompanyName,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[1] : subCompanyUrl,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[2] : subCompanyCik,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[3] : subCompanyCikUrl,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[4] : subCompanyTransactionDate,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[5] : ownershipValue
                    }
                    entitySubCompanyIsPartialOwnerOfJsonDataList.append(entitySubCompanyIsPartialOwnerOfJsonData)

        # owner stock part
        tableStock = ownerSoup.find('table', attrs={"id": "transaction-report"})
        # print(tableStock)

        # owner stock tr
        tableOwnerStockTrs = tableStock.find_all('tr')
        # print(tableOwnerStockTrs)

        # get stock table
        if len(tableOwnerStockTrs) > 1:

            # loop through each company
            for isPartialOwnerOfIssuerCik in entitySubCompanyIsPartialOwnerOfJsonDataList:

                # loop through each company stock and find the relative company stock
                for tr_idx, tr in enumerate(tableOwnerStockTrs):

                    # start from the second row
                    if tr_idx > 0:
                        tableCompanyTds = tr.find_all('td')
                        issuerCik = tableCompanyTds[10].text.strip()
                        # print(issuerCik)

                        # find the relative company
                        if isPartialOwnerOfIssuerCik['issuerCik'] == issuerCik:
                            # sub company name
                            securityName = tableCompanyTds[11].text.strip()

                            numberOfSecuritiesOwned = tableCompanyTds[8].text.strip()
                            # print(numberOfSecuritiesOwned)
                            directOrIndirectOwnership = tableCompanyTds[6].text.strip()
                            # print(directOrIndirectOwnership)
                            transactionType = tableCompanyTds[5].text.strip()
                            # print(transactionType)
                            form = tableCompanyTds[4].text.strip()
                            # print(form)
                            transactionDate = tableCompanyTds[1].text.strip()
                            # print(transactionDate)
                            acquistionOrDisposition = tableCompanyTds[0].text.strip()
                            # print(acquistionOrDisposition)

                            # HAS_INSTRUMENTS_OF json data
                            entitySubCompanyHasInstrumentsOfJsonData = {
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[0] : securityName,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[1] : numberOfSecuritiesOwned,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[2] : directOrIndirectOwnership,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[3] : transactionType,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[4] : form,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[5] : transactionDate,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[6] : acquistionOrDisposition
                            }
                            entitySubCompanyHasInstrumentsOfJsonDataList.append(entitySubCompanyHasInstrumentsOfJsonData)
                            break

        entitySubCompanyJsonData = {
            self.companyRelationshipKeys[4] : entitySubCompanyIsPartialOwnerOfJsonDataList,
            self.companyRelationshipKeys[5] : entitySubCompanyHasInstrumentsOfJsonDataList
        }
        
        # create entity json file
        with open(subCompanyFilename, 'w', encoding='utf-8') as entitySubCompany_json_writer:
            json.dump(entitySubCompanyJsonData, entitySubCompany_json_writer, indent=4, ensure_ascii=False)

    # get company issuer info list
    def createCompanyHasPersonJsonFile(self, cik):
        # person json file
        personFilename = self.entityCompanyCikPath + cik + self.jsonHasPersonExtensionName

        if exists(personFilename):
            return

        entityPersonIsPartialOwnerOfJsonDataList = []
        entityPersonHasInstrumentsOfJsonDataList = []

        # get company issuer html data
        issuerResponse = self.getCompanyIssuerHtmlData(cik)

        # BeautifulSoup
        issuerSoup = BeautifulSoup(issuerResponse, 'lxml')
        # print(issuerSoup)

        # issuer company part
        tableCompany = issuerSoup.find('table', attrs={"border": "1"})

        # print(tableCompany)
        # has not any IS_PARTIAL_OWNER_OF relationship
        if not tableCompany:
            return

        # issuer company tr
        tableIssuerCompanyTrs = tableCompany.find_all('tr')
        # print(tableCompanyTrs)

        # get company table
        if len(tableIssuerCompanyTrs) > 1:
            for tr_idx, tr in enumerate(tableIssuerCompanyTrs):
                if tr_idx > 0:
                    tablePersonTds = tr.find_all('td')
                    # personal name
                    personalName = tablePersonTds[0].find('a').text.strip()

                    personalUrl = self.secUrl + tablePersonTds[0].find('a')['href']
                    # print(personalUrl)
                    # person mail address
                    personalMailAddress = self.getPersonMailAddress(personalUrl, cik)

                    personalWikiUrl = self.googleSearchEndpoint + personalName.replace(' ', '+')
                    print(personalWikiUrl)

                    # personal cik
                    personalCik = tablePersonTds[1].find('a').text.strip()
                    # print(personalCik)
                    # personal cik url
                    personalCikUrl = self.secUrl + tablePersonTds[1].find('a')['href']
                    print(personalCikUrl)
                    # sub company transaction date
                    personalTransactionDate = tablePersonTds[2].text.strip()
                    # print(personalTransactionDate)
                    issuershipValue = tablePersonTds[3].text.strip()

                    # IS_PARTIAL_OWNER_OF json data
                    entityPersonIsPartialOwnerOfJsonData = {
                        self.personIsPartialOwnerOfPropertyKeys[0] : personalName,
                        self.personIsPartialOwnerOfPropertyKeys[1] : personalUrl,
                        self.personIsPartialOwnerOfPropertyKeys[2] : personalCik,
                        self.personIsPartialOwnerOfPropertyKeys[3] : personalCikUrl,
                        self.personIsPartialOwnerOfPropertyKeys[4] : personalWikiUrl,
                        self.personIsPartialOwnerOfPropertyKeys[5] : personalMailAddress,
                        self.personIsPartialOwnerOfPropertyKeys[6] : personalTransactionDate,
                        self.personIsPartialOwnerOfPropertyKeys[7] : issuershipValue
                    }
                    entityPersonIsPartialOwnerOfJsonDataList.append(entityPersonIsPartialOwnerOfJsonData)

        # issuer stock part
        tableStock = issuerSoup.find('table', attrs={"id": "transaction-report"})
        # print(tableStock)

        # issuer stock tr
        tableIssuerStockTrs = tableStock.find_all('tr')
        # print(tableIssuerStockTrs)

        # get stock table
        if len(tableIssuerStockTrs) > 1:

            # loop through each company
            for personalProperty in entityPersonIsPartialOwnerOfJsonDataList:

                # loop through each company stock and find the relative company stock
                for tr_idx, tr in enumerate(tableIssuerStockTrs):

                    # start from the second row
                    if tr_idx > 0:
                        # table personal info
                        tablePersonTds = tr.find_all('td')

                        # issuer cik
                        issuerCik = tablePersonTds[10].text.strip()
                        # print(issuerCik)
                        
                        # find the relative personal
                        if personalProperty['issuerCik'] == issuerCik:
                            # sucurity name
                            securityName = tablePersonTds[11].text.strip()

                            numberOfSecuritiesOwned = tablePersonTds[8].text.strip()
                            # print(numberOfSecuritiesOwned)
                            directOrIndirectIssuership = tablePersonTds[6].text.strip()
                            # print(directOrIndirectIssuership)
                            transactionType = tablePersonTds[5].text.strip()
                            # print(transactionType)
                            form = tablePersonTds[4].text.strip()
                            # print(form)
                            transactionDate = tablePersonTds[1].text.strip()
                            # print(transactionDate)
                            acquistionOrDisposition = tablePersonTds[0].text.strip()
                            # print(acquistionOrDisposition)

                            # HAS_INSTRUMENTS_OF json data
                            entityPersonHasInstrumentsOfJsonData = {
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[0] : securityName,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[1] : numberOfSecuritiesOwned,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[2] : directOrIndirectIssuership,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[3] : transactionType,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[4] : form,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[5] : transactionDate,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[6] : acquistionOrDisposition
                            }
                            entityPersonHasInstrumentsOfJsonDataList.append(entityPersonHasInstrumentsOfJsonData)
                            break

        entityPersonJsonData = {
            self.personalRelationshipKeys[0] : entityPersonIsPartialOwnerOfJsonDataList,
            self.personalRelationshipKeys[1] : entityPersonHasInstrumentsOfJsonDataList
        }
        
        # create entity json file
        with open(personFilename, 'w', encoding='utf-8') as entityPerson_json_writer:
            json.dump(entityPersonJsonData, entityPerson_json_writer, indent=4, ensure_ascii=False)

    # get company issuer info list
    def getPersonMailAddress(self, personalUrl, mainCik):

        personCik = personalUrl.split('=')[2]        

        # person entity json file
        entityPersonPath = self.entityCompanyCikPath + 'personHasCompany/'

        if not exists(entityPersonPath):
            os.makedirs(entityPersonPath)

        # sub company entity json file
        personCompanyFilename = entityPersonPath + personCik + self.jsonExtensionName

        personalMailAddress = ""

        if exists(personCompanyFilename):
            return personalMailAddress

        # personal company info list
        entityPersonIsDirectorOfJsonDataList = []
        entityPersonHasInstrumentsOfJsonDataList = []

        # get personal company html data
        personalComapnyResponse = self.getPersonalCompanyHtmlData(personalUrl)

        # BeautifulSoup
        personalComapnySoup = BeautifulSoup(personalComapnyResponse, 'lxml')
        # print(issuerSoup)

        # personal mail address part
        tableMailAddress = personalComapnySoup.find('table', attrs={"cellspacing": "16"})

        # mail address
        if tableMailAddress:
            # mail address td
            tableMailAddressTds = tableMailAddress.find_all('td')
            if len(tableMailAddressTds) > 0:
                for td_idx, td in enumerate(tableMailAddressTds):
                    if td_idx > 0:
                        for str in td.text.split('\n')[2:]:
                            personalMailAddress += str + " "
                personalMailAddress = personalMailAddress.rstrip()
                print(personalMailAddress)

        # owner company part
        tableCompany = personalComapnySoup.find('table', attrs={"border": "1"})

        # print(tableCompany)
        # has not any IS_PARTIAL_OWNER_OF relationship
        if not tableCompany:
            return personalMailAddress

        # owner company tr
        tableOwnerCompanyTrs = tableCompany.find_all('tr')
        # print(tableCompanyTrs)

        # get company table
        if len(tableOwnerCompanyTrs) > 1:
            for tr_idx, tr in enumerate(tableOwnerCompanyTrs):                
                if tr_idx > 0:
                    tableCompanyTds = tr.find_all('td')
                    # sub company name
                    subCompanyName = tableCompanyTds[0].find('a').text.strip()

                    subCompanyUrl = self.secUrl + tableCompanyTds[0].find('a')['href']
                    print(subCompanyUrl)
                    # sub company cik name
                    subCompanyCik = tableCompanyTds[1].find('a').text.strip()
                    # print(subCompanyCik)

                    # don't get info if it is the same company
                    if subCompanyCik == mainCik:
                        continue

                    # sub company cik url
                    subCompanyCikUrl = self.secUrl + tableCompanyTds[1].find('a')['href']
                    print(subCompanyCikUrl)
                    # sub company transaction date
                    subCompanyTransactionDate = tableCompanyTds[2].text.strip()
                    # print(subCompanyTransactionDate)
                    ownershipValue = tableCompanyTds[3].text.strip()
                    # print(ownershipValue)

                    # IS_DIRECTOR_OF json data
                    entityPersonIsDirectorOfJsonData = {
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[0] : subCompanyName,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[1] : subCompanyUrl,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[2] : subCompanyCik,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[3] : subCompanyCikUrl,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[4] : subCompanyTransactionDate,
                        self.isPartialOwnerOfOwnerIssuerPropertyKeys[5] : ownershipValue
                    }
                    entityPersonIsDirectorOfJsonDataList.append(entityPersonIsDirectorOfJsonData)

        # owner stock part
        tableStock = personalComapnySoup.find('table', attrs={"id": "transaction-report"})
        # print(tableStock)

        # owner stock tr
        tableOwnerStockTrs = tableStock.find_all('tr')
        # print(tableOwnerStockTrs)

        # get stock table
        if len(tableOwnerStockTrs) > 1:

            # loop through each company
            for personCompanyPropertyPair in entityPersonIsDirectorOfJsonDataList:

                # loop through each company stock and find the relative company stock
                for tr_idx, tr in enumerate(tableOwnerStockTrs):

                    # start from the second row
                    if tr_idx > 0:
                        tableCompanyTds = tr.find_all('td')
                        issuerCik = tableCompanyTds[10].text.strip()
                        # print(issuerCik)

                        # find the relative company
                        if personCompanyPropertyPair['issuerCik'] == issuerCik:

                            # sub company name
                            securityName = tableCompanyTds[11].text.strip()

                            numberOfSecuritiesOwned = tableCompanyTds[8].text.strip()
                            # print(numberOfSecuritiesOwned)
                            directOrIndirectOwnership = tableCompanyTds[6].text.strip()
                            # print(directOrIndirectOwnership)
                            transactionType = tableCompanyTds[5].text.strip()
                            # print(transactionType)
                            form = tableCompanyTds[4].text.strip()
                            # print(form)
                            transactionDate = tableCompanyTds[1].text.strip()
                            # print(transactionDate)
                            acquistionOrDisposition = tableCompanyTds[0].text.strip()
                            # print(acquistionOrDisposition)

                            # HAS_INSTRUMENTS_OF json data
                            entityPersonHasInstrumentsOfJsonData = {
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[0] : securityName,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[1] : numberOfSecuritiesOwned,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[2] : directOrIndirectOwnership,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[3] : transactionType,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[4] : form,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[5] : transactionDate,
                                    self.hasInstrumentsOfOwnerIssuerPropertyKeys[6] : acquistionOrDisposition
                            }
                            entityPersonHasInstrumentsOfJsonDataList.append(entityPersonHasInstrumentsOfJsonData)
                            break
        if len(entityPersonIsDirectorOfJsonDataList) > 0:

            entityPersonJsonData = {
                self.personalRelationshipKeys[0] : entityPersonIsDirectorOfJsonDataList,
                self.personalRelationshipKeys[1] : entityPersonHasInstrumentsOfJsonDataList
            }
            
            # create entity json file
            with open(personCompanyFilename, 'w', encoding='utf-8') as entityPerson_json_writer:
                json.dump(entityPersonJsonData, entityPerson_json_writer, indent=4, ensure_ascii=False)

        # return personal mail address
        return personalMailAddress

    # get exchange pair list
    def getExchangePairList(self):

        with open(self.exchangeEntityFilename, encoding='utf-8') as csv_file:
            csv_exchangeCsvReader = csv.reader(csv_file, delimiter=',')
            exchangePairList = []
            for idx, row in enumerate(csv_exchangeCsvReader):
                if idx > 0:
                    if row[0] == 'NASDAQ' or row[0] == 'NYSE':
                        exchangePair = {
                            self.exchangePropertyKeys[0] : row[0],
                            self.exchangePropertyKeys[1] : row[1],
                            self.exchangePropertyKeys[2] : row[2],
                            self.exchangePropertyKeys[3] : row[3],
                            self.exchangePropertyKeys[4] : row[4]
                        }
                        exchangePairList.append(exchangePair)
            return exchangePairList


    # create exchange nodes
    def createExchangeNodes(self):

        self.exchangePairList = self.getExchangePairList()
        print(self.exchangePairList)

        # set country entity
        entity = { 'Exchange' : self.exchangePairList }

        # create Country nodes
        self.graph.createNodes(entity)

    # create country nodes
    def createCountryNodes(self):

        # country code pair
        countryPairList = self.getCountryPairList()

        # set country entity
        entity = { 'Country' : countryPairList }

        # create Country nodes
        self.graph.createNodes(entity)

    # create sic nodes
    def createSicNodes(self):

        # sic code pair
        sicPairList = self.getSicPairList()

        # set sic entity
        entity = { 'StandardIndustrialClassification' : sicPairList }

        # create sic nodes
        self.graph.createNodes(entity)
    
    def createMajorIndustryTriples(self):

        # sic code pair
        sicPairList = self.getSicPairList()

        for sic in sicPairList:
            # subject: sic
            subject = { 'StandardIndustrialClassification' : { 'sicCode' : sic['sicCode'] } }
            # predicate: BELONGS_TO_MAJOR_INDUSTRY
            predicate = 'BELONGS_TO_MAJOR_INDUSTRY'
            # object: major industry

            major_industry_code = sic['sicCode'][:2] if len(sic['sicCode']) == 4 else '0'+sic['sicCode'][:1]

            object = { 'MajorIndustry' : { 'sicCode':major_industry_code,
                                           'name' : self.major_industry_mapping[major_industry_code] } }
            self.graph.createTriple(subject, predicate, object)

    # create event nodes
    def createEventNodes(self):
        """
        event = {
                    "text": "Elizabeth II dies at the age of 96, and is succeeded by Charles III.",
                    "date": [
                    "2022-09-08 00:00:00",
                    "2022-09-08 23:59:59"
                    ],
                    "event_type": [
                    "political.leadership_changes.power_transfers",
                    " political.leadership_changes.leader_deaths_or_assassinations"
                    ],
                    "geo": [],
                    "event_id": "2022_25"
                }
        """

        event_pair_list = self.getEventPairList()

        # set event entity, we dont include event types here
        entity = { 'Event' : [{k: v for k, v in event.items() if k != "event_type"} for event in event_pair_list] }

        # create nodes
        self.graph.createNodes(entity)

        # now add the event category nodes and relationships (2-level taxonomy)
        for event in event_pair_list:
            event_id = event['id']
             
            for category in event['event_type']:
                # split category by fullstops and strip spaces
                levels = [c.strip() for c in category.split('.')]
                # create relationships for each level
                # subject: event
                subject = { 'Event' : { 'id' : event_id } }
                # predicate: EVENT_HAS_CATEGORY
                predicate = 'EVENT_HAS_CATEGORY'
                # object: lowest category
                subcategory = { 'EventCategory' : { 'name' : levels[-1] } }
                self.graph.createTriple(subject, predicate, subcategory)
                
                # link subcategory to parent categorie
                level_2_category = { 'EventCategory' : { 'name' : levels[-2] } } if len(levels) > 1 else None
                self.graph.createTriple(subcategory, 'SUBCATEGORY_OF', level_2_category)
    
    def createNewsNodes(self):
        """ News example:
        {"news_id":6,
        "Article_title":"\"Bitcoin Stocks\" Get a New Member as Cboe Launches Bitcoin Futures on Sunday, Dec. 10",
        "Article":"The price of bitcoin, the oldest and largest cryptocurrency by market cap, has skyrocketed 1,578%, from less than $1,000 to $15,973 in 2017, as of 4:00 p.m. ET on Dec. 7....
        "Date":"2017-12-07 00:00:00 UTC",
        "Url":"https:\/\/www.nasdaq.com\/articles\/bitcoin-stocks-get-new-member-cboe-launches-bitcoin-futures-sunday-dec-10-2017-12-07"}
        """
        news_pair_list = self.getNewsPairList()
        print(news_pair_list)
        
        # set news entity
        entity = { 'News' : news_pair_list }

        self.graph.createNodes(entity)
    
    def createNewsMentionsTriples(self):
        # first company mentions
        with open(self.csv_news_mentions_company_path, newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)                 
            subj_label, _, obj_label = header     
            print(f"Adding news mentions triples. Using labels: subject: {subj_label}, object: {obj_label}")
            for news_id, _, company_cik in reader:         
                subject = { 'News' : { 'news_id' : news_id } }
                object = { 'Company' : { 'cik' : company_cik } }
                self.graph.createTriple(subject, 'MENTIONS', object)
        
        # then event mentions
        with open(self.csv_news_mentions_event_path, newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)                 
            subj_label, _, obj_label = header     
            print(f"Adding news mentions triples. Using labels: subject: {subj_label}, object: {obj_label}")
            for news_id, _, event_id in reader:         
                subject = { 'News' : { 'news_id' : news_id } }
                object = { 'Event' : { 'id' : event_id } }
                self.graph.createTriple(subject, 'MENTIONS', object)

    def createEventImpactTriples(self, predicate_name="IMPACTS", triples_path=None):

        if triples_path:
            self.csv_event_impacts_path = triples_path

        with open(self.csv_event_impacts_path, newline='', encoding="utf-8") as f:

            reader = csv.reader(f)
            header = next(reader)                 
            subj_label, _, obj_label = header     
            print(f"Adding event impact triples. Using labels: subject: {subj_label}, object: {obj_label}")
            for event_id, _, company_cik in reader:         
                subject = { 'Event' : { 'id' : event_id } }
                object = { 'Company' : { 'cik' : company_cik } }

                self.graph.createTriple(subject, predicate_name, object)

    # create state country relationship
    def generateStateCountryRelationshipGraph(self):

        # state code pair
        stateCodeNameList = self.getStatePairList()

        # country code pair
        countryCodeNameList = self.getCountryPairList()

        # set object
        object = {}

        for country in countryCodeNameList:
            if country['isoAlpha3Code'] == 'USA':
                object = { 'Country' : country }
                break

        for i in range(len(stateCodeNameList)):

            # set state as subject
            subject = { 'State' : stateCodeNameList[i] }

            # set predicate
            predicate = 'IS_STATE_OF'

            # break if don't have any relation
            if not subject or not object or not predicate:
                continue

            self.graph.createTriple(subject, predicate, object)

    # get company info from json
    def getCompanyInfoFromJson(self, cik):
        # company cik json filename
        cikJsonFilename = "CIK" + cik + ".json"
        if not exists(self.companyCikJsonPath):
            os.makedirs(self.companyCikJsonPath)

        cikfilename = self.companyCikJsonPath + cikJsonFilename

        # get the content from local file if exists
        if not exists(cikfilename):
            cikJsonUrl = r"https://data.sec.gov/submissions/" + cikJsonFilename
            jsonResponse = self.getUrlResponse(cikJsonUrl)
            # print(jsonResponse)
            print(r"{cikJsonFilename} has been downloaded successfully.")
            open(cikfilename, 'wb').write(jsonResponse.content)
        
        # read local json file
        return self.loadJsonData(cikfilename)
    
    # load json data
    def loadJsonData(self, filename):
        print(f"Loading json file: {filename}")
        if not exists(filename):
            return None
        
        # read local json file
        with open(filename, encoding='utf-8') as  cik_json_file:
            # print(cik_json_file)
            return json.load(cik_json_file)

    # get 10k data
    def get10kData(self, cik, txt10kfilename):
        # company 10k file path
        if not exists(self.company10kFilePath):
            os.makedirs(self.company10kFilePath)

        path10kFile = self.company10kFilePath + txt10kfilename

        if not exists(path10kFile):

            # get company 10k filename url
            company10kFilenameUrl = self.generateCompany10kFilenameUrl(cik, txt10kfilename)

            # request the url, and then parse the response
            response10k = self.getUrlResponse(company10kFilenameUrl)
            print(response10k.headers)
            print(response10k.encoding)
            # let the user know it was successful
            print(f'Request Successful from {response10k.url}')
            open(path10kFile, 'wb').write(response10k.content)

        # read the 10k file
        with open(path10kFile, encoding='utf-8', errors='ignore') as file10k: # errors = ignore to ignore undecodable characters)
            # read txt file
            txt10kData=file10k.readlines()
            return txt10kData

    # get company owner html data
    def getCompanyOwnerHtmlData(self, cik):
        # company owner html file path
        if not exists(self.companyOwnerHtmlFilePath):
            os.makedirs(self.companyOwnerHtmlFilePath)

        pathOwnerHtml = self.companyOwnerHtmlFilePath + cik + self.htmlExtensionName

        if not exists(pathOwnerHtml):

            # get company owner
            ownerUrl = self.companyOwnerUrl + cik + self.companyStockRecords
            # print(ownerUrl)

            # get response from the web
            ownerResponse = self.getUrlResponse(ownerUrl)
            # let the user know it was successful
            print(f'Request Successfully from {ownerResponse.url}')
            open(pathOwnerHtml, 'wb').write(ownerResponse.content)
        
        # html contents
        contents = ""

        # read the company owner html file
        with open(pathOwnerHtml, encoding='utf-8') as company_owner_html:
            print(f'Read Successfully from {pathOwnerHtml}')
            # read html file
            ownerData=company_owner_html.readlines()
            for row in ownerData:
                contents += row

            return contents

    # get company issuer html data
    def getCompanyIssuerHtmlData(self, cik):
        # company issuer html file path
        if not exists(self.companyIssuerHtmlFilePath):
            os.makedirs(self.companyIssuerHtmlFilePath)

        pathIssuerHtml = self.companyIssuerHtmlFilePath + cik + self.htmlExtensionName

        if not exists(pathIssuerHtml):

            # get company issuer
            issuerUrl = self.companyIssuerUrl + cik + self.companyStockRecords
            # print(issuerUrl)

            # get response from the web
            issuerResponse = self.getUrlResponse(issuerUrl)
            # let the user know it was successful
            print(f'Request Successful from {issuerResponse.url}')
            open(pathIssuerHtml, 'wb').write(issuerResponse.content)
        
        # html contents
        contents = ""

        # read the company owner html file
        with open(pathIssuerHtml, encoding='utf-8') as company_issuer_html:
            print(f'Read Successfully from {pathIssuerHtml}')
            # read html file
            issuerData=company_issuer_html.readlines()
            for row in issuerData:
                contents += row

            return contents

    # get personal company html data
    def getPersonalCompanyHtmlData(self, personalUrl):
        personalCik = personalUrl.split('=')[-1]

        if not exists(self.personHtmlFilePath):
            os.makedirs(self.personHtmlFilePath)

        # personal html file path
        pathPersonHtml = self.personHtmlFilePath + personalCik + self.htmlExtensionName

        if not exists(pathPersonHtml):

            # add records
            personalUrl = personalUrl + self.companyStockRecords
            # print personal url
            # print(personalUrl)

            # get response from the web
            personalComapnyResponse = self.getUrlResponse(personalUrl)
            # let the user know it was successful
            print(f'Request Successful from {personalComapnyResponse.url}')
            open(pathPersonHtml, 'wb').write(personalComapnyResponse.content)
        
        # html contents
        contents = ""

        # read the personal html file
        with open(pathPersonHtml, encoding='utf-8') as personal_html:
            print(f'Read Successfully from {pathPersonHtml}')
            # read html file
            personalData=personal_html.readlines()
            for row in personalData:
                contents += row

            return contents

    def createTriplesCSV(self):
        """save the graph in csv triples files"""
        if not exists(self.csvTriplesPath):
            os.makedirs(self.csvTriplesPath)
        
        # get all company ciks
        company_file_pairs = [[row[0],row[-1]] for row in self.getCompanyCikAnd10kFilename()]

        company_files = defaultdict(list)

        for cik, filename in company_file_pairs:
            company_files[cik].append(filename)

        # create a csv file x relation -> best format for simplified instance in neo4j
        
        for relationship in self.companyRelationshipKeys:                   
            if relationship == 'HAS_STATE_LOCATION': 

                # create the list of csv rows
                rows = [["Company","HAS_STATE_LOCATION","State"]] 

                for cik in company_files.keys():
                    # state can be obtained from the json data directly
                    data = self.getCompanyInfoFromJson(cik)
                    # state code of HAS_STATE_LOCATION
                    companyStateCode = data['addresses']['business']['stateOrCountry']
                    rows.append([cik,relationship,companyStateCode])

                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows)   

                    

            if relationship == 'HAS_STATE_OF_INCORPORATION':
                
                # create the list of csv rows
                rows = [["Company","HAS_STATE_OF_INCORPORATION","State"]] 

                for cik in company_files.keys():
                    # state can be obtained from the json data directly
                    data = self.getCompanyInfoFromJson(cik)
                    # HAS_STATE_OF_INCORPORATION
                    companyStateCodeOfIncorporation = data['stateOfIncorporation']
                    rows.append([cik,relationship,companyStateCodeOfIncorporation])

                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows)        

            
            if relationship == 'HAS_SEC_FILINGS':
                rows = [["Company","HAS_SEC_FILINGS","SecFilings"]]
                for row in company_file_pairs:
                    row_copy = row.copy()
                    row_copy.insert(1, relationship)
                    rows.append(row_copy)
                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows) 

        
            if relationship == 'BELONGS_TO_INDUSTRY_OF':

                # create the list of csv rows
                rows = [["Company","BELONGS_TO_INDUSTRY_OF","Industry"]] # add the header first

                for cik in company_files.keys():
                    # state can be obtained from the json data directly
                    data = self.getCompanyInfoFromJson(cik)
                    companySicCode = data['sic']
                    rows.append([cik,relationship,companySicCode])

                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows) 


            if relationship == 'HAS_EXCHANGE_MARKET':
                # create the list of csv rows
                rows = [["Company","HAS_EXCHANGE_MARKET","Exchange"]] # add the header first

                for cik in company_files.keys():
                    data = self.getCompanyInfoFromJson(cik)
                    if data['exchanges']:
                        if data['exchanges'][0]:
                            companyExchangeTicker = data['exchanges'][0] # add relation only if there are exchanges
                                                                            # they only add the first exchange?
                            rows.append([cik,relationship,companyExchangeTicker])
                    
                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows) 

                
            # https://www.sec.gov/cgi-bin/own-disp?action=getowner&CIK=0001018724

            # get owner info
            if relationship == 'IS_PARTIAL_OWNER_OF':
                
                rows = [["Company","IS_PARTIAL_OWNER_OF","Company"]]

                for cik in company_files.keys():

                    self.entityCompanyCikPath = self.entityCompanyPath + cik + '/' # first set the company path
                    subCompanyFilename = self.entityCompanyCikPath + cik + self.jsonSubCompanyExtensionName
                    entitySubCompanyJsonData = self.loadJsonData(subCompanyFilename)
                    
                    if not entitySubCompanyJsonData:
                        continue # if the compan is not owner of any other companies skip this relation
                    
                    for subCompany in entitySubCompanyJsonData["IS_PARTIAL_OWNER_OF"]:
                        subcompany_cik = subCompany["issuerCik"]
                        rows.append([cik,relationship,subcompany_cik])

                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows)     

                    

            # https://www.sec.gov/cgi-bin/own-disp?action=getowner&CIK=0001018724
            # get issuer info
            if relationship == 'HAS_INSTRUMENTS_OF':
                pass # no entiendo que significa esta relacion

        # person relationships
        for relationship in self.personalRelationshipKeys:
            if relationship == "IS_DIRECTOR_OF":
                
                rows = [["Person","IS_DIRECTOR_OF","Company"]]

                for cik in company_files.keys():
                    # person entity json file
                    self.entityCompanyCikPath = self.entityCompanyPath + cik + '/' # first set the company path
                    hasPersonJsonDataFilename = self.entityCompanyCikPath + cik + self.jsonHasPersonExtensionName
                    hasPersonJsonData = self.loadJsonData(hasPersonJsonDataFilename)

                    if not hasPersonJsonData:
                        continue

                    personList = hasPersonJsonData[self.personalRelationshipKeys[0]]

                    for person in personList:
                        personCik = person["issuerCik"]
                        rows.append([personCik,relationship,cik])

                        # person has company entity json file
                        # add as well other companies owned by the director
                        personHasCompanyFilename = self.entityCompanyCikPath + 'personHasCompany/' + personCik + self.jsonExtensionName

                        # read sub company info
                        personHasCompanyJsonData = self.loadJsonData(personHasCompanyFilename)
                        if not personHasCompanyJsonData:
                            continue

                        personCompanyList = personHasCompanyJsonData[self.personalRelationshipKeys[0]]

                        for company in personCompanyList: # extract the company ciks form the list of jsons
                            rows.append([personCik,relationship,company["issuerCik"]])

                with open(f"{self.csvTriplesPath}{relationship}.csv","w") as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerows(rows) 

            if relationship == "HAS_INSTRUMENTS_OF":  
                pass

    # download data from edgar and draw graph
    def downloadDataFromEdgarAndDrawGraph(self, to_neo4j=False):

        # get company CIK and 10k filename
        cik10kFilenameTuple = self.getCompanyCikAnd10kFilename()

        # loop through company CIK and 10k filename dict
        for cik, ticker, txt10kfilename in cik10kFilenameTuple:
            
            # company cik path
            self.entityCompanyCikPath = self.entityCompanyPath + cik + '/'

            if not exists(self.entityCompanyCikPath):
                os.makedirs(self.entityCompanyCikPath)

            self.entitySecFilingsCikPath = self.entitySecFilingsPath + cik + "/"

            if not exists(self.entitySecFilingsCikPath):
                os.makedirs(self.entitySecFilingsCikPath)
            
            # entity company json file name
            entityCompanyJsonFilename = self.entityCompanyCikPath + cik + self.jsonExtensionName

            # entity sec filings json file name
            entitySecFilingsJsonFilename = self.entitySecFilingsCikPath + txt10kfilename + self.jsonExtensionName

            # TEMPORAL
            # SKIP IF we already downloaded the data to speed up
            # if exists(entitySecFilingsJsonFilename):
            #     print(f"We already downloaded data for sec filing {txt10kfilename} and company {cik}. Skip for now...")
            #     continue

            # get company info from json
            # https://data.sec.gov/submissions/CIK0001793294.json
            data = self.getCompanyInfoFromJson(cik)

            """
                entity Company
            """
            # name
            companyName = data['name']
            # ticker
            companyTicker = ticker
            # cik
            companyCik = cik
            # irsNumber
            companyIrsNumber = ""
            # secFileNumber
            companySecFileNumber = ""
            # fiscalYear
            companyFiscalYear = ""
            # get 10k data
            data10k = self.get10kData(cik, txt10kfilename)

            # define head sec flag
            headSecFlg = False

            # loop through the file
            for i, line in enumerate(data10k):

                # remove empty line
                line = line.strip().replace('\t','')
                if line == '':
                    continue

                # get company info
                upperLine = line.upper()
                if upperLine.startswith('<SEC-HEADER>'):
                    headSecFlg = True

                elif headSecFlg and upperLine.startswith('</SEC-HEADER>'):
                    headSecFlg = False
                    break

                elif headSecFlg and upperLine.startswith('IRS NUMBER:'):
                    companyIrsNumber = line.split(':')[1]

                elif headSecFlg and upperLine.startswith('SEC FILE NUMBER:'):
                    companySecFileNumber = line.split(':')[1]

                elif headSecFlg and upperLine.startswith('CONFORMED PERIOD OF REPORT:'):
                    companyFiscalYear = line.split(':')[1]

            # state code of HAS_STATE_LOCATION
            companyStateCode = data['addresses']['business']['stateOrCountry']
            # state code of HAS_STATE_OF_INCORPORATION
            companyStateCodeOfIncorporation = data['stateOfIncorporation']
            # fiscalYearEnd
            companyFiscalYearEnd = data['fiscalYearEnd']
            # businessAddress
            businessAddress = data['addresses']['business']
            # add business phone to business address
            businessAddress['phone'] = data['phone']
            companyBusinessAddress = ''
            for ba in businessAddress.values():
                if ba:
                    try:
                        companyBusinessAddress += str(ba) + ' '
                    except Exception as e:
                        print("Error with business address",ba)
                        raise e
            companyBusinessAddress =  companyBusinessAddress.strip()
            # mailingAddress
            mailingAddress = data['addresses']['mailing']
            companyMailingAddress = ''
            for ma in mailingAddress.values():
                if ma:
                    companyMailingAddress += str(ma) + ' '
            companyMailingAddress =  companyMailingAddress.strip()

            # sicCode of BELONGS_TO_INDUSTRY_OF
            companySicCode = data['sic']
            # name of BELONGS_TO_INDUSTRY_OF
            # companySicName = data['sicDescription']

            """
                entity HAS_SEC_FILINGS
            """
            # sec filing info

            # review 
            filingsCategory = data['category']
            filingsAmounts = ""
            if data['filings']:
                if data['filings']['files']:
                    if data['filings']['files'][0]:
                        if data['filings']['files'][0]['filingFrom']:
                            filingsAmounts = data['filings']['files'][0]['filingFrom'] # ??? not all filings

            # company exchange ticker of HAS_EXCHANGE_MARKET
            companyExchangeTicker = ""
            if data['exchanges']:
                if data['exchanges'][0]:
                    companyExchangeTicker = data['exchanges'][0]

            # businessSegments
            companyBusinessSegments = ""
            # productServices
            companyProductServices = ""

            # entity company json data
            entityCompanyJsonData = {
                'name' : companyName,
                 'ticker' : companyTicker,
                 'cik' : companyCik,
                 'irsNumber' : companyIrsNumber,
                 'stateCode' : companyStateCode,
                 'stateCodeOfIncorporation' : companyStateCodeOfIncorporation,
                 'fiscalYearEnd' : companyFiscalYearEnd,
                 'businessAddress' : companyBusinessAddress,
                 'mailingAddress' : companyMailingAddress,
                 'exchangeTicker' : companyExchangeTicker,
                 'businessSegments' : companyBusinessSegments,
                 'productServices' : companyProductServices,
                 'sicCode' : companySicCode
            }

            # entity secFilings json data
            entitySecFilingsJsonData = {
                'cik' : companyCik,
                'filingsCategory' : filingsCategory,
                'filingsAmounts' : filingsAmounts,
                'fiscalYear' : companyFiscalYear,
                'secFileNumber' : companySecFileNumber
            }

            # create entity json file
            if not exists(entityCompanyJsonFilename):
                with open(entityCompanyJsonFilename, 'w', encoding='utf-8') as entityCompany_json_writer:
                    json.dump(entityCompanyJsonData, entityCompany_json_writer, indent=4, ensure_ascii=False)

            # create entity json file
            if not exists(entitySecFilingsJsonFilename):
                with open(entitySecFilingsJsonFilename, 'w', encoding='utf-8') as entitySecFilings_json_writer:
                    json.dump(entitySecFilingsJsonData, entitySecFilings_json_writer, indent=4, ensure_ascii=False)

            # create sub company entity json file
            self.createCompanyHasCompanyJsonFile(cik)

            # get company issuer info list
            self.createCompanyHasPersonJsonFile(cik)

            print('*'*80)
            print(f"Data of Company Name: {companyName}, Company CIK: {companyCik} has been downloaded successfully.")
            print('*'*80)
            
            if to_neo4j:
                """
                Draw the graph in neo4j

                changes pending: before adding the comapny again check if it already exists, avoid creating duplicated triples
                only create secfiling related properties.
                """
                # set subject
                subject = {'Company' : entityCompanyJsonData}
                print(subject)
                
                # if main company exists, then set other properties
                self.graph.setMainCompanyProperty(subject)

                # sub company entity json file
                subCompanyFilename = self.entityCompanyCikPath + cik + self.jsonSubCompanyExtensionName

                # read sub company info
                entitySubCompanyJsonData = self.loadJsonData(subCompanyFilename)

                # loop through company relationships
                for relationship in self.companyRelationshipKeys:

                    if relationship == 'HAS_STATE_LOCATION':

                        # set predicate
                        predicate = 'HAS_STATE_LOCATION'
                        object = ''

                        for statePair in self.statePairList:
                            
                            # company location
                            # just loop though the pair list until it finds the state
                            if companyStateCode == statePair['code']:

                                object = {'State' : statePair}
                                break

                        # break if don't have any relation
                        if not subject or not object or not predicate:
                            break
                        
                        # create location graph
                        self.graph.createTriple(subject, predicate, object)

                    if relationship == 'HAS_STATE_OF_INCORPORATION':

                        # set predicate
                        predicate = 'HAS_STATE_OF_INCORPORATION'

                        # loop through state pair list
                        for statePair in self.statePairList:
                            
                            # company location of incorporation
                            if companyStateCodeOfIncorporation == statePair['code']:

                                object = {'State' : statePair}
                                break

                        # break if don't have any relation
                        if not subject or not object or not predicate:
                            break
                        
                        # create graph
                        self.graph.createTriple(subject, predicate, object)

                    if relationship == 'HAS_SEC_FILINGS':

                        # set predicate
                        predicate = 'HAS_SEC_FILINGS'

                        secFilingObject = {
                                            self.secFilingsPropertyKeys[0]: cik,
                                            self.secFilingsPropertyKeys[1]: filingsCategory,
                                            self.secFilingsPropertyKeys[2]: filingsAmounts,
                                            self.secFilingsPropertyKeys[3]: companyFiscalYearEnd,
                                            self.secFilingsPropertyKeys[4]: companySecFileNumber
                                            }

                        object = {'SecFilings' : secFilingObject}
                        

                        # break if don't have any relation
                        if not subject or not object or not predicate:
                            break
                        
                        # create graph
                        self.graph.createTriple(subject, predicate, object)

                    if relationship == 'BELONGS_TO_INDUSTRY_OF':

                        # set predicate
                        predicate = 'BELONGS_TO_INDUSTRY_OF'

                        for sicPair in self.sicPairList:
                            
                            # company location
                            if companySicCode == sicPair['sicCode']:

                                object = {'StandardIndustrialClassification' : sicPair}
                                break

                        # break if don't have any relation
                        if not subject or not object or not predicate:
                            break
                        
                        # create graph
                        self.graph.createTriple(subject, predicate, object)

                    if relationship == 'HAS_EXCHANGE_MARKET':

                        # set predicate
                        predicate = 'HAS_EXCHANGE_MARKET'
                        
                        if not companyExchangeTicker:
                            continue

                        exchangePair = self.getExchangePair(companyExchangeTicker)

                        object = {'Exchange' : exchangePair}                    

                        # break if don't have any relation
                        if not subject or not object or not predicate:
                            break
                        
                        # create graph
                        self.graph.createTriple(subject, predicate, object)
                    
                    # https://www.sec.gov/cgi-bin/own-disp?action=getowner&CIK=0001018724
                    # get owner info
                    if relationship == 'IS_PARTIAL_OWNER_OF':

                        if not entitySubCompanyJsonData:
                            continue

                        # IS_PARTIAL_OWNER_OF
                        entityCompanyIsPartialOwnerOfJsonData = entitySubCompanyJsonData[self.companyRelationshipKeys[4]]

                        # set predicate
                        predicate = ''
                        object = ''

                        for idx, entityCompanyIsPartialOwnerOf in enumerate(entityCompanyIsPartialOwnerOfJsonData):
                        
                            predicate = {self.companyRelationshipKeys[4] : 
                                                {
                                                    self.isPartialOwnerOfPropertyName[0] : entityCompanyIsPartialOwnerOf[self.isPartialOwnerOfPropertyName[0]],
                                                    self.isPartialOwnerOfPropertyName[1] : entityCompanyIsPartialOwnerOf[self.isPartialOwnerOfPropertyName[1]]
                                                }
                                        }

                            object = {'Company' : {
                                self.companyPropertyKeys[0] : entityCompanyIsPartialOwnerOfJsonData[idx][self.isPartialOwnerOfOwnerIssuerPropertyKeys[0]],
                                self.companyPropertyKeys[2] : entityCompanyIsPartialOwnerOfJsonData[idx][self.isPartialOwnerOfOwnerIssuerPropertyKeys[2]]
                                }}

                            # break if don't have any relation
                            if not subject or not object or not predicate:
                                break

                            # create graph
                            self.graph.createTriple(subject, predicate, object)

                    # https://www.sec.gov/cgi-bin/own-disp?action=getowner&CIK=0001018724
                    # get issuer info
                    if relationship == 'HAS_INSTRUMENTS_OF':

                        if not entitySubCompanyJsonData:
                            continue

                        # HAS_INSTRUMENTS_OF
                        entityCompanyHasInstrumentsOfJsonData = entitySubCompanyJsonData[self.companyRelationshipKeys[5]]

                        # set predicate
                        predicate = ''
                        object = ''

                        for idx, entityCompanyHasInstrumentsOf in enumerate(entityCompanyHasInstrumentsOfJsonData):
                        
                            predicate = {self.companyRelationshipKeys[5] : 
                                                {
                                                    self.hasInstrumentsOfPropertyName[0] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[0]],
                                                    self.hasInstrumentsOfPropertyName[1] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[1]],
                                                    self.hasInstrumentsOfPropertyName[2] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[2]],
                                                    self.hasInstrumentsOfPropertyName[3] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[3]],
                                                    self.hasInstrumentsOfPropertyName[4] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[4]],
                                                    self.hasInstrumentsOfPropertyName[5] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[5]],
                                                    self.hasInstrumentsOfPropertyName[6] : entityCompanyHasInstrumentsOf[self.hasInstrumentsOfPropertyName[6]]
                                                }
                                        }

                            object = {'Company' : {
                                self.companyPropertyKeys[0] : entityCompanyIsPartialOwnerOfJsonData[idx][self.isPartialOwnerOfOwnerIssuerPropertyKeys[0]],
                                self.companyPropertyKeys[2] : entityCompanyIsPartialOwnerOfJsonData[idx][self.isPartialOwnerOfOwnerIssuerPropertyKeys[2]]
                                }}

                            # break if don't have any relation
                            if not subject or not object or not predicate:
                                break

                            # create graph
                            self.graph.createTriple(subject, predicate, object)

                # person entity json file
                hasPersonJsonDataFilename = self.entityCompanyCikPath + cik + self.jsonHasPersonExtensionName

                # read sub company info
                hasPersonJsonData = self.loadJsonData(hasPersonJsonDataFilename)

                if not hasPersonJsonData:
                    continue

                personList = hasPersonJsonData[self.personalRelationshipKeys[0]]
                stockLIst= hasPersonJsonData[self.personalRelationshipKeys[1]]

                for idx, person in enumerate(personList):
                    # set object
                    object = {'Person' : {
                                            self.personalPropertyKeys[0] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[0]],
                                            self.personalPropertyKeys[1] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[2]],
                                            self.personalPropertyKeys[2] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[4]],
                                            self.personalPropertyKeys[3] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[5]]
                                        }}
                    # set predicate
                    predicate = {self.personalRelationshipKeys[0] : 
                                    {
                                        self.personalIsDirectorOfPropertyKeys[0] : person[self.personIsPartialOwnerOfPropertyKeys[6]],
                                        self.personalIsDirectorOfPropertyKeys[1] : person[self.personIsPartialOwnerOfPropertyKeys[7]]
                                    }
                                }
                    # create graph
                    self.graph.createTriple(object, predicate, subject)

                    personCik = personList[idx][self.personIsPartialOwnerOfPropertyKeys[2]]

                    # person has company entity json file
                    personHasCompanyFilename = self.entityCompanyCikPath + 'personHasCompany/' + personCik + self.jsonExtensionName

                    # read sub company info
                    personHasCompanyJsonData = self.loadJsonData(personHasCompanyFilename)
                    if not personHasCompanyJsonData:
                        continue

                    personCompanyList = personHasCompanyJsonData[self.personalRelationshipKeys[0]]
                    personStockLIst= personHasCompanyJsonData[self.personalRelationshipKeys[1]]
                    for idx, personCompany in enumerate(personCompanyList):
                        # set predicate
                        predicate = {self.personalRelationshipKeys[0] : 
                                        {
                                            self.personalIsDirectorOfPropertyKeys[0] : personCompany[self.personIsPartialOwnerOfPropertyKeys[6]],
                                            self.personalIsDirectorOfPropertyKeys[1] : personCompany[self.personIsPartialOwnerOfPropertyKeys[7]]
                                        }
                                    }
                        # set subject
                        subCompanySubject = {'Company' : 
                                                        {
                                                            self.companyPropertyKeys[0] : personCompany[self.personIsPartialOwnerOfPropertyKeys[0]],
                                                            self.companyPropertyKeys[2] : personCompany[self.personIsPartialOwnerOfPropertyKeys[2]]
                                                        }
                                            }
                        print(subCompanySubject)
                        # create graph
                        self.graph.createTriple(object, predicate, subCompanySubject)
                    for idx, personStock in enumerate(personStockLIst):
                        # set predicate
                        predicate = {self.personalRelationshipKeys[1] : 
                                        {
                                        self.hasInstrumentsOfPropertyName[0] : personStock[self.hasInstrumentsOfPropertyName[0]],
                                        self.hasInstrumentsOfPropertyName[1] : personStock[self.hasInstrumentsOfPropertyName[1]],
                                        self.hasInstrumentsOfPropertyName[2] : personStock[self.hasInstrumentsOfPropertyName[2]],
                                        self.hasInstrumentsOfPropertyName[3] : personStock[self.hasInstrumentsOfPropertyName[3]],
                                        self.hasInstrumentsOfPropertyName[4] : personStock[self.hasInstrumentsOfPropertyName[4]],
                                        self.hasInstrumentsOfPropertyName[5] : personStock[self.hasInstrumentsOfPropertyName[5]],
                                        self.hasInstrumentsOfPropertyName[6] : personStock[self.hasInstrumentsOfPropertyName[6]]
                                        }
                                    }
                        # set subject
                        subCompanySubject = {'Company' : 
                                                        {
                                                            self.companyPropertyKeys[0] : personCompanyList[idx][self.personIsPartialOwnerOfPropertyKeys[0]],
                                                            self.companyPropertyKeys[2] : personCompanyList[idx][self.personIsPartialOwnerOfPropertyKeys[2]]
                                                        }
                                            }
                        print(subCompanySubject)
                        # create graph
                        self.graph.createTriple(object, predicate, subCompanySubject)

                # stock info
                for idx, stock in enumerate(stockLIst):
                    # set object
                    object = {'Person' : {
                                            self.personalPropertyKeys[0] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[0]],
                                            self.personalPropertyKeys[1] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[2]],
                                            self.personalPropertyKeys[2] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[4]],
                                            self.personalPropertyKeys[3] : personList[idx][self.personIsPartialOwnerOfPropertyKeys[5]]
                                        }}
                    # set predicate
                    predicate = {self.personalRelationshipKeys[1] : 
                                    {
                                        self.hasInstrumentsOfPropertyName[0] : stock[self.hasInstrumentsOfPropertyName[0]],
                                        self.hasInstrumentsOfPropertyName[1] : stock[self.hasInstrumentsOfPropertyName[1]],
                                        self.hasInstrumentsOfPropertyName[2] : stock[self.hasInstrumentsOfPropertyName[2]],
                                        self.hasInstrumentsOfPropertyName[3] : stock[self.hasInstrumentsOfPropertyName[3]],
                                        self.hasInstrumentsOfPropertyName[4] : stock[self.hasInstrumentsOfPropertyName[4]],
                                        self.hasInstrumentsOfPropertyName[5] : stock[self.hasInstrumentsOfPropertyName[5]],
                                        self.hasInstrumentsOfPropertyName[6] : stock[self.hasInstrumentsOfPropertyName[6]]
                                    }
                                }
                    # create graph
                    self.graph.createTriple(object, predicate, subject)
            
                    

# main implement area
if __name__ == "__main__":

    # init Russell3000 instance
    coreKG = CoreKG()

    # generate security exchange files
    # coreKG.generateSecurityExchangeNameFile()

    # remove all the nodes and relations
    coreKG.graph.remove_relationships_nodes()
    print('Removed all nodes with relationships.')

    # remove all the nodes
    coreKG.graph.remove_nodes()
    print('Removed all the sole nodes.')

    # create event and event category nodes
    coreKG.createEventNodes()

    # create the news nodes
    coreKG.createNewsNodes()

    # create exchange nodes
    coreKG.createExchangeNodes()

    # create country nodes
    coreKG.createCountryNodes()

    # create sic nodes
    coreKG.createSicNodes()

    coreKG.createMajorIndustryTriples()

    # create state and country relationship
    coreKG.generateStateCountryRelationshipGraph()

    # download data from edgar
    coreKG.downloadDataFromEdgarAndDrawGraph(to_neo4j=True)
    
    # coreKG.createEventImpactTriples(predicate_name="IMPACTS_CORRECT", triples_path="csvTriples\IMPACTS-CORRECT.csv")
    coreKG.createEventImpactTriples(predicate_name="IMPACTS_STRICT_CORRECT", triples_path="csvTriples\IMPACTS-91percThreshold-CORRECT.csv")

    # create news mentions company and event triples
    coreKG.createNewsMentionsTriples()

    # delete duplicated nodes repeated ids and ciks
    coreKG.graph.remove_duplicated_nods(label="Company", property="cik")
    coreKG.graph.remove_duplicated_nods(label="Event", property="id")
    coreKG.graph.remove_duplicated_nods(label="News", property="news_id")

    # store the results in csv triples
    # coreKG.createTriplesCSV()