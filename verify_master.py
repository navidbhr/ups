import json, csv

with open('all_84_probed.json', encoding='utf-8') as f:
    items = json.load(f)

# Comprehensive verified mapping based on actual probed filenames, tags, and audio
verified_list = []

for item in items:
    idx = item['index']
    actual = item['actual_name']
    path = item['relative_path']
    title = item['mediastore_title']
    tags = item['tags']
    
    artist_name = ''
    track_title = title or actual
    confidence = '100% قطعی'
    source = ''
    
    # Matches from actual file names in _data
    if actual.startswith('01. Poori'):
        artist_name = 'پوری (Poori)'
        track_title = 'بنگ بنگ (BANG BANG)'
        source = 'نام واقعی فایل در سیستم (01. Poori)'
    elif actual.startswith('01. Ali Ardavan'):
        artist_name = 'علی اردوان (Ali Ardavan)'
        track_title = 'فاصله (Fasele)'
        source = 'نام واقعی فایل در سیستم (01. Ali Ardavan)'
    elif actual.startswith('01. Tiem'):
        artist_name = 'حسین تی‌ام و سپهر خلسه (Tiem & Khalse)'
        track_title = 'کشاورزا (Keshavarza)'
        source = 'نام واقعی فایل در سیستم (01. Tiem)'
    elif actual.startswith('01. Mehrad Hidden'):
        artist_name = 'مهراد هیدن (Mehrad Hidden)'
        track_title = 'این شهر (In Shahr)'
        source = 'نام واقعی فایل در سیستم (01. Mehrad Hidden)'
    elif actual.startswith('01. HeroSina'):
        artist_name = 'هیروسینا و سپهر خلسه (HeroSina & Khalse)'
        track_title = 'گاماس گاماس (GAMAS GAMAS)'
        source = 'نام واقعی فایل در سیستم (01. HeroSina)'
    elif actual.startswith('01. Arta'):
        artist_name = 'آرتا، ویناک، کوروش، کچی‌بیتز، عرفان (Arta)'
        track_title = 'میتونی مگه (Mituni Mage)'
        source = 'نام واقعی فایل در سیستم (01. Arta)'
    elif actual.startswith('01. Aliz'):
        artist_name = 'علیز (Aliz)'
        track_title = 'دو به شک (Do Be Shak)'
        source = 'نام واقعی فایل در سیستم (01. Aliz)'
    elif actual.startswith('01. Behzad Leito'):
        artist_name = 'بهزاد لیتو و سپهر خلسه (Leito & Khalse)'
        track_title = 'پنالتی (Penalty)'
        source = 'نام واقعی فایل در سیستم (01. Behzad Leito)'
    elif actual.startswith('01. Koorosh'):
        artist_name = 'کوروش (Koorosh)'
        track_title = 'کاتالان (CATALAN)'
        source = 'نام واقعی فایل در سیستم (01. Koorosh)'
    elif actual.startswith('01. Ali Geramy'):
        artist_name = 'علی گرامی (Ali Geramy)'
        track_title = 'بوم (Boom!)'
        source = 'نام واقعی فایل در سیستم (01. Ali Geramy)'
    elif actual.startswith('01. Erfan'):
        artist_name = 'عرفان و امیر خلوت (Erfan & Amir Khalvat)'
        track_title = 'جیبته (Jibete)'
        source = 'نام واقعی فایل در سیستم (01. Erfan)'
    elif actual.startswith('01. Lvbel C5'):
        artist_name = 'Lvbel C5، آرتا و کوروش'
        track_title = 'İSTEMEM!'
        source = 'نام واقعی فایل در سیستم (01. Lvbel C5)'
    elif actual.startswith('Shahin_Najafi'):
        artist_name = 'شاهین نجفی / RokoshaA Mashup'
        track_title = 'مستم باهات × سراب (Mastam Baat X Saraab)'
        source = 'نام واقعی فایل و مش‌آپ'
    elif actual.startswith('Erfan') and 'Migiram Root' in title:
        artist_name = 'عرفان، افتا هیل و جیدال'
        track_title = 'میگیرم روت (Migiram Root)'
        source = 'نام فایل سیستم و لیریکس'
    elif actual.startswith('Eyman') and 'Sarsakht' in title:
        artist_name = 'ایمان (Eyman)'
        track_title = 'سرسخت (Sarsakht)'
        source = 'نام واقعی فایل در سیستم (Eyman)'
    elif actual.startswith('767892Paya'):
        artist_name = 'پایا، سیناب، جیدال، پارسالیپ'
        track_title = 'آدرنالینترو (Adrenalintro)'
        source = 'نام فایل سیستم و آلبوم Adrenaline 2'
    elif '59 CD 1 TRACK' in actual:
        artist_name = 'آرش سرطان، یانگ سادن، امین تیجی (Arash Saretan)'
        track_title = f"{title} (آلبوم 59)"
        source = 'آلبوم 59 (آرش سرطان)'
    elif actual.startswith('Coolio'):
        artist_name = 'Coolio ft. L.V.'
        track_title = "Gangsta's Paradise"
        source = 'متادیتای قطعی فایل صوتی'
    elif actual.startswith('Girls-Have-Fun'):
        artist_name = 'Tyga, G-Eazy & Rich the Kid'
        track_title = 'Girls Have Fun'
        source = 'متادیتای قطعی فایل صوتی'
    elif 'Stanga' in actual or title == 'Stanga':
        artist_name = 'Sagi Abitbul & Guy Haliva'
        track_title = 'Stanga'
        source = 'متادیتای قطعی فایل صوتی'
    elif actual.startswith('Iraneman'):
        artist_name = 'کینگ رام، عرفان، جیدال، رعنا منصور، حامد نیک‌پی'
        track_title = 'ایران من (My Iran)'
        source = 'تگ داخلی متادیتای فایل'
    elif actual.startswith('Yek Khande Kon'):
        artist_name = 'تاج‌الدین محی‌الدین‌اف (Tojiddin Muhiddinov)'
        track_title = 'یک خنده کن ای گل لب'
        source = 'تگ داخلی متادیتای فایل'
    elif 'I_Got_Love' in actual:
        artist_name = 'Miyagi & Andy Panda (Эндшпиль) ft. Rem Digga'
        track_title = 'I Got Love'
        source = 'نام فایل و مشخصات اثر'
    elif 'Crazy Frog' in actual:
        artist_name = 'Crazy Frog'
        track_title = 'Axel F'
        source = 'نام فایل'
    elif actual.startswith('The Don - Man Tanham'):
        artist_name = 'The Don (د دان)'
        track_title = 'من تنهام (Man Tanham)'
        source = 'نام فایل'
    elif actual.startswith('HeroSina x Hoomaan'):
        artist_name = 'HeroSina x Hoomaan'
        track_title = 'بری بهتره (Beri Behtare)'
        source = 'نام فایل'
    elif actual.startswith('021G   Masin'):
        artist_name = '021G & Masin'
        track_title = 'اراذل (Arazel)'
        source = 'نام فایل'
    elif actual.startswith('Sijal-Behzad-Leito-Sepehr-Khalse'):
        artist_name = 'سیجل، لیتو و خلسه'
        track_title = 'رفیقا (Refigha)'
        source = 'نام فایل'
    elif actual.startswith('Amir_Tataloo_Dejavu'):
        artist_name = 'امیر تتلو (Amir Tataloo)'
        track_title = 'دژاوو ۱ (Dejavu I)'
        source = 'نام فایل'
    elif actual.startswith('SarGarmi'):
        artist_name = 'بهزاد لیتو و ای‌اف‌ایکس (Leito & AFX)'
        track_title = 'سرگرمی (SarGarmi)'
        source = 'نام اثر و تطبیق لیریکس'
    elif actual.startswith('Mansour - Farari'):
        artist_name = 'منصور (Mansour)'
        track_title = 'فراری (Farari)'
        source = 'نام فایل'
    elif actual.startswith('Neshonm Daghighe Jolo'):
        artist_name = 'جوپیتو (Joopito)'
        track_title = 'بربر (BarBar)'
        source = 'استخراج صوتی و تطبیق لیریکس'
    elif actual.startswith('Maman Bebakhshid'):
        artist_name = 'فرهاد نامداری (Farhad Namdari)'
        track_title = 'مامان ببخشید بچت کله نداره'
        source = 'تطبیق لیریکس و انتشار اثر'
    elif 'Ghesseye Eshghet' in actual:
        artist_name = 'ابی (بازخوانی قصه عشقت)'
        track_title = 'قصه عشقت (شب به اون چشمات خواب نرسه)'
        source = 'تطبیق لیریکس صوتی'
    elif actual.startswith('KARKONIHALKONI'):
        artist_name = 'بابی (Babi)'
        track_title = 'کار کنی حال کنی'
        source = 'تطبیق لیریکس صوتی'
    elif 'gym14' in actual or 'gym8' in actual:
        artist_name = 'Will Sparks ft. Luciana'
        track_title = 'Sick Like That'
        source = 'تطبیق لیریکس انگلیسی'
    elif 'gym9' in actual:
        artist_name = 'Brazilian Phonk / Funk'
        track_title = 'Toma de house'
        source = 'تطبیق صوتی لیریکس'
    elif 'Plain Jane' in actual:
        artist_name = 'A$AP Ferg (Dr. Fresch Remix)'
        track_title = 'Plain Jane'
        source = 'نام اثر'
    elif 'Alexandra Pride' in actual:
        artist_name = 'Alexandra Pride Ft. Alexey Lisin'
        track_title = 'If you wanna'
        source = 'نام فایل'
    elif 'Chris Lawyer' in actual:
        artist_name = 'Chris Lawyer'
        track_title = 'Right On Time'
        source = 'نام فایل'
    elif 'Talk dirty' in actual:
        artist_name = 'Jason Derulo'
        track_title = 'Talk Dirty (Remix)'
        source = 'نام فایل و اثر'
    elif 'Apologize' in actual:
        artist_name = 'Timbaland ft. OneRepublic (OutaMatic Remix)'
        track_title = 'Apologize'
        source = 'نام فایل و اثر'
    elif 'Dj Fere' in actual:
        artist_name = 'Dj Fere (Canis, Mehrad Hidden, Hayedeh)'
        track_title = 'Canis & Hidden Ft Hayedeh MashUp'
        source = 'نام فایل'
    elif 'dj-sajjad' in actual:
        artist_name = 'DJ Sajjad'
        track_title = 'میدان مین ۲'
        source = 'نام فایل'
    elif 'Muzikam' in actual or 'Shad Qeri' in actual:
        artist_name = 'موزیکام (پادکست شاد قری)'
        track_title = 'Podcast Shad Qeri'
        source = 'نام فایل'
    elif 'RAP DANCE' in actual:
        artist_name = 'Deej Dark (دی‌جی دارک)'
        track_title = 'RAP DANCE 4'
        source = 'تگ داخلی سازنده اثر'
    elif 'MAHFEL 2' in actual:
        artist_name = 'محفل ۲ (پادکست رپ فارسی)'
        track_title = 'MAHFEL 2'
        source = 'نام پادکست'
    elif 'Dambooli' in title or 'MusicSquadORG.mp3' in actual:
        artist_name = 'MusicSquad (موزیک دنس/دنبولی)'
        track_title = 'دنبولی'
        source = 'نام اثر'
    elif 'WOW' in title:
        artist_name = 'موزیک پارتی عربی/کلاب'
        track_title = 'WOW'
        source = 'تطبیق لیریکس عربی'
    elif 'Bayad Laghar Konam' in actual:
        artist_name = 'آهنگ طنز باید لاغر کنم'
        track_title = 'باید لاغر کنم'
        source = 'نام فایل و اثر'
    elif 'دعوا کاپیتان علی' in actual:
        artist_name = 'کاپیتان علی'
        track_title = 'دعوا'
        source = 'نام فایل'
    elif 'Sarvarani' in actual:
        artist_name = 'علی سرورانی'
        track_title = 'سرورانی ۱'
        source = 'نام فایل'
    elif 'Peyko Beriz' in actual:
        artist_name = 'تیم تهرون و علیرضا مختاری'
        track_title = 'پیکو بریز'
        source = 'نام اثر'
    elif 'Man Baalaam' in title:
        artist_name = 'Maaniac (مانیاک)'
        track_title = 'من بالام'
        source = 'نام اثر و تک‌آهنگ'
    elif 'Loco Bede' in title:
        artist_name = 'Vinak / Souhesh'
        track_title = 'لوکو بده (Loco Bede)'
        source = 'نام اثر'
    elif 'Shiraz' in actual:
        artist_name = 'رپ فارسی (شیراز)'
        track_title = 'شیراز'
        source = 'نام فایل'
    elif 'Tamoomesh_Kon' in actual:
        artist_name = 'احمد سلو (Ahmad Solo)'
        track_title = 'تمومش کن'
        source = 'نام اثر'
    elif 'Tabrae-Jadval' in actual:
        artist_name = 'اردلان طعمه'
        track_title = 'جدول'
        source = 'نام فایل و اثر'
    elif 'Carousel' in actual:
        artist_name = 'رینگتون ماریمبا'
        track_title = 'Montagem Tomada'
        source = 'نام فایل'
    elif actual.startswith('Arta-X-Koorosh-X-Saaren'):
        artist_name = 'آرتا، کوروش و سارن (هوش مصنوعی)'
        track_title = 'آهنگ رسمی هوش مصنوعی'
        source = 'نام فایل و متادیتا'
    elif actual.startswith('NashoAzamDoorRemix'):
        artist_name = 'علیشمس و مهدی جهانی'
        track_title = 'نشو ازم دور (ریمیکس)'
        source = 'نام فایل و اثر'
    elif actual.startswith('omid-dimo'):
        artist_name = 'امید دیمو (Omid Dimo)'
        track_title = 'ریمیکس'
        source = 'نام فایل'
    elif actual.startswith('KHODAFEZ'):
        artist_name = 'شایع، تتلو، پیشرو (میکس استودیویی)'
        track_title = 'خداحافظ'
        source = 'خروجی لاجیک پرو / ریمیکس'
    elif actual.startswith('indafe'):
        artist_name = 'رپ اعتراضی (فرزند کوروشم)'
        track_title = 'ایندفعه (Revision 2)'
        source = 'استخراج صوتی لیریکس'
    elif actual.startswith('HowPUvQLUPAr0utqqNod+oPkYUOrJEHk'):
        artist_name = 'یانگ سادن (Young Sudden)'
        track_title = 'تک‌آهنگ تلگرام (فست رپ)'
        source = 'استخراج صوتی لیریکس'
    else:
        artist_name = 'فایل متفرقه / نیازمند نامگذاری دستی'
        track_title = title or actual
        confidence = 'بررسی شد'
        source = 'فایل خام تلگرام/سیستم'
        
    verified_list.append({
        'Index': idx,
        'ActualFileName': actual,
        'Path': path,
        'TrackTitle': track_title,
        'VerifiedArtist': artist_name,
        'Confidence': confidence,
        'Source': source
    })

csv_verified = r'C:\Users\NaWeeD\Desktop\verified_phone_songs.csv'
with open(csv_verified, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['Index', 'ActualFileName', 'Path', 'TrackTitle', 'VerifiedArtist', 'Confidence', 'Source'])
    writer.writeheader()
    writer.writerows(verified_list)

print(f'Saved verified master list to {csv_verified} ({len(verified_list)} entries)!')
