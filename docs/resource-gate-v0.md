# Resource Gate v0

لا يبدأ التدريب العصبي قبل تحقق الشروط التالية:

1. وجود Python 3.10+ فعلي وليس Microsoft Store alias.
2. تثبيت إطار ML متوافق مع العتاد الفعلي.
3. وجود ذاكرة GPU كافية لحجم baseline المختار، أو قرار CPU صريح بميزانية صغيرة.
4. تثبيت نسخة البيئة في lock/manifest.
5. نجاح smoke training على batch صغير قبل أي dataset أكبر.

حالة الفحص الحالية: Python 3.12 متاح، لكن لم يُثبت ML runtime مدعومًا للتدريب العصبي والبطاقات الظاهرة Intel UHD 630 وAMD Radeon 625 بذاكرة معلنة منخفضة؛ لذلك يظل التدريب العصبي مؤجلًا.

يمكن تشغيل الفحص في Windows عبر:

```powershell
./scripts/check_resources.ps1
```
