# سجل المخاطر

| الخطر | الإشارة | التخفيف | قرار الإيقاف |
|---|---|---|---|
| بيانات غير مرخّصة | غياب license metadata | استبعاد المصدر | لا ingest |
| تسرب بين splits | تكرار exact أو near duplicate | manifest وفحص تكرار | إبطال release |
| خطأ التطبيع | تغير غير مبرر في النص | raw/normalized واختبارات | مراجعة التحويل |
| lineage ناقص | حقول run مفقودة | schema validation | invalidated |
| تحسن شكلي | تحسن compression فقط | تقييم morphology/factual منفصل | لا Go |
