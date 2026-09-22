# سجل تدقيق المصادر v0

الحالة الحالية لكل المصادر `proposed`؛ لم يتم تنزيل أو إدخال corpus خارجي في Git.

| المصدر | الاستخدام المقترح | الحالة | سبب عدم الاعتماد الآن |
|---|---|---|---|
| OpenITI release 2025-1-9 | research-only heritage train | proposed | الحقوق مختلطة لكل مصدر ويجب تدقيق السجلات الفردية |
| Quranic Arabic Corpus 0.4 | auxiliary morphology/syntax | proposed | شروط الاستخدام تتطلب فصل البحث عن التوزيع التجاري |
| UD Arabic NYUAD | gold evaluation | proposed | النص الأساسي غير مضمن وحقوق المصدر الأصلي منفصلة |
| Alkhalil candidate | modern MSA train | proposed | يجب تثبيت الترخيص وسلسلة provenance قبل ingest |

## قرار v0

نبدأ بالـmetadata audit فقط. لا تُنزل البيانات إلا بعد تحويل المصدر إلى `approved_research` أو `approved_redistributable` وتسجيل رابط الإصدار وhash وسياسة الاستخدام.

## مصادر المراجعة

- OpenITI RELEASE وZenodo release notes.
- OpenITI/KITAB metadata documentation.
- Quranic Arabic Corpus download/license/FAQ.
- Universal Dependencies treebank license pages.
- صفحة الجهة الناشرة للمصادر الحديثة وملف الترخيص الخاص بكل release.
