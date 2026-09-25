# Changelog

## 0.1.0 - Unreleased

- تأسيس هيكل المشروع وعقود domain.
- إضافة خط بيانات حتمي للتطبيع والتقسيم وإزالة التكرار.
- إضافة سجل runs مع التحقق من اكتمال metadata.
- إضافة tokenizer baseline، مقاييس evaluation، وbigram reference baseline لدورة smoke كاملة.
- إضافة manifest export وscripts تشغيل قابلة للتسجيل.
- إضافة evaluation suite مستقلًا حسب الفئات مع اختبارات morphology/syntax أولية.
- إضافة بوابة `phase1_local_check.py` لتشغيل التحقق المحلي الكامل من أمر واحد.
- إنشاء مستودع Git محلي وإضافة Notebook وتعليمات تشغيل المرحلة الأولى على Colab.
- جعل إعادة تشغيل reference baseline آمنة عند تطابق metadata بدل اعتبارها run مكررًا فاشلًا.
- إضافة PyTorch tiny Transformer اختياري وخلية Colab لتسجيل أول neural smoke run على T4.
- إضافة source registry وLicenseGate وسياسة الطبقات الأربع وسجل تدقيق للمصادر دون تنزيل corpus خارجي.
- إضافة SourceAuditRegistry وملف الأدلة والقرارات المبدئية لكل مصدر، مع أداة تحقق تمنع التدقيق الناقص.
- جلب OpenITI metadata snapshot واختيار pilot عربي حتمي من 100 سجل دون تنزيل النصوص أو تجاوز license gate.
- إضافة تحميل checkpoint وواجهة inference وخلية Colab لتوليد نص smoke من النموذج المحفوظ.
- إضافة synthetic multi-view pilot من 35 جملة مع JSON schema، export نصي، وتحقق original-only.
- إضافة split حتمي 28/3/4 وتدريب tiny baseline بميزانية steps/batch وdev evaluation.
- إضافة OOV rate وknown-token perplexity وتسجيل commit الحقيقي في neural runs لتفسير dev metrics بدقة.
- جعل run_id يتضمن dataset/version/commit/config لتجنب حذف registry عند تغير الكود.
