#!/usr/bin/python
# -*- coding: utf-8 -*

# This file contains the channel's categories and the channel names to be displayed
# for each category in the plugin's UI. 

Egypt = ['dmc Drama', 'Sada El Balad', 'Al Kahera Wal Nas', 'Sofra',
         'El Balad Drama', 'AlHayah 2', 'Al Kahera Wal Nas 2', 'ON Ent',
         'قناة دريم', 'CBCDrama', 'Alhayah 1', 'dmc Live', 'MBC Masr'
]
News = ['DW عربية', 'قناة الإخبارية', 'سكاي نيوز عربية', 'Fox News', 'CNN', 'MSNBC',
        'فرانس 24', 'AlArabiya', 'FRANCE 24 English', 'Al Jazeera Arabic',
        'Al Jazeera Mubasher', 'eXtra news', 'Al Mayadeen', 'ON live',
        'BBC Arabic', 'الاخبارية السورية', 'Sky News - Live', 'Al Manar TV',
        'مباشر 24', 'DW English', 'RT Arabic', 'Al Jazeera English',
        'Al Jazeera Balkans', 'euronews EN DIRECT', 'africanews Live',
        'africanews (en français)', 
]
Sports = ['الرياضية المغربية', 'السعودية الرياضية', 'beIN SPORTS News',
          'Alkass', 'الرياضية العراقية', 'Kuwait Sport TV', 'ON Sport',
          'kuwait sport plus', 'AlAhly TV', 'dmc SPORTS', 'memo tube', 
]
Islam = ['منهاج النبوة', 'قناة دار الإيمان', 'إذاعة القران الكريم', 'قناة افاق',
         'قناة مكة - البث المباشر', 'لإذاعة القرآن الكريم من قطر',
         'لقناة الشيخ ابن عثيمين', 'إذاعة القرآن الكريم من القاهرة',
         'Quran Hidayah', 'على العهد', 'السنة النبوية', 'قناة النعيم',
         'قناة الإصلاح', 'قناة القران الكريم', 'قناة الاستقامة', 
         'لقناة صوت العترة الشيعية', 'FADAK TV', 'ALNADATV', 'Hidayat TV',
         'قناة القرآن الكريم .. مكه المكرمه',
]
Christian = ['alfadytv', 'الكرمة 1 شمال امريكا', 'الكرمة 2 الشرق الاوسط',
             'MESat', 'Al Hayat TV', 'Aghapy TV', 'كنيسة المسيح مصر الجديدة بث مباشر',

]
Syria = ['الفضائية السورية', 'اذاعة زنوبيا', 'اذاعة دمشق : البث المباشر',
         'اذاعة سوريانا', 'قناة سما الفضائية', 'سورية دراما', 'اذاعة أمواج',
         'قناة الفلوجة', 'اذاعة صوت الشباب',  'قناة نور الشام',
         'قناة أوغاريت', 'قناة السوري الحر', 'التربوية السورية',
         'قناة سوريا الحرة','اذاعة الكرمة','العهد', 'قناة كربلاء'
]
Gulf = ['الاتجاه', 'قناة أجيال', 'قناة الإخبارية', 'قناة الأماكن الفضائية',
        'السعودية الرياضية', 'قناة العصر', 'الاقتصادية السعودية', 'الساحات',
        'Kuwait Television KTV1', 'Wesal Tv', 'Belqees TV',
        'Bedaya TV', 'المسار الاولى','القناة ‫السعودية‬‎', 'قناة الصحراء',
        'قناة الصحراء الابل', 'قناة الواحة', 'Kuwait Television English',
        'Dubai','قناة خير الفضائية','المسيرة','Marina TV','القرين',
        'LuaLuaTV Bahrain', 'تلفزيون البحرين','قناة الوسام',
        
]
North_Africa = ['الرياضية المغربية', 'Attessia TV', 'Libya24 Tv', 'TAWATUR']
Misc = ['قناة BF الفضائية', 'Direct TV', 'قناة أوكرانيا الآن', 'Prime Tv',
        'قناة العدالة', 'قناة الواقع', 'قناة وصال', 'Al Jazeera Documentary',
        'Sudania24', 'القناة الثقافية السعودية'  ]
Entertainment = ['MBC 4', 'سورية دراما', 'الدوشكا', 'Roya TV', ]

categories = {'Egypt':Egypt, 'News': News, 'Sports':Sports, 'Islam':Islam, 
              'Christian': Christian, 'Syria': Syria, 'Gulf': Gulf,
              'North_Africa':North_Africa, 'Entertainment': Entertainment,
              'Misc': Misc }

# the following list contains all acceptable tv channel partial names
# that can be retrieved.
filters = [ \
     'Al',
     'Arab',
     'ON E',
     'البث',
     'قناة',
     'مباشر',
     'news',
    ]
excludes = r'2k|playground'

# the folowing list is the search items to execute via the youtube api
search_list = ['قناة', 'dmc', 'arabic', 'egypt', 'مصر', 'beIN', 'ON E', 'sports', 'NBA', 'live']

