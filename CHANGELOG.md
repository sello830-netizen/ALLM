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
