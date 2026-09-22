# OpenITI Arabic Metadata Pilot

## ما تم تنفيذه

تم تنزيل ملف metadata فقط من إصدار Zenodo `2025-1-9`:

- الملف: `OpenITI_metadata_2025-1-9.tsv`
- الحجم المرجعي: حوالي 12.1MB
- MD5 المنشور: `cb2226f64264efa964df9ef659d40199`
- النصوص نفسها لم تُنزّل.

الأمر المستخدم:

```text
python scripts/select_openiti_metadata.py data/raw/OpenITI_metadata_2025-1-9.tsv data/manifests/openiti-arabic-pilot.json --limit 100
```

## النتيجة

قبل الفلترة كان هناك `13,375` سجلًا عربيًا. بعد الفلترة المحافظة:

- clean primary candidates: `7,402`
- selected deterministic pilot records: `100`
- filters: `status=pri`, `uncorrected_OCR=False`, `subcorpus=ara`، وجود العنوان والمؤلف، و`1000 <= tok_length <= 500000`
- `text_downloaded: false`
- `license_gate: blocked_pending_review`

الملف الناتج content metadata فقط:

```text
data/manifests/openiti-arabic-pilot.json
```

## لماذا لم ننزل النصوص؟

OpenITI release يحتوي مصادر وحقوقًا مختلطة. توفر metadata لا يساوي موافقة على تنزيل النص أو تدريبه أو توزيع نموذج مشتق منه. لذلك لا ينتقل المصدر إلى ingest حتى تكتمل مراجعة source-level rights.

## القرار التالي

يجب مراجعة السجلات المختارة، تحديد النصوص العربية المناسبة، وتوثيق حقوق كل مصدر قبل تنزيل أي نص. لا يجوز استخدام هذا pilot كـtraining dataset حاليًا.
